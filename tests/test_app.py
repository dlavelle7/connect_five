from unittest import TestCase
from unittest.mock import patch

from src.server import app


class TestApp(TestCase):

    def setUp(self):
        """Test client for testing requests to the application."""
        app.app.testing = True
        self.client = app.app.test_client()

    def test_get_state(self):
        test_state = {
            "1": {"board": [], "game_status": "playing", "turn": "foo"}
        }
        with patch("src.server.game.Game.state", test_state):
            response = self.client.get("/game/1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(test_state["1"], response.json)

    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=None)
    def test_move_negative_1(self, mock_move, mock_get_disc):
        """Column full, return 400"""
        test_state = {
            "2": {"board": [], "game_status": "playing", "turn": "foo"}
        }
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        with patch("src.server.game.Game.state", test_state):
            response = self.client.patch("/game/2", json=test_payload)
        self.assertEqual(400, response.status_code)
        test_state["2"].update({'message': 'Bad request, column full.'})
        self.assertDictEqual(test_state["2"], response.json)
        mock_move.assert_called_once_with("2", 1, "x")
        mock_get_disc.assert_called_once_with("2", "foo")

    @patch("src.server.game.Game.game_over")
    @patch("src.server.game.Game.has_won", return_value=True)
    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=(1, 2))
    def test_move_positive_1(self, mock_move, mock_get_disc, mock_has_won,
                             mock_game_over):
        """Winning move, inform client with response."""
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        response = self.client.patch("/game", json=test_payload)
        self.assertEqual(200, response.status_code)
        self.assertListEqual(["board", "message"],
                             list(response.json.keys()))
        self.assertEqual("won", response.json["message"])
        mock_move.assert_called_once_with(1, "x")
        mock_get_disc.assert_called_once_with("foo")
        mock_has_won.assert_called_once_with("x", (1, 2))
        mock_game_over.assert_called_once_with()

    @patch("src.server.game.Game.toggle_turn")
    @patch("src.server.game.Game.game_over")
    @patch("src.server.game.Game.has_won", return_value=False)
    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=(1, 2))
    def test_move_positive_2(self, mock_move, mock_get_disc, mock_has_won,
                             mock_game_over, mock_toggle_turn):
        """Move accepted, not a winning one, play on."""
        test_payload = {
            "name": "foo",
            "column": 1,
        }
        response = self.client.patch("/game", json=test_payload)
        self.assertEqual(200, response.status_code)
        self.assertListEqual(["board", "message"],
                             list(response.json.keys()))
        self.assertEqual("OK", response.json["message"])
        mock_move.assert_called_once_with(1, "x")
        mock_get_disc.assert_called_once_with("foo")
        mock_has_won.assert_called_once_with("x", (1, 2))
        self.assertFalse(mock_game_over.called)
