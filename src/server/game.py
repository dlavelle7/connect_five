"""Server module for holding game state and business logic."""
import threading

from requests import codes

LOCK = threading.RLock()


class Game:
    """Class to hold state of application and business logic."""

    # Game state
    status = None
    turn = None
    board = []
    players = []

    EMPTY = "-"
    Xs = "x"
    Os = "o"
    player_discs = (Xs, Os)
    PLAYING = "playing"
    WON = "won"
    DISCONNECTED = "disconnected"

    @classmethod
    def new_player(cls, name):
        """Add new player if possible.

        Return whether or not player was added and corresponding
        status code for response.
        """
        with LOCK:
            if len(cls.players) < 2:
                if name in cls.players:
                    return False, codes.conflict
                cls.players.append(name)
                if len(cls.players) == 1:
                    cls.start_new_game()
                if cls.turn is None:
                    cls.turn = name
            else:
                return False, codes.forbidden
            return True, codes.created

    @classmethod
    def start_new_game(cls):
        """Create new board and set game state to 'playing'."""
        cls.board = [[cls.EMPTY for i in range(6)] for j in range(9)]
        cls.status = cls.PLAYING

    @classmethod
    def make_move(cls, move, disc):
        """Make move on board and return coordinates of move."""
        column = int(move) - 1
        # Check if this row is already full
        if cls.board[column][0] != cls.EMPTY:
            return None
        # Drop disc
        for idx, cell in enumerate(cls.board[column]):
            if cell != cls.EMPTY:
                row = idx - 1
                break
        else:
            row = idx
        cls.board[column][row] = disc
        return (column, row)

    @classmethod
    def get_player_disc_colour(cls, name):
        """Return the player's disc colour (Player 1 is always 'X')."""
        return cls.player_discs[cls.players.index(name)]

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
                if cls.board[column][row_idx] != disc:
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
                if cls.board[column_idx][row] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break

        if count == 5:
            return True

        # Count matching discs to the left (can only go left to index 0)
        next_lhs_col = column - 1
        to_lhs = next_lhs_col - 4
        for column_idx in range(next_lhs_col, to_lhs, -1):
            if column_idx < 0:
                break
            if cls.board[column_idx][row] == disc:
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
                if cls.board[column_idx][row_idx] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
            column_idx += 1
            row_idx += 1

        if count == 5:
            return True

        # Count matching up and to the left
        column_idx = column - 1
        row_idx = row - 1
        for _ in range(0, 4):
            if column_idx < 0 or row_idx < 0:
                break
            if cls.board[column_idx][row_idx] == disc:
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
                if cls.board[column_idx][row_idx] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break
            column_idx += 1
            row_idx -= 1

        if count == 5:
            return True

        # Count matching discs down and to the left
        column_idx = column - 1
        row_idx = row + 1
        for _ in range(0, 4):
            if column_idx < 0:
                break
            try:
                if cls.board[column_idx][row_idx] == disc:
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
        if just_moved == cls.players[0]:
            try:
                cls.turn = cls.players[1]
            except IndexError:
                # other player may not have joined yet
                cls.turn = None
        else:
            cls.turn = cls.players[0]

    @classmethod
    def game_over(cls, won=True):
        """Set state to a game over state (player won / player disconnected)"""
        cls.status = cls.WON if won is True else cls.DISCONNECTED
