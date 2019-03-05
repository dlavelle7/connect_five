"""Server module for holding game state and business logic."""
import uuid
import threading

LOCK = threading.RLock()


class Game:
    """Class to hold state of application and business logic."""

    # Games state
    state = {}

    EMPTY = "-"
    Xs = "x"
    Os = "o"
    player_discs = (Xs, Os)
    PLAYING = "playing"
    WON = "won"
    DISCONNECTED = "disconnected"

    @classmethod
    def new_player(cls, name):
        """Add new player to a game.

        If there is an open space in an existing game, add the player to that,
        otherwise create a new game for that user.

        Return the game_id of the game that the user joined.
        """
        with LOCK:
            # Check for a space in an existing game for our new player to join
            for game_id, existing_game in cls.state.items():
                if len(existing_game["players"]) < 2 and \
                        name not in existing_game["players"]:
                    self.join_existing_game(name, game_id)
                    break
            else:
                game_id = self.start_new_game(name)
            return game_id

    @classmethod
    def join_existing_game(cls, name, game_id):
        cls.state[game_id]["players"].append(name)
        if cls.state[game_id]["turn"] is None:
            cls.state[game_id]["turn"] = name

    @classmethod
    def start_new_game(cls, name):
        """Create a new game id and new game state. Return new game ID."""
        new_game = {
            "board": [[cls.EMPTY for i in range(6)] for j in range(9)],
            "game_status": cls.PLAYING,
            "players": [name],
            "turn": name,
        }
        new_game_id = uuid.uuid4()
        cls.state[new_game_id] = new_game
        return new_game_id

    @classmethod
    def make_move(cls, move, disc):
        """Make move on board and return coordinates of move."""
        column = move - 1
        # Check if this row is already full
        if cls.state["board"][column][0] != cls.EMPTY:
            return None
        # Drop disc
        for idx, cell in enumerate(cls.state["board"][column]):
            if cell != cls.EMPTY:
                row = idx - 1
                break
        else:
            row = idx
        cls.state["board"][column][row] = disc
        return (column, row)

    @classmethod
    def get_player_disc_colour(cls, name):
        """Return the player's disc colour (Player 1 is always 'X')."""
        return cls.player_discs[cls.state["players"].index(name)]

    @classmethod
    def has_won(cls, disc, coordinates):
        """Returns True if move wins, otherwise returns False"""
        check_methods = [cls.check_vertical, cls.check_horizontal,
                         cls.check_diagonal_1, cls.check_diagonal_2]
        for check_method in check_methods:
            if check_method(disc, *coordinates) is True:
                return True
        return False

    @classmethod
    def check_vertical(cls, disc, column, row):
        """Check from coordinates down"""
        next_row = row + 1
        for row_idx in range(next_row, next_row + 4):
            try:
                if cls.state["board"][column][row_idx] != disc:
                    return False
            except IndexError:
                return False
        return True

    @classmethod
    def check_horizontal(cls, disc, column, row):
        """Check from coordinates horizontally (left and right)"""
        count = 1
        # Count matching discs to the right
        next_rhs_col = column + 1
        for column_idx in range(next_rhs_col, next_rhs_col + 4):
            try:
                if cls.state["board"][column_idx][row] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
        else:
            return True

        # Count matching discs to the left (can only go left to index 0)
        next_lhs_col = column - 1
        to_lhs = next_lhs_col - 4
        for column_idx in range(next_lhs_col, to_lhs, -1):
            if column_idx < 0:
                break
            if cls.state["board"][column_idx][row] == disc:
                count += 1
                if count == 5:
                    return True
            else:
                break
        return False

    @classmethod
    def check_diagonal_1(cls, disc, column, row):
        """Check diagonal in '\' direction."""
        count = 1
        # Count matching down and to the right
        column_idx = column + 1
        row_idx = row + 1
        for _ in range(0, 4):
            try:
                if cls.state["board"][column_idx][row_idx] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
            column_idx += 1
            row_idx += 1
        else:
            return True

        # Count matching up and to the left
        column_idx = column - 1
        row_idx = row - 1
        for _ in range(0, 4):
            if column_idx < 0 or row_idx < 0:
                break
            if cls.state["board"][column_idx][row_idx] == disc:
                count += 1
                if count == 5:
                    return True
            else:
                break
            column_idx -= 1
            row_idx -= 1

        return False

    @classmethod
    def check_diagonal_2(cls, disc, column, row):
        """Check diagonal in '/' direction."""
        # TODO: Diagonal methods are similar, see if you can refactor into one
        count = 1
        # Count matching discs up and to the right
        column_idx = column + 1
        row_idx = row - 1
        for _ in range(0, 4):
            if row_idx < 0:
                break
            try:
                if cls.state["board"][column_idx][row_idx] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
            column_idx += 1
            row_idx -= 1
        else:
            return True

        # Count matching discs down and to the left
        column_idx = column - 1
        row_idx = row + 1
        for _ in range(0, 4):
            if column_idx < 0:
                break
            try:
                if cls.state["board"][column_idx][row_idx] == disc:
                    count += 1
                    if count == 5:
                        return True
                else:
                    break
            except IndexError:
                break
            column_idx -= 1
            row_idx += 1

        return False

    @classmethod
    def toggle_turn(cls, just_moved):
        """Swap the 'turn' from player who has just moved."""
        if just_moved == cls.state["players"][0]:
            try:
                cls.state["turn"] = cls.state["players"][1]
            except IndexError:
                # other player may not have joined yet
                cls.state["turn"] = None
        else:
            cls.state["turn"] = cls.state["players"][0]

    @classmethod
    def game_over(cls, won=True):
        """Set state to a game over state (player won / player disconnected)"""
        cls.state["game_status"] = cls.WON if won is True else cls.DISCONNECTED
