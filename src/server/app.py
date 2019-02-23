from requests import codes
from flask import Flask, request, json, jsonify

from src.server.game import Game


app = Flask(__name__)

WIN_RESPONSE = "Win"

# TODO: A delete method to end game and reset game state
@app.route("/connect", methods=["POST"])
def connect():
    name = request.json.get("name")
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
        return app.response_class(
            response=json.dumps({"message": message}),
            status=codes.bad_request,
            mimetype='application/json'
        )
    if Game.has_won(disc, coordinates):
        message = WIN_RESPONSE
        Game.game_over()
    else:
        message = "OK"
        Game.toggle_turn(name)
    # TODO: Show user their last move (also for winning move)
    return app.response_class(
        response=json.dumps({"message": message}),
        status=codes.ok,
        mimetype='application/json'
    )
