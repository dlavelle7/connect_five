from requests import codes
from flask import Flask, request, json, jsonify

from src.server.game import Game


app = Flask(__name__)

WIN_RESPONSE = "Win"


@app.route("/connect", methods=["POST", "DELETE"])
def connect():
    name = request.json.get("name")
    if request.method == 'DELETE':
        # TODO: Game over to be words ("won", "disconnected")
        Game.game_over()
        return "OK"
    player_added, status_code = Game.new_player(name)
    if player_added:
        response = json.dumps({
            "message": "OK",
            "board": Game.board,
            "turn": Game.turn,
        })
    else:
        response = json.dumps({
            "message": "Forbidden, no new players allowed."
        })
    response = app.response_class(
        response=response,
        status=status_code,
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
        message = f"Bad request, column full."
        status_code = codes.bad_request
    elif Game.has_won(disc, coordinates):
        message = WIN_RESPONSE
        status_code = codes.ok
        Game.game_over()
    else:
        message = "OK"
        status_code = codes.ok
        Game.toggle_turn(name)
    response_data = {"message": message, "board": Game.board}
    return app.response_class(
        response=json.dumps(response_data),
        status=status_code,
        mimetype='application/json'
    )
