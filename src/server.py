from flask import Flask, request, json, jsonify

app = Flask(__name__)


# TODO: Make players & turn test/set Thread safe with a RLock
class Game(object):
    # TODO: Put turn, board, players into a dict (atomic)
    turn = None
    board = None
    players = []
    EMPTY = "-"
    Xs = "x"
    Os = "o"
    player_discs = (Xs, Os)

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

    @classmethod
    def make_move(cls, move, name):
        """Make move on board and return position of move."""
        column = int(move) - 1
        # Check if this row is already full
        if cls.board[column][0] != cls.EMPTY:
            return None
        # Drop disc
        for idx, cell in enumerate(cls.board[column]):
            if cell != cls.EMPTY:
                position = idx - 1
                break
        else:
            position = idx
        disc = cls.get_player_disc_colour(name)
        cls.board[column][position] = disc
        cls.toggle_turn(name)
        return position

    @classmethod
    def get_player_disc_colour(cls, name):
        """Return the player's disc colour (Player 1 is always 'X')."""
        return cls.player_discs[cls.players.index(name)]

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


# TODO: A delete method to end game
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
    return jsonify({"turn": Game.turn, "board": Game.board})


@app.route("/move", methods=["PATCH"])
def move():
    # TODO: Column may be full?
    column = request.json.get("column")
    import ipdb; ipdb.set_trace();  # XXX Breakpoint
    name = request.json.get("name")
    Game.make_move(column, name)
    return "OK"
