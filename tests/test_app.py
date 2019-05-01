from unittest import TestCase
from unittest.mock import patch

from src.server import app


# FIXME: More meaningful test method names
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

    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=None)
    def test_move_column_full(self, mock_move, mock_get_disc):
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
        mock_move.assert_called_once_with(self.test_state, 1, "x")
        mock_get_disc.assert_called_once_with(self.test_state, "foo")

    # FIXME: Too much mocking
    @patch("src.server.game.Game.game_over")
    @patch("src.server.game.Game.has_won", return_value=True)
    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=(1, 2))
    def test_move_winning_move(self, mock_move, mock_get_disc, mock_has_won,
                             mock_game_over):
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
        mock_move.assert_called_once_with(self.test_state, 1, "x")
        mock_get_disc.assert_called_once_with(self.test_state, "foo")
        mock_has_won.assert_called_once_with(self.test_state, "x", (1, 2))
        mock_game_over.assert_called_once_with("2", self.test_state)

    # FIXME: Too much mocking
    @patch("src.server.game.Game.toggle_turn")
    @patch("src.server.game.Game.game_over")
    @patch("src.server.game.Game.has_won", return_value=False)
    @patch("src.server.game.Game.get_player_disc_colour", return_value="x")
    @patch("src.server.game.Game.make_move", return_value=(1, 2))
    def test_move_no_win(self, mock_move, mock_get_disc, mock_has_won,
                         mock_game_over, mock_toggle_turn):
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
        mock_move.assert_called_once_with(self.test_state, 1, "x")
        mock_get_disc.assert_called_once_with(self.test_state, "foo")
        mock_has_won.assert_called_once_with(self.test_state, "x", (1, 2))
        self.assertFalse(mock_game_over.called)
