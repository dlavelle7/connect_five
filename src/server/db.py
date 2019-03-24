"""Module for handling DB connection and data serialization/deserialization."""
import redis
import json


class DB:

    _connection = None

    def __init__(self):
        self.connection = self.get_connection()

    @classmethod
    def get_connection(cls):
        if DB._connection is None:
            # 'redis' is the hostname of the redis conainer
            DB._connection = redis.StrictRedis(
                host='redis', port=6379, db=0,
                charset="utf-8", decode_responses=True)
        return DB._connection

    def get_games(self):
        games = {}
        # TODO: use scan_iter() instead (generator)
        for game_id in self.connection.keys():
            games[game_id] = self.get_game(game_id)
        return games

    def get_game(self, game_id):
        return json.loads(self.connection.get(game_id))

    def save_game(self, game_id, game):
        self.connection.set(game_id, json.dumps(game))

    def save_game_transaction(self, pipeline, game_id, game):
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
