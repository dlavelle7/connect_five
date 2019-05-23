from redis import WatchError

from unittest import TestCase
from unittest.mock import Mock

from src.server.db import RedisDB


class TestRedisDB(TestCase):

    def test_save_game_transaction_successful(self):
        """Transaction executed successfully, return True."""
        mock_pipeline = Mock()
        self.assertTrue(
            RedisDB.save_game_transaction(mock_pipeline, "1", {"turn": "me"}))
        mock_pipeline.multi.assert_called_once_with()
        mock_pipeline.set.assert_called_once_with("1", '{"turn": "me"}')
        mock_pipeline.execute.assert_called_once_with()

    def test_save_game_transaction_key_changed_while_watching(self):
        """A watched key was changed during the tranaction, return False"""
        mock_pipeline = Mock(execute=Mock(side_effect=WatchError))
        self.assertFalse(
            RedisDB.save_game_transaction(mock_pipeline, "1", {"turn": "me"}))
        mock_pipeline.multi.assert_called_once_with()
        mock_pipeline.set.assert_called_once_with("1", '{"turn": "me"}')
        mock_pipeline.execute.assert_called_once_with()
