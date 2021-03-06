"""Server module containing application instance and RESTful API."""
import json

from flask import request
from flask_api import FlaskAPI, status

from src.server.game import Game
from src.server.game_finder import get_game_finder
from src.server.utils import DecimalEncoder


app = FlaskAPI(__name__)

RESPONSE_HEADERS = {"Content-Type": "application/json"}


@app.route("/game", methods=["POST"])
def create_game():
    """Create a new game for the new player."""
    name = request.json.get("name")
    max_players = request.json.get("max_players")
    game_id = Game.start_new_game(name, max_players)
    return {"game_id": game_id}, status.HTTP_201_CREATED, RESPONSE_HEADERS


@app.route("/game", methods=["PATCH"])
def update_game_new_player():
    """Update an available game by adding the new player to it."""
    name = request.json.get("name")
    game_finder = get_game_finder()
    game_id = game_finder.join_game(name)
    if game_id is None:
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_200_OK
    return {"game_id": game_id}, status_code, RESPONSE_HEADERS


@app.route("/game/<game_id>", methods=["GET"])
def get_game(game_id):
    """Get the specified game."""
    game = Game(game_id)
    game.load_game()
    response_body = json.dumps(game.game, cls=DecimalEncoder)
    return response_body, status.HTTP_200_OK, RESPONSE_HEADERS


@app.route("/game/<game_id>", methods=["PATCH"])
def update_game(game_id):
    """Update the specified game (make a move or end a game)."""
    game = Game(game_id)
    game.load_game()
    if request.json.get("game_status") == Game.DISCONNECTED:
        game.game_over(won=False)
        return {"message": "OK"}, status.HTTP_200_OK, RESPONSE_HEADERS

    column = request.json["column"]
    name = request.json["name"]
    move_result = game.move(name, column)

    if move_result is None:
        message = "Bad request, column full."
        status_code = status.HTTP_400_BAD_REQUEST
    elif move_result is True:
        message = Game.WON
        status_code = status.HTTP_200_OK
    else:
        message = "OK"
        status_code = status.HTTP_200_OK

    response_data = {"message": message}
    response_data.update(game.game)
    response_body = json.dumps(response_data, cls=DecimalEncoder)
    return response_body, status_code, RESPONSE_HEADERS
