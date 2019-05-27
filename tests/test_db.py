from redis import WatchError
from unittest import TestCase
from unittest.mock import Mock, patch

from src.server.db import DB, RedisDB, get_db


class TestDB(TestCase):

    def setUp(self):
        # reset db connection for each test so singleton pattern can be tested
        DB._connection = None


@patch("src.server.db.RedisDB._get_connection")
class TestRedisDB(TestDB):

    def test_save_game_transaction_successful(self, mock_get_redis_connection):
        """Transaction executed successfully, return True."""
        mock_pipeline = Mock()
        self.assertTrue(
            RedisDB("redis").save_game_transaction(
                mock_pipeline, "1", {"turn": "me"}))
        mock_pipeline.multi.assert_called_once_with()
        mock_pipeline.set.assert_called_once_with("1", '{"turn": "me"}')
        mock_pipeline.execute.assert_called_once_with()

    def test_save_game_transaction_key_changed_while_watching(
            self, mock_get_redis_connection):
        """A watched key was changed during the tranaction, return False"""
        mock_pipeline = Mock(execute=Mock(side_effect=WatchError))
        self.assertFalse(
            RedisDB("redis").save_game_transaction(
                mock_pipeline, "1", {"turn": "me"}))
        mock_pipeline.multi.assert_called_once_with()
        mock_pipeline.set.assert_called_once_with("1", '{"turn": "me"}')
        mock_pipeline.execute.assert_called_once_with()

    def test_get_db_singleton(self, mock_get_redis_connection):
        """Ensure that only one db connection is created with multiple calls"""
        redis1 = get_db()
        redis2 = get_db()
        self.assertEqual(id(redis1.connection), id(redis2.connection))
        self.assertEqual(1, mock_get_redis_connection.call_count)


@patch.dict("src.server.db.os.environ", {"CONNECT_5_DB_TYPE": "dynamodb"})
class TestDynamoDB(TestDB):

    @patch("src.server.db.DynamoDB._get_connection")
    def test_get_db_singleton(self, mock_get_ddb_connection):
        """Ensure that only one db connection is created with multiple calls"""
        ddb1 = get_db()
        ddb2 = get_db()
        self.assertEqual(id(ddb1.connection), id(ddb2.connection))
        self.assertEqual(1, mock_get_ddb_connection.call_count)

    @patch("src.server.db.DynamoDB._get_connection")
    def test_create_table_table_exists(self, mock_get_connection):
        mock_connection = Mock()
        mock_connection.meta.client.list_tables.return_value = \
            {"TableNames": ["Game"]}
        mock_get_connection.return_value = mock_connection
        db = get_db()
        db.create_game_table()
        self.assertFalse(mock_connection.create_table.called)
