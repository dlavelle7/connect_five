from flask import Flask, request, json, jsonify

app = Flask(__name__)


# TODO: Do i need a lock here?
class Game(object):
    turn = None
    players = []
    EMPTY = ""
    X = "x"
    O = "o"

    @classmethod
    def new_player(cls, name):
        if len(cls.players) < 2:
            cls.players.append(name)
            if len(cls.players) == 1:
                cls.start_new_game()
        else:
            return False
        return True

    @classmethod
    def start_new_game(cls):
        cls.board = [[cls.EMPTY for i in range(6)] for j in range(9)]
        cls.turn = cls.players[0]


    @classmethod
    def make_move(cls, column, name):
        move = int(column) - 1
        # TODO: Do move in board
        cls.toggle_turn(name)

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
    name = request.json.get("name")
    Game.make_move(column, name)
    return "OK"
