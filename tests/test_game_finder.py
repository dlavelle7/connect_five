from unittest import TestCase
from unittest.mock import patch

from src.server.game_finder import RedisGameFinder


class TestRedisGameFinder(TestCase):

    @patch("src.server.game_finder.db")
    @patch("src.server.game_finder.RedisGameFinder._join_game",
           side_effect=[False, True])
    def test_join_existing_game_game_found(self, mock_join, mock_db):
        """Available game with space found, return game_id."""
        mock_db.scan_games.return_value = ["1", "2", "3"]
        self.assertEqual("2", RedisGameFinder.join_game("foo"))
        self.assertEqual(2, mock_join.call_count)

    @patch("src.server.game_finder.db")
    @patch("src.server.game_finder.RedisGameFinder._join_game",
           return_value=False)
    def test_join_existing_game_no_game_found(self, mock_join, mock_db):
        """No available game with space found, return None."""
        mock_db.connection.scan_iter.return_value = ["1", "2", "3"]
        self.assertIsNone(RedisGameFinder.join_game("foo"))

    @patch("src.server.game_finder.db")
    def test_2nd_player_joins_after_player1_has_moved(self, mock_db):
        """2nd player added, player 1 had already moved, their turn now"""
        game_id = "246"
        test_game_state = {
            "turn": None,
            "players": ["dom"],
            "game_status": "open",
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        RedisGameFinder._join_game("mary", game_id)

        _, call_game_id, call_game_state = \
            mock_db.save_game_transaction.call_args[0]

        self.assertEqual(game_id, call_game_id)
        self.assertEqual("mary", call_game_state["turn"])
        self.assertListEqual(["dom", "mary"], call_game_state["players"])

    @patch("src.server.game_finder.db")
    def test_2nd_player_joins_while_its_player1s_move(self, mock_db):
        """2nd player added, while it's player 1 move, not their turn now."""
        game_id = "246"
        test_game_state = {
            "turn": "dom",
            "players": ["dom"],
            "game_status": "open",
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        RedisGameFinder._join_game("mary", game_id)

        _, call_game_id, call_game_state = \
            mock_db.save_game_transaction.call_args[0]

        self.assertEqual(game_id, call_game_id)
        self.assertEqual("dom", call_game_state["turn"])
        self.assertListEqual(["dom", "mary"], call_game_state["players"])

    @patch("src.server.game_finder.db")
    def test_bug_2nd_player_cant_join_disconnected_game(self, mock_db):
        """2nd player added, game checked has been disconnected, can't join."""
        game_id = "888"
        test_game_state = {
            "turn": "bob",
            "players": ["bob"],
            "game_status": "disconnected",
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(RedisGameFinder._join_game("mary", game_id))

    @patch("src.server.game_finder.db")
    def test_new_player_joins_this_game_already_full(self, mock_db):
        """This existing game is full, return False so next game is checked"""
        game_id = "333"
        test_game_state = {
            "turn": "eric",
            "players": ["eric", "polly"],
            "game_status": "playing",
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(RedisGameFinder._join_game("mary", game_id))
        self.assertFalse(mock_db.save_game_transaction.called)

    @patch("src.server.game_finder.db")
    def test_new_player_joins_with_same_name(self, mock_db):
        """Player name already in use for this game, don't add, return False"""
        game_id = "222"
        test_game_state = {
            "turn": "terry",
            "players": ["terry"],
            "game_status": "open",
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(RedisGameFinder._join_game("terry", game_id))
        self.assertFalse(mock_db.save_game_transaction.called)
