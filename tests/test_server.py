from unittest import TestCase
from unittest.mock import patch, call, Mock

from src.server import Game


# TODO: View tests with Flask Test request client

class TestServer(TestCase):

    def test_check_vertical_positive(self):
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Xs, Game.Xs]
        ]
        with patch("src.server.Game.board", test_board):
            has_won = Game.check_vertical(Game.Xs, 0, 1)
        self.assertTrue(has_won)
