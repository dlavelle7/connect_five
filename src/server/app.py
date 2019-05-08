"""Server module containing application instance and RESTful API."""
from requests import codes
from flask import Flask, request, json

from src.server.game import Game


app = Flask(__name__)


@app.route("/game", methods=["POST"])
def connect():
    """Find an available game for the new user and return that games game id"""
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
    # TODO: This should be a patch with {"game_status": "disconnected"}
    game = Game(game_id)
    game.load_game()
    game.game_over(won=False)
    return app.response_class(
        response=json.dumps({"message": "OK"}),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["GET"])
def state(game_id):
    """Return the current state of the game."""
    game = Game(game_id)
    game.load_game()
    return app.response_class(
        response=json.dumps(game.game),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["PATCH"])
def move(game_id):
    """Apply client move if valid and check if it's a winning move."""
    column = request.json["column"]
    name = request.json["name"]
    game = Game(game_id)
    game.load_game()
    move_result = game.move(name, column)

    if move_result is None:
        message = "Bad request, column full."
        status_code = codes.bad_request
    elif move_result is True:
        message = Game.WON
        status_code = codes.ok
    else:
        message = "OK"
        status_code = codes.ok

    response_data = {"message": message}
    response_data.update(game.game)
    return app.response_class(
        response=json.dumps(response_data),
        status=status_code,
        content_type='application/json'
    )
