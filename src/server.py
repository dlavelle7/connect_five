from flask import Flask, request, jsonify

app = Flask(__name__)


# TODO: Do i need a lock here?
class Game(object):
    state = None
    players = []

    @classmethod
    def new_player(cls, name):
        if len(cls.players) <= 2:
            cls.players.append(name)


# TODO: A delete method to end game
@app.route("/connect", methods=["POST"])
def join():
    name = request.json.get("name")
    Game.new_player(name)
    return jsonify(Game.players)
