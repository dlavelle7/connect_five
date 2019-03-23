"""Server module containing application instance and RESTful API."""
import redis

from requests import codes
from flask import Flask, request, json

from src.server.game import Game


app = Flask(__name__)

# 'redis' is the hostname of the redis conainer
db = redis.Redis(host='redis', port=6379)


@app.route("/game", methods=["POST"])
def connect():
    """Handle new user connections and current user disconnections."""
    name = request.json.get("name")
    game_id = Game.new_player(name)
    response = app.response_class(
        response=json.dumps({"game_id": game_id}),
        status=codes.created,
        content_type='application/json'
    )
    return response


@app.route("/game/<game_id>", methods=["DELETE"])
def disconnect(game_id):
    Game.game_over(game_id, won=False)
    return app.response_class(
        response=json.dumps({"message": "OK"}),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["GET"])
def state(game_id):
    """Return the current state of the game."""
    return app.response_class(
        response=json.dumps(Game.state[game_id]),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["PATCH"])
def move(game_id):
    """Apply client move if valid and check if it's a winning move."""
    column = request.json["column"]
    name = request.json["name"]
    disc = Game.get_player_disc_colour(game_id, name)
    coordinates = Game.make_move(game_id, column, disc)
    if coordinates is None:
        message = f"Bad request, column full."
        status_code = codes.bad_request
    elif Game.has_won(game_id, disc, coordinates):
        message = Game.WON
        status_code = codes.ok
        Game.game_over(game_id)
    else:
        message = "OK"
        status_code = codes.ok
        Game.toggle_turn(game_id, name)
    response_data = {"message": message}
    response_data.update(Game.state[game_id])
    return app.response_class(
        response=json.dumps(response_data),
        status=status_code,
        content_type='application/json'
    )
