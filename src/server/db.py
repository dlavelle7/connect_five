"""Module for handling DB connection and data serialization/deserialization."""
import os
import json
import redis
import boto3

from botocore.exceptions import ClientError


class DB:
    """Base class for APIs to whatever underlying DB is used."""

    _connection = None
    DB_HOST = 'db'  # 'db' is the hostname of the db conainer

    def __init__(self, db_name):
        self.name = db_name
        self.connection = self.get_connection()

    @classmethod
    def get_connection(cls):
        """Singleton pattern to ensure only one db connection opened."""
        if DB._connection is None:
            DB._connection = cls._get_connection()
        return DB._connection

    def setup_db(self):
        """Prior to running app, set up any DB dependencies required."""
        pass

    @classmethod
    def _get_connection(cls):
        """Make the db connection for the specific underlying db."""
        raise NotImplementedError()

    def get_game(self, game_id):
        """Return the game of the given game id."""
        raise NotImplementedError()

    def save_game(self, game_id, game):
        """Persist the given game object using the given game id."""
        raise NotImplementedError()

    def scan_games(self, *args):
        """Traverse through all the games in the database."""
        raise NotImplementedError()

    def begin_transaction(self, game_id):
        """Begin transaction while checking for available games to join."""
        raise NotImplementedError()

    def get_game_transaction(self, *args):
        """Return game object from transaction."""
        raise NotImplementedError()

    def save_game_transaction(self, *args):
        """Commit transaction."""
        raise NotImplementedError()


class RedisDB(DB):

    DB_PORT = 6379
    DB_NUMBER = 0

    @classmethod
    def _get_connection(cls):
        return redis.StrictRedis(
            host=cls.DB_HOST, port=cls.DB_PORT, db=cls.DB_NUMBER,
            charset="utf-8", decode_responses=True)

    def get_game(self, game_id):
        return json.loads(self.connection.get(game_id))

    def get_game_transaction(self, pipeline, game_id):
        return json.loads(pipeline.get(game_id))

    def save_game(self, game_id, game):
        self.connection.set(game_id, json.dumps(game))

    def save_game_transaction(self, pipeline, game_id, game):
        """Save game within a transaction.

        Use Redis transaction with WATCH on game key to avoid race conditions.
        Return whether or not the transaction executed successfully.
        """
        pipeline.multi()
        pipeline.set(game_id, json.dumps(game))
        try:
            pipeline.execute()
        except redis.WatchError:
            print("A watched key has changed, abort transaction.")
            return False
        return True

    def scan_games(self, *args):
        for game_id in self.connection.scan_iter():
            yield game_id

    def begin_transaction(self, game_id):
        """WATCH game_id for changes by other clients, while checking it."""
        pipeline = self.connection.pipeline()
        pipeline.watch(game_id)
        return pipeline


class DynamoDB(DB):

    DB_PORT = 8000
    DB_TABLE = "Game"
    LAST_EVALUATED_KEY = "LastEvaluatedKey"

    @classmethod
    def _get_connection(cls):
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url=f"http://{cls.DB_HOST}:{cls.DB_PORT}")
        return dynamodb

    def setup_db(self):
        """Create the Game table in dynamodb."""
        self.create_game_table()

    def create_game_table(self):
        """Create the Game table if required."""
        tables = self.connection.meta.client.list_tables()["TableNames"]
        if self.DB_TABLE in tables:
            return
        # Create the table schema and define the primary key
        table = self.connection.create_table(
            TableName=self.DB_TABLE,
            KeySchema=[
                {
                    "AttributeName": "game_id",
                    "KeyType": "HASH",
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "game_id",
                    "AttributeType": "S",
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 100,  # throttle rate (requests per sec)
                'WriteCapacityUnits': 100,
            },
        )
        # create_table is async, wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(
            TableName=self.DB_TABLE)

    def get_game_table(self):
        return self.connection.Table(self.DB_TABLE)

    def get_game(self, game_id):
        table = self.get_game_table()
        response = table.get_item(
            Key={
                "game_id": game_id,
            }
        )
        game = response["Item"]
        return game

    def save_game(self, game_id, game):
        table = self.get_game_table()
        table.put_item(
            Item=game,
        )

    def scan_games(self, status_key, status_value, player_key, player_value):
        """Traverse through all the open games in the database."""
        filter_exp = (
            f"{status_key} = :status AND NOT contains ({player_key}, :name)"
        )
        filter_exp_attr_values = {
            ":status": status_value,
            ":name": player_value,
        }
        response = self.connection.meta.client.scan(
            TableName=self.DB_TABLE,
            FilterExpression=filter_exp,
            ExpressionAttributeValues=filter_exp_attr_values,
        )
        games = response["Items"]
        for game in games:
            yield game

        # If the scan results are greater than 1mb, dynamo will paginate
        while self.LAST_EVALUATED_KEY in response:
            table = self.get_game_table()
            response = table.scan(
                ExclusiveStartKey=response[self.LAST_EVALUATED_KEY])
            games = response["Items"]
            for game in games:
                yield game

    def save_game_transaction(self, game, status_key, status_value):
        """Save game in a dynamodb transaction.

        Use conditional check on game status and return whether or
        not transaction was successful.
        """
        try:
            self.connection.meta.client.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'Item': game,
                            'TableName': self.DB_TABLE,
                            'ConditionExpression': f'{status_key} = :status',
                            'ExpressionAttributeValues': {
                                ":status": status_value,
                            }
                        }
                    },
                ]
            )
        except ClientError:
            print("Abort transaction, game is no longer available.")
            return False
        return True


DB_OPTIONS = {
    "redis": RedisDB,
    "dynamodb": DynamoDB,
}


def get_db():
    db_name = os.environ.get("CONNECT_5_DB_TYPE", "redis")
    return DB_OPTIONS[db_name](db_name)


def setup_db():
    db = get_db()
    db.setup_db()
