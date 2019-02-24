"""Server module containing application instance and RESTful API."""
from requests import codes
from flask import Flask, request, json

from src.server.game import Game


app = Flask(__name__)


@app.route("/connect", methods=["POST", "DELETE"])
def connect():
    """Handle new user connections and current user disconnections."""
    if request.method == 'DELETE':
        Game.game_over(won=False)
        return app.response_class(
            response=json.dumps({"message": "OK"}),
            status=codes.ok,
            mimetype='application/json'
        )
    name = request.json.get("name")
    player_added, status_code = Game.new_player(name)
    if player_added:
        response_data = json.dumps({
            "message": "OK",
            "board": Game.board,
            "turn": Game.turn,
        })
    else:
        response_data = json.dumps({
            "message": "Forbidden, no new players allowed."
        })
    response = app.response_class(
        response=response_data,
        status=status_code,
        mimetype='application/json'
    )
    return response


@app.route("/state", methods=["GET"])
def state():
    """Return the current state of the game."""
    game_state = {
        "turn": Game.turn,
        "board": Game.board,
        "game_status": Game.status
    }
    return app.response_class(
        response=json.dumps(game_state),
        status=codes.ok,
        mimetype='application/json'
    )


@app.route("/move", methods=["PATCH"])
def move():
    """Apply client move if valid and check if it's a winning move."""
    column = request.json["column"]
    name = request.json["name"]
    disc = Game.get_player_disc_colour(name)
    coordinates = Game.make_move(column, disc)
    if coordinates is None:
        message = f"Bad request, column full."
        status_code = codes.bad_request
    elif Game.has_won(disc, coordinates):
        message = Game.WON
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
