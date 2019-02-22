from flask import Flask, request, json, jsonify

# TODO: Flask-API???
app = Flask(__name__)

WIN_RESPONSE = "Win"


# TODO: Move game to own module (src.server.game.py)
# TODO: Make players & turn test/set Thread safe with a RLock
class Game(object):

    # TODO: Put game_status, turn, board, players into a dict (atomic)
    status = None
    turn = None
    board = None
    players = []

    EMPTY = "-"
    Xs = "x"
    Os = "o"
    player_discs = (Xs, Os)
    PLAY = 1
    OVER = 0

    @classmethod
    def new_player(cls, name):
        if len(cls.players) < 2:
            cls.players.append(name)
            if len(cls.players) == 1:
                cls.start_new_game()
            if cls.turn is None:
                cls.turn = name
        else:
            return False
        return True

    @classmethod
    def start_new_game(cls):
        cls.board = [[cls.EMPTY for i in range(6)] for j in range(9)]
        cls.status = cls.PLAY

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
                         cls.check_diagonal]
        for check_method in check_methods:
            if check_method(disc, *coordinates) is True:
                return True
        return False

    @classmethod
    def check_vertical(cls, disc, column, row):
        """Check from coordinates down"""
        next_idx = row + 1
        for idx in range(next_idx, next_idx + 4):
            try:
                if cls.board[column][idx] != disc:
                    return False
            except IndexError:
                return False
        return True

    @classmethod
    def check_horizontal(cls, disc, column, row):
        """Check from coordinates horizontally (left and right)"""
        count = 1
        # Count matching discs to the right
        next_rhs_col_idx = column + 1
        for column_idx in range(next_rhs_col_idx, next_rhs_col_idx + 4):
            try:
                if cls.board[column_idx][row] == disc:
                    count += 1
                else:
                    break
            except IndexError:
                break

        if count == 5:
            return True

        # Count matching discs to the left
        next_lhs_col_idx = column - 1
        for column_idx in range(next_lhs_col_idx, next_lhs_col_idx - 4, -1):
            # TODO: Replace this with max(next_lhs_col, 0)
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
    def check_diagonal(cls, disc, column, row):
        """Check from coordinates diagonally (left and right, up and down)"""
        # TODO:
        return False

    @classmethod
    def toggle_turn(cls, just_moved):
        if just_moved == cls.players[0]:
            try:
                cls.turn = cls.players[1]
            except IndexError:
                # other player may not have joined yet
                cls.turn = None
        else:
            cls.turn = cls.players[0]

    @classmethod
    def game_over(cls):
        cls.status = cls.OVER


# TODO: A delete method to end game?
@app.route("/connect", methods=["POST"])
def join():
    name = request.json.get("name")
    if Game.new_player(name):
        response = json.dumps({
            "message": "OK",
            "board": Game.board,
            "turn": Game.turn,
        })
        status = 201
    else:
        # TODO: The server should not be dictating the messages to the user
        response = json.dumps({
            "message": "This game is already full, try again later."
        })
        status = 403
    response = app.response_class(
        response=response,
        status=status,
        mimetype='application/json'
    )
    return response


@app.route("/state", methods=["GET"])
def state():
    state = {
        "turn": Game.turn,
        "board": Game.board,
        "game_status": Game.status
    }
    return jsonify(state)


@app.route("/move", methods=["PATCH"])
def move():
    column = request.json.get("column")
    name = request.json.get("name")
    disc = Game.get_player_disc_colour(name)
    coordinates = Game.make_move(column, disc)
    if coordinates is None:
        # TODO: The server should not be dictating the messages to the user
        message = f"Column {column} is full, please try another: "
        return app.response_class(
            response=json.dumps({"message": message}),
            status=400,
            mimetype='application/json'
        )
    if Game.has_won(disc, coordinates):
        message = WIN_RESPONSE
        Game.game_over()
    else:
        message = "OK"
        Game.toggle_turn(name)
    return app.response_class(
        response=json.dumps({"message": message}),
        status=200,
        mimetype='application/json'
    )
