from unittest import TestCase
from unittest.mock import patch

from src.server import app


class TestApp(TestCase):

    def setUp(self):
        """Test client for testing requests to the application."""
        app.app.testing = True
        self.client = app.app.test_client()
        # mock game state for each test method
        self.test_state = {
            "board": [], "game_status": "playing", "turn": "foo"}
        self.patcher = patch("src.server.game.db.get_game",
                             return_value=self.test_state)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_get_state(self):
        response = self.client.get("/game/2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.test_state, response.json)

    @patch("src.server.game.Game.move", return_value=None)
    def test_move_column_full(self, mock_move):
        """Column full, return 400"""
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        response = self.client.patch("/game/2", json=test_payload)
        self.assertEqual(400, response.status_code)
        expected_msg = 'Bad request, column full.'
        self.assertEqual(expected_msg, response.json.pop("message"))
        self.assertDictEqual(self.test_state, response.json)
        mock_move.assert_called_once_with("foo", 1)

    @patch("src.server.game.Game.move", return_value=True)
    def test_move_winning_move(self, mock_move):
        """Winning move, inform client with response."""
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        response = self.client.patch("/game/2", json=test_payload)
        self.assertEqual(200, response.status_code)
        expected_msg = 'won'
        self.assertEqual(expected_msg, response.json.pop("message"))
        self.assertDictEqual(self.test_state, response.json)
        mock_move.assert_called_once_with("foo", 1)

    @patch("src.server.game.Game.move", return_value=False)
    def test_move_no_win(self, mock_move):
        """Move accepted, not a winning one, play on."""
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        response = self.client.patch("/game/2", json=test_payload)
        self.assertEqual(200, response.status_code)
        expected_msg = 'OK'
        self.assertEqual(expected_msg, response.json.pop("message"))
        self.assertDictEqual(self.test_state, response.json)
        mock_move.assert_called_once_with("foo", 1)

    @patch("src.server.game.Game.game_over")
    def test_disconnect(self, mock_game_over):
        """PATCH request to disconnect from a game."""
        test_payload = {
            "game_status": "disconnected"
        }
        response = self.client.patch("/game/2", json=test_payload)
        self.assertEqual(200, response.status_code)
        expected_msg = 'OK'
        self.assertEqual(expected_msg, response.json.pop("message"))
        mock_game_over.assert_called_once_with(won=False)
