from flask import Flask, request, jsonify, json

app = Flask(__name__)


# TODO: Do i need a lock here?
class Game(object):
    state = None
    players = []
    EMPTY = ""
    X = "x"
    O = "o"

    @classmethod
    def new_player(cls, name):
        no_of_players = len(cls.players)
        if no_of_players == 0:
            cls.start_new_game()
        if no_of_players < 2:
            cls.players.append(name)
        else:
            return False
        return True

    @classmethod
    def start_new_game(cls):
        cls.board = [[cls.EMPTY for i in range(6)] for j in range(9)]


# TODO: A delete method to end game
@app.route("/connect", methods=["POST"])
def join():
    name = request.json.get("name")
    if Game.new_player(name):
        response = json.dumps({
            "board": Game.board,
            "players": Game.players,
        })
        status = 201
    else:
        response = json.dumps({
            "error":"This game is already full, try again later."
        })
        status = 403
    response = app.response_class(
        response=response,
        status=status,
        mimetype='application/json'
    )
    return response
