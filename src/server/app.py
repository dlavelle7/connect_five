"""Server module containing application instance and RESTful API."""
from requests import codes
from flask import Flask, request, json

from src.server.game import Game, db


app = Flask(__name__)


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
    game = db.get_game(game_id)
    Game.game_over(game, won=False)
    db.save_game(game_id, game)
    return app.response_class(
        response=json.dumps({"message": "OK"}),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["GET"])
def state(game_id):
    """Return the current state of the game."""
    return app.response_class(
        response=json.dumps(db.get_game(game_id)),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["PATCH"])
def move(game_id):
    """Apply client move if valid and check if it's a winning move."""
    column = request.json["column"]
    name = request.json["name"]
    game = db.get_game(game_id)
    disc = Game.get_player_disc_colour(game, name)
    coordinates = Game.make_move(game, column, disc)
    if coordinates is None:
        message = f"Bad request, column full."
        status_code = codes.bad_request
    elif Game.has_won(game, disc, coordinates):
        message = Game.WON
        status_code = codes.ok
        Game.game_over(game)
    else:
        message = "OK"
        status_code = codes.ok
        Game.toggle_turn(game, name)
    db.save_game(game_id, game)
    response_data = {"message": message}
    response_data.update(game)
    return app.response_class(
        response=json.dumps(response_data),
        status=status_code,
        content_type='application/json'
    )
