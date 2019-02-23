from unittest import TestCase
from unittest.mock import patch

from src.server import Game


# TODO: View tests with Flask Test request client

class TestServer(TestCase):

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
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_vertical(Game.Xs, 0, 1)
        self.assertTrue(has_won)

    def test_check_vertical_negative_1(self):
        """Xs doesn't win -> next vertical 4 has a mix of Xs & Os."""
        test_board = [
            [Game.Xs, Game.Os, Game.Xs, Game.Xs, Game.Xs, Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_vertical(Game.Xs, 0, 0)
        self.assertFalse(has_won)

    def test_check_vertical_negative_2(self):
        """Os doesn't win -> there are not 5 contiguous discs in column."""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os, Game.Os]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_vertical(Game.Os, 0, 4)
        self.assertFalse(has_won)

    def test_check_horizontal_positive_1(self):
        """Xs wins -> 5 in a row horizontally accross top of board (right)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 1, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_positive_2(self):
        """Xs wins -> 5 in a row horizontally accross top of board (left)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 5, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_bug(self):
        """Xs wins -> 5 in a row (left): Off by one error."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Os], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 4, 0)
        self.assertTrue(has_won)


    def test_check_horizontal_positive_3(self):
        """Xs wins -> 5 in a row horizontally accross top (left and right)"""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 3, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_negative_1(self):
        """Xs doesn't win -> 1 X to the rhs & 2 Xs to the lhs."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 4, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_negative_2(self):
        """Xs doesn't win -> Noting to rhs, and 3 Xs to the left."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 8, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_negative_3(self):
        """Xs doesn't win -> 1 X to lhs, and 1 X to the rhs."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_horizontal(Game.Xs, 1, 0)
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
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_diagonal_1(Game.Os, 0, 0)
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
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_diagonal_1(Game.Os, 3, 3)
        self.assertTrue(has_won)

    def test_check_diagonal_2_positive_1(self):
        # TODO:
        pass
