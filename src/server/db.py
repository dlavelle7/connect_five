"""Module for handling DB connection and data serialization/deserialization."""
import redis
import json


class DB:

    _connection = None
    DB_HOST = 'redis'  # 'redis' is the hostname of the redis conainer
    DB_PORT = 6379
    DB_NUMBER = 0

    def __init__(self):
        self.connection = self.get_connection()

    @classmethod
    def get_connection(cls):
        if DB._connection is None:
            DB._connection = redis.StrictRedis(
                host=cls.DB_HOST, port=cls.DB_PORT, db=cls.DB_NUMBER,
                charset="utf-8", decode_responses=True)
        return DB._connection

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
