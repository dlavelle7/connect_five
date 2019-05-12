"""Server module containing application instance and RESTful API."""
from requests import codes
from flask import Flask, request, json

from src.server.game import Game


app = Flask(__name__)


@app.route("/game", methods=["POST"])
def create_game():
    """Create a new game for the new player."""
    name = request.json.get("name")
    max_players = int(request.json.get("max_players"))
    game_id = Game.start_new_game(name, max_players)
    return app.response_class(
        response=json.dumps({"game_id": game_id}),
        status=codes.created,
        content_type='application/json'
    )


@app.route("/game", methods=["PATCH"])
def new_player_update_game():
    """Update an available game by adding the new player to it."""
    name = request.json.get("name")
    game_id = Game.join_existing_game(name)
    status = codes.not_found if game_id is None else codes.ok
    return app.response_class(
        response=json.dumps({"game_id": game_id}),
        status=status,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["GET"])
def get_game(game_id):
    """Get the specified game."""
    game = Game(game_id)
    game.load_game()
    return app.response_class(
        response=json.dumps(game.game),
        status=codes.ok,
        content_type='application/json'
    )


@app.route("/game/<game_id>", methods=["PATCH"])
def update_game(game_id):
    """Update the specified game (make a move or end a game)."""
    game = Game(game_id)
    game.load_game()
    if request.json.get("game_status") == Game.DISCONNECTED:
        game.game_over(won=False)
        return app.response_class(
            response=json.dumps({"message": "OK"}),
            status=codes.ok,
            content_type='application/json'
        )

    column = request.json["column"]
    name = request.json["name"]
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
