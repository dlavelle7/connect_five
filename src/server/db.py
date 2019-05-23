"""Module for handling DB connection and data serialization/deserialization."""
import os
import redis
import json


class DB:
    """Base class for APIs to whatever underlying DB is used."""

    def get_game(self, game_id):
        """Return the game of the given game id."""
        raise NotImplementedError()

    def save_game(self, game_id, game):
        """Persist the given game object using the given game id."""
        raise NotImplementedError()

    def scan_games(self):
        """Traverse through all the games in the database."""
        raise NotImplementedError()


class RedisDB(DB):

    _connection = None
    DB_HOST = 'redis'  # 'redis' is the hostname of the redis conainer
    DB_PORT = 6379
    DB_NUMBER = 0

    def __init__(self):
        self.connection = self.get_connection()

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = redis.StrictRedis(
                host=cls.DB_HOST, port=cls.DB_PORT, db=cls.DB_NUMBER,
                charset="utf-8", decode_responses=True)
        return cls._connection

    def get_game(self, game_id):
        return json.loads(self.connection.get(game_id))

    @staticmethod
    def get_game_transaction(pipeline, game_id):
        return json.loads(pipeline.get(game_id))

    def save_game(self, game_id, game):
        self.connection.set(game_id, json.dumps(game))

    @staticmethod
    def save_game_transaction(pipeline, game_id, game):
        """Save game within a transaction.

        Return whether or not the transaction executed successfully."""
        pipeline.multi()
        pipeline.set(game_id, json.dumps(game))
        try:
            pipeline.execute()
        except redis.WatchError:
            print("A watched key has changed, abort transaction.")
            return False
        return True

    def scan_games(self):
        for game_id in self.connection.scan_iter():
            yield game_id


DB_OPTIONS = {
    "redis": RedisDB,
}


def get_db():
    db_setting = os.environ.get("CONNECT_5_DB_TYPE", "redis")
    return DB_OPTIONS[db_setting]()
