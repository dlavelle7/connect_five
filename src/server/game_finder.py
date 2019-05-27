"""
Module for housing the logic to find an existing game to join, depending on the
specific DB being used.
"""
import os

from src.server.game import Game

from src.server.db import get_db

db = get_db()


class GameFinder:

    @classmethod
    def find_game(cls):
        raise NotImplementedError()


class RedisGameFinder(GameFinder):

    @classmethod
    def join_game(cls, name):
        """Use redis scan to search for an available game.

        If a game could be joined, return that game_id.
        If no open game was found, return None.
        """
        for game_id in db.scan_games():
            if cls._join_game(name, game_id):
                return game_id
        else:
            return None

    @classmethod
    def _join_game(cls, name, game_id):
        """Try to join an existing active game if there is space."""
        transaction = db.begin_transaction(game_id)
        game = db.get_game_transaction(transaction, game_id)

        if game.get("game_status") != Game.PLAYING:
            return False
        if len(game["players"]) > game["max_players"] - 1:
            return False
        if name in game["players"]:
            return False

        game["players"].append(name)
        if game["turn"] is None:
            game["turn"] = name

        # Save existing game in a transaction
        return db.save_game_transaction(transaction, game_id, game)


class DynamoGameFinder(GameFinder):

    # TODO:
    pass


GAME_FINDERS = {
    "redis": RedisGameFinder,
    "dynamodb": DynamoGameFinder,
}


def get_game_finder():
    db_name = os.environ.get("CONNECT_5_DB_TYPE", "redis")
    return GAME_FINDERS[db_name]()
