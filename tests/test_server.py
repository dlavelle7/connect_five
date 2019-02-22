from unittest import TestCase
from unittest.mock import patch

from src.server import Game


# TODO: View tests with Flask Test request client

class TestServer(TestCase):

    def test_check_vertical_positive_1(self):
        """Xs wins."""
        test_board = [
            [Game.EMPTY, Game.Xs, Game.Xs, Game.Xs, Game.Xs, Game.Xs]
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
