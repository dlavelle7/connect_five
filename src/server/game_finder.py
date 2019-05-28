"""
Module for housing the logic to find an existing game to join, depending on the
specific DB being used. Purpose is to keep db & game logic separate.
"""
import os

from src.server.game import Game

from src.server.db import get_db

db = get_db()


class GameFinder:

    @classmethod
    def join_game(cls):
        """
        If a game could be joined, return that game_id.
        If no open game was found, return None.
        """
        raise NotImplementedError()

    @staticmethod
    def add_player(game, name):
        """Add the player to the game and change turn / state accordingly."""
        game["players"].append(name)

        if game["turn"] is None:
            game["turn"] = name

        if len(game["players"]) == game["max_players"]:
            game["game_status"] = Game.PLAYING

        return game


class RedisGameFinder(GameFinder):

    @classmethod
    def join_game(cls, name):
        """Use redis scan to search for an available game."""
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

        if game.get("game_status") != Game.OPEN:
            return False
        if name in game["players"]:
            return False

        game = cls.add_player(game, name)

        # Save existing game in a transaction
        return db.save_game_transaction(transaction, game_id, game)


class DynamoGameFinder(GameFinder):

    @classmethod
    def join_game(cls, name):
        """Use dynamo scan with filter to search for an available game."""
        for game in db.scan_games("game_status", Game.OPEN):
            if cls._join_game(name, game):
                return game["game_id"]
        else:
            return None

    @classmethod
    def _join_game(cls, name, game):
        """Attempt to join the game within a transaction condition."""
        # TODO: Make this a scan filter expression (x not in y)
        if name in game["players"]:
            return False
        game = cls.add_player(game, name)
        return db.save_game_transaction(game)



GAME_FINDERS = {
    "redis": RedisGameFinder,
    "dynamodb": DynamoGameFinder,
}


def get_game_finder():
    db_name = os.environ.get("CONNECT_5_DB_TYPE", "redis")
    return GAME_FINDERS[db_name]()
