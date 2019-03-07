from unittest import TestCase
from unittest.mock import patch

from src.server.game import Game


class TestGame(TestCase):

    def test_check_vertical_positive_1(self):
        """Xs wins -> 5 in a row down."""
        test_board = [
            [Game.EMPTY,
             Game.Xs,
             Game.Xs,
             Game.Xs,
             Game.Xs,
             Game.Xs]
        ]
        has_won = Game.check_vertical(test_board, Game.Xs, 0, 1)
        self.assertTrue(has_won)

    def test_check_vertical_negative_1(self):
        """Xs doesn't win -> next vertical 4 has a mix of Xs & Os."""
        test_board = [
            [Game.Xs, Game.Os, Game.Xs, Game.Xs, Game.Xs, Game.Xs]
        ]
        has_won = Game.check_vertical(test_board, Game.Xs, 0, 0)
        self.assertFalse(has_won)

    def test_check_vertical_negative_2(self):
        """Os doesn't win -> there are not 5 contiguous discs in column."""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os, Game.Os]
        ]
        has_won = Game.check_vertical(test_board, Game.Os, 0, 4)
        self.assertFalse(has_won)

    def test_check_horizontal_positive_1(self):
        """Xs wins -> 5 in a row horizontally accross top of board (right)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 1, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_positive_2(self):
        """Xs wins -> 5 in a row horizontally accross top of board (left)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 5, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_bug(self):
        """Xs wins -> 5 in a row (left): Off by one error."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 4, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_positive_3(self):
        """Xs wins -> 5 in a row horizontally accross top (left and right)"""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 3, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_negative_1(self):
        """Xs doesn't win -> 1 X to the rhs & 2 Xs to the lhs."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 4, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_negative_2(self):
        """Xs doesn't win -> Noting to rhs, and 3 Xs to the left."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 8, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_negative_3(self):
        """Xs doesn't win -> 1 X to lhs, and 1 X to the rhs."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 1, 0)
        self.assertFalse(has_won)

    def test_check_diagonal_1_positive_1(self):
        """Os win -> 4 Os rhs and down (Direction: '\')"""
        test_board = [
            [Game.Os],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 0, 0)
        self.assertTrue(has_won)

    def test_check_diagonal_1_positive_2(self):
        """Os win -> 2 Os rhs down & 2 Os lhs up (Direction: '\')"""
        test_board = [
            [Game.Xs],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 3, 3)
        self.assertTrue(has_won)

    def test_check_diagonal_1_negative_1(self):
        """Os doesn't win -> not enough Os left or right (Direction: '\')"""
        test_board = [
            [Game.Xs],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Xs],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 3, 3)
        self.assertFalse(has_won)

    def test_check_diagonal_2_positive_1(self):
        """Xs win -> 1 Xs lhs down & 3 Os rhs up (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.Xs, Game.Os, Game.Os, Game.Xs],
            [Game.Xs, Game.Xs, Game.Os, Game.Os, Game.Xs],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 1, 3)
        self.assertTrue(has_won)

    def test_check_diagonal_2_positive_2(self):
        """Xs win -> 4 Xs lhs down (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.Xs],
            [Game.Xs],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 4, 0)
        self.assertTrue(has_won)

    def test_check_diagonal_2_positive_3(self):
        """Xs win -> 4 Xs rhs up (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.Xs],
            [Game.Xs],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 0, 4)
        self.assertTrue(has_won)

    def test_check_diagonal_2_negative_1(self):
        """Xs doesn't win -> not enough Xs left or right (Direction '/')"""
        test_board = [
            [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.Os],
            [Game.Xs],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
            [Game.EMPTY * 6],
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Os, 1, 3)
        self.assertFalse(has_won)

    @patch("src.server.game.Game.check_diagonal_2", return_value=False)
    @patch("src.server.game.Game.check_diagonal_1", return_value=True)
    @patch("src.server.game.Game.check_horizontal", return_value=False)
    @patch("src.server.game.Game.check_vertical", return_value=False)
    def test_has_won_positive(self, mock_vert, mock_horiz, mock_d1, mock_d2):
        """Assert if one of the 'check' functions returns True, player wins"""
        self.assertTrue(Game.has_won('x', (0, 1)))
        mock_vert.assert_called_once_with('x', 0, 1)
        mock_horiz.assert_called_once_with('x', 0, 1)
        mock_d1.assert_called_once_with('x', 0, 1)
        self.assertFalse(mock_d2.called)

    @patch("src.server.game.Game.check_diagonal_2", return_value=False)
    @patch("src.server.game.Game.check_diagonal_1", return_value=False)
    @patch("src.server.game.Game.check_horizontal", return_value=False)
    @patch("src.server.game.Game.check_vertical", return_value=False)
    def test_has_won_negative(self, mock_vert, mock_horiz, mock_d1, mock_d2):
        """Assert if none of the 'check' functions return True game still on"""
        self.assertFalse(Game.has_won('x', (0, 1)))
        mock_vert.assert_called_once_with('x', 0, 1)
        mock_horiz.assert_called_once_with('x', 0, 1)
        mock_d1.assert_called_once_with('x', 0, 1)
        mock_d2.assert_called_once_with('x', 0, 1)

    def test_new_player_positive_1(self):
        """1st new player, gets added, their turn and board created."""
        test_state = {}
        with patch("src.server.game.Game.state", test_state):
            game_id = Game.new_player("dave")
        self.assertIsInstance(game_id, str)
        self.assertIsInstance(test_state[game_id]["board"], list)
        self.assertEqual("dave", test_state[game_id]["turn"])
        self.assertListEqual(["dave"], test_state[game_id]["players"])
        self.assertEqual("playing", test_state[game_id]["game_status"])

    @patch("src.server.game.Game.start_new_game")
    def test_new_player_positive_2(self, mock_start_new_game):
        """2nd new player, gets added, not their turn and board not created."""
        with patch("src.server.game.Game.players", ["dom"]) as mock_players:
            added, code = Game.new_player("mary")
            self.assertNotEqual("mary", Game.turn)
        self.assertListEqual(["dom", "mary"], mock_players)
        self.assertTrue(added)
        self.assertEqual(201, code)
        self.assertFalse(mock_start_new_game.called)

    def test_new_player_negative_2(self):
        """Player name already in use, return 409."""
        with patch("src.server.game.Game.players", ["terry"]):
            added, code = Game.new_player("terry")
        self.assertFalse(added)
        self.assertEqual(409, code)

    def test_get_player_disc_colour_positive_1(self):
        """Test with one player, 2nd player hasn't joined yet"""
        with patch("src.server.game.Game.players", ["john"]):
            disc = Game.get_player_disc_colour("john")
        self.assertEqual("x", disc)

    def test_get_player_disc_colour_positive_2(self):
        """Player 1 is Xs"""
        with patch("src.server.game.Game.players", ["robin", "brian"]):
            disc = Game.get_player_disc_colour("robin")
        self.assertEqual("x", disc)

    def test_get_player_disc_colour_positive_3(self):
        """Player 2 is Ys"""
        with patch("src.server.game.Game.players", ["robin", "brian"]):
            disc = Game.get_player_disc_colour("brian")
        self.assertEqual("o", disc)

    def test_toggle_turn_positive_1(self):
        game_id = "123"
        test_state = {
            game_id: {"players": ["arthur", "billy"]}
        }
        with patch("src.server.game.Game.state", test_state):
            Game.toggle_turn(game_id, "arthur")
            self.assertEqual(Game.state[game_id]["turn"], "billy")

    def test_toggle_turn_positive_2(self):
        game_id = "12"
        test_state = {
            game_id: {"players": ["dingo", "zoot"]}
        }
        with patch("src.server.game.Game.state", test_state):
            Game.toggle_turn(game_id, "zoot")
            self.assertEqual(Game.state[game_id]["turn"], "dingo")

    def test_toggle_turn_negative_1(self):
        """2nd player hasn't joined yet, turn = None."""
        game_id = "1"
        test_state = {
            game_id: {"players": ["galahad"]}
        }
        with patch("src.server.game.Game.state", test_state):
            Game.toggle_turn(game_id, "galahad")
            self.assertIsNone(Game.state[game_id]["turn"])
