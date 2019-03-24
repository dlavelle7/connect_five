"""Server module for holding game state and business logic."""
import uuid

from operator import add, sub

from src.server.db import DB

db = DB()


class Game:
    """Class to hold state of application and business logic."""

    EMPTY = "-"
    Xs = "x"
    Os = "o"
    player_discs = (Xs, Os)
    PLAYING = "playing"
    WON = "won"
    DISCONNECTED = "disconnected"
    WINNING_COUNT = 5
    MAX_COUNT = WINNING_COUNT - 1
    BOARD_ROWS = 6
    BOARD_COLS = 9

    @classmethod
    def new_player(cls, name):
        """Add new player to a game.

        If there is an open space in an existing game, add the player to that,
        otherwise create a new game for that user.

        Return the game_id of the game that the user joined.
        """

        # Check for a space in an existing game for our new player to join
        for game_id, game in db.get_games().items():
            if cls.join_existing_game(name, game_id, game):
                break
        else:
            game_id, game = cls.start_new_game(name)
        return game_id

    @classmethod
    def join_existing_game(cls, name, game_id, game):
        """Try to join an existing game if there is space.

        Use Redis transaction with WATCH on game key to avoid race conditions.
        """
        # WATCH this game_id for changes by other clients, while checking it
        pipeline = db.connection.pipeline()
        pipeline.watch(game_id)
        if len(game["players"]) > 1 or name in game["players"]:
            return False

        game["players"].append(name)
        if game["turn"] is None:
            game["turn"] = name
        # Save existing game in a transaction
        return db.save_game_transaction(pipeline, game_id, game)

    @classmethod
    def start_new_game(cls, name):
        """Create a new game id and new game state. Return new game ID."""
        new_game = {
            "board": [[cls.EMPTY for i in range(cls.BOARD_ROWS)]
                      for j in range(cls.BOARD_COLS)],
            "game_status": cls.PLAYING,
            "players": [name],
            "turn": name,
        }
        new_game_id = str(uuid.uuid4())
        db.save_game(new_game_id, new_game)
        return new_game_id, new_game

    @classmethod
    def make_move(cls, game, move, disc):
        """Make move on board and return coordinates of move."""
        column = move - 1
        board = game["board"]
        # Check if this row is already full
        if board[column][0] != cls.EMPTY:
            return None
        # Drop disc
        for idx, cell in enumerate(board[column]):
            if cell != cls.EMPTY:
                row = idx - 1
                break
        else:
            row = idx
        board[column][row] = disc
        return (column, row)

    @classmethod
    def get_player_disc_colour(cls, game, name):
        """Return the player's disc colour (Player 1 is always 'X')."""
        player_number = game["players"].index(name)
        return cls.player_discs[player_number]

    @classmethod
    def has_won(cls, game, disc, coordinates):
        """Returns True if move wins, otherwise returns False"""
        board = game["board"]
        check_methods = [cls.check_vertical, cls.check_horizontal,
                         cls.check_diagonal_1, cls.check_diagonal_2]
        for check_method in check_methods:
            if check_method(board, disc, *coordinates) is True:
                return True
        return False

    @classmethod
    def check_vertical(cls, board, disc, column, row):
        """Check from coordinates down"""
        next_row = row + 1
        for row_idx in range(next_row, next_row + cls.MAX_COUNT):
            try:
                if board[column][row_idx] != disc:
                    return False
            except IndexError:
                return False
        return True

    @classmethod
    def check_horizontal(cls, board, disc, column, row):
        """Check from coordinates horizontally (left and right)"""
        count = 1
        # Count matching discs to the right
        next_rhs_col = column + 1
        for column_idx in range(next_rhs_col, next_rhs_col + cls.MAX_COUNT):
            try:
                if board[column_idx][row] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
        else:
            return True

        # Count matching discs to the left (can only go left to index 0)
        next_lhs_col = column - 1
        to_lhs = next_lhs_col - cls.MAX_COUNT
        for column_idx in range(next_lhs_col, to_lhs, -1):
            if column_idx < 0:
                break
            if board[column_idx][row] == disc:
                count += 1
                if count == cls.WINNING_COUNT:
                    return True
            else:
                break
        return False

    @classmethod
    def _check_diagonal(cls, board, disc, column, row, direction):
        operators = {
            "\\": [(add, add), (sub, sub)],
            "//": [(add, sub), (sub, add)]
        }
        count = 1

        # Count 1st direction (has to at least get to end of 1st loop)
        col_operator, row_operator = operators[direction][0]
        column_idx = col_operator(column, 1)
        row_idx = row_operator(row, 1)
        for _ in range(cls.MAX_COUNT):
            if column_idx < 0 or row_idx < 0:
                break
            try:
                if board[column_idx][row_idx] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
            column_idx = col_operator(column_idx, 1)
            row_idx = row_operator(row_idx, 1)
        else:
            return True

        # Count 2nd direction (check if won at each matched disc)
        col_operator, row_operator = operators[direction][1]
        column_idx = col_operator(column, 1)
        row_idx = row_operator(row, 1)
        for _ in range(cls.MAX_COUNT):
            if column_idx < 0 or row_idx < 0:
                break
            try:
                if board[column_idx][row_idx] == disc:
                    count += 1
                    if count == cls.WINNING_COUNT:
                        return True
                else:
                    break
            except IndexError:
                break
            column_idx = col_operator(column_idx, 1)
            row_idx = row_operator(row_idx, 1)
        return False

    @classmethod
    def check_diagonal_1(cls, board, disc, column, row):
        return cls._check_diagonal(board, disc, column, row, "\\")

    @classmethod
    def check_diagonal_2(cls, board, disc, column, row):
        return cls._check_diagonal(board, disc, column, row, "//")

    @classmethod
    def toggle_turn(cls, game, just_moved):
        """Swap the 'turn' from player who has just moved."""
        if just_moved == game["players"][0]:
            try:
                game["turn"] = game["players"][1]
            except IndexError:
                # other player may not have joined yet
                game["turn"] = None
        else:
            game["turn"] = game["players"][0]

    @classmethod
    def game_over(cls, game, won=True):
        """Set state to a game over state (player won / player disconnected)"""
        game["game_status"] = cls.WON if won is True else cls.DISCONNECTED
