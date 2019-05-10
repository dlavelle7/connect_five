from unittest import TestCase
from unittest.mock import patch

from src.server.game import Game


class TestGame(TestCase):

    def test_check_vertical_x_wins_5_down(self):
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

    def test_check_vertical_x_doesnt_win_mixed(self):
        """Xs doesn't win -> next vertical 4 has a mix of Xs & Os."""
        test_board = [
            [Game.Xs, Game.Os, Game.Xs, Game.Xs, Game.Xs, Game.Xs]
        ]
        has_won = Game.check_vertical(test_board, Game.Xs, 0, 0)
        self.assertFalse(has_won)

    def test_check_vertical_o_doesnt_win_mixed(self):
        """Os doesn't win -> there are not 5 contiguous discs in column."""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os, Game.Os]
        ]
        has_won = Game.check_vertical(test_board, Game.Os, 0, 4)
        self.assertFalse(has_won)

    def test_check_horizontal_x_wins_5_across_to_right(self):
        """Xs wins -> 5 in a row horizontally accross top of board (right)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 1, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_x_wins_5_across_to_left(self):
        """Xs wins -> 5 in a row horizontally accross top of board (left)."""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 5, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_bug_x_wins_5_across_to_left_place_at_end(self):
        """Xs wins -> 5 in a row (left): Off by one error."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 4, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_x_wins_5_across_place_disc_in_middle(self):
        """Xs wins -> 5 in a row horizontally accross top (left and right)"""
        test_board = [
            [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 3, 0)
        self.assertTrue(has_won)

    def test_check_horizontal_x_doesnt_win_place_in_middle_4_across(self):
        """Xs doesn't win -> 1 X to the rhs & 2 Xs to the lhs."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs],
            [Game.Os], [Game.Os], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 4, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_x_doesnt_win_place_at_end_4_across(self):
        """Xs doesn't win -> Noting to rhs, and 3 Xs to the left."""
        test_board = [
            [Game.Os], [Game.Os], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 8, 0)
        self.assertFalse(has_won)

    def test_check_horizontal_x_doesnt_will_only_1_x_each_side(self):
        """Xs doesn't win -> 1 X to lhs, and 1 X to the rhs."""
        test_board = [
            [Game.Xs], [Game.Xs], [Game.Xs], [Game.Os],
            [Game.EMPTY], [Game.Xs], [Game.Xs], [Game.Xs], [Game.Xs]
        ]
        has_won = Game.check_horizontal(test_board, Game.Xs, 1, 0)
        self.assertFalse(has_won)

    def test_check_diagonal_1_o_wins_5_to_right_and_down(self):
        """Os win -> 4 Os rhs and down (Direction: '\')"""
        test_board = [
            [Game.Os],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 0, 0)
        self.assertTrue(has_won)

    def test_check_diagonal_1_o_wins_2_to_right_and_2_to_left(self):
        """Os win -> 2 Os rhs down & 2 Os lhs up (Direction: '\')"""
        test_board = [
            [Game.Xs],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 3, 3)
        self.assertTrue(has_won)

    def test_check_diagonal_1_o_doesnt_will_1_left_2_right(self):
        """Os doesn't win -> not enough Os left or right (Direction: '\')"""
        test_board = [
            [Game.Xs],
            [Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Xs],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_1(test_board, Game.Os, 3, 3)
        self.assertFalse(has_won)

    def test_check_diagonal_2_x_wins_1_to_left_and_3_to_right(self):
        """Xs win -> 1 Xs lhs down & 3 Xs rhs up (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs, Game.Os],
            [Game.EMPTY, Game.EMPTY, Game.Xs, Game.Xs, Game.Os],
            [Game.EMPTY, Game.Xs, Game.Os, Game.Os, Game.Xs],
            [Game.Xs, Game.Xs, Game.Os, Game.Os, Game.Xs],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 1, 3)
        self.assertTrue(has_won)

    def test_check_diagonal_2_x_wins_4_to_left_and_down(self):
        """Xs win -> 4 Xs lhs down (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.Xs],
            [Game.Xs],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 4, 0)
        self.assertTrue(has_won)

    def test_check_diagonal_2_x_wins_4_to_right_and_up(self):
        """Xs win -> 4 Xs rhs up (Direction '/')"""
        test_board = [
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.EMPTY, Game.Xs],
            [Game.EMPTY, Game.Xs],
            [Game.Xs],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Xs, 0, 4)
        self.assertTrue(has_won)

    def test_check_diagonal_2_x_doesnt_win_only_3_in_a_row(self):
        """Xs doesn't win -> not enough Xs left or right (Direction '/')"""
        test_board = [
            [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.EMPTY], [Game.Xs],
            [Game.EMPTY], [Game.Os],
            [Game.Xs],
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
            [Game.EMPTY] * 6,
        ]
        has_won = Game.check_diagonal_2(test_board, Game.Os, 1, 3)
        self.assertFalse(has_won)

    @patch("src.server.game.Game.check_horizontal")
    @patch("src.server.game.Game.check_vertical", return_value=True)
    def test_has_won_return_true_on_2nd_check(self, mock_vert, mock_horiz):
        """Assert if one of the 'check' functions returns True, player wins"""
        game = Game("1")
        game.game = {"board": []}
        self.assertTrue(game.has_won('x', (0, 1)))
        mock_vert.assert_called_once_with([], 'x', 0, 1)
        self.assertFalse(mock_horiz.called)

    @patch("src.server.game.Game.check_has_won_methods",
           return_value=[False, False])
    def test_has_won_all_check_methods_return_false(self, mock_check_methods):
        """Assert if none of the 'check' functions return True game still on"""
        game = Game("2")
        game.game = {"board": []}
        self.assertFalse(game.has_won('x', (0, 1)))

    @patch("src.server.game.db")
    def test_start_new_game(self, mock_db):
        """new player added to 'players', their turn and board created."""
        game_id = Game.start_new_game("dave")
        self.assertIsInstance(game_id, str)
        call_game_id, call_game_state = mock_db.save_game.call_args[0]
        self.assertEqual(game_id, call_game_id)
        self.assertIsInstance(call_game_state["board"], list)
        self.assertEqual("dave", call_game_state["turn"])
        self.assertListEqual(["dave"], call_game_state["players"])
        self.assertEqual("playing", call_game_state["game_status"])
        self.assertEqual(2, call_game_state["max_players"])

    @patch("src.server.game.db")
    def test_2nd_player_joins_after_player1_has_moved(self, mock_db):
        """2nd player added, player 1 had already moved, their turn now"""
        game_id = "246"
        test_game_state = {
            "turn": None,
            "players": ["dom"],
            "game_status": Game.PLAYING,
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        Game.join_existing_game("mary", game_id)

        _, call_game_id, call_game_state = \
            mock_db.save_game_transaction.call_args[0]

        self.assertEqual(game_id, call_game_id)
        self.assertEqual("mary", call_game_state["turn"])
        self.assertListEqual(["dom", "mary"], call_game_state["players"])

    @patch("src.server.game.db")
    def test_2nd_player_joins_while_its_player1s_move(self, mock_db):
        """2nd player added, while it's player 1 move, not their turn now."""
        game_id = "246"
        test_game_state = {
            "turn": "dom",
            "players": ["dom"],
            "game_status": Game.PLAYING,
            "max_players": 2,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        Game.join_existing_game("mary", game_id)

        _, call_game_id, call_game_state = \
            mock_db.save_game_transaction.call_args[0]

        self.assertEqual(game_id, call_game_id)
        self.assertEqual("dom", call_game_state["turn"])
        self.assertListEqual(["dom", "mary"], call_game_state["players"])

    @patch("src.server.game.db")
    def test_bug_2nd_player_cant_join_disconnected_game(self, mock_db):
        """2nd player added, game checked has been disconnected, can't join."""
        game_id = "888"
        test_game_state = {
            "turn": "bob",
            "players": ["bob"],
            "game_status": Game.DISCONNECTED,
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(Game.join_existing_game("mary", game_id))

    @patch("src.server.game.db")
    def test_new_player_joins_this_game_already_full(self, mock_db):
        """This existing game is full, return False so next game is checked"""
        game_id = "333"
        test_game_state = {
            "turn": "eric",
            "players": ["eric", "polly"],
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(Game.join_existing_game("mary", game_id))
        self.assertFalse(mock_db.save_game_transaction.called)

    @patch("src.server.game.db")
    def test_new_player_joins_with_same_name(self, mock_db):
        """Player name already in use for this game, don't add, return False"""
        game_id = "222"
        test_game_state = {
            "turn": "terry",
            "players": ["terry"],
        }
        mock_db.get_game_transaction.return_value = test_game_state
        self.assertFalse(Game.join_existing_game("terry", game_id))
        self.assertFalse(mock_db.save_game_transaction.called)

    def test_get_player_disc_colour_player_1_is_xs_no_player_2(self):
        """Test with one player, 2nd player hasn't joined yet"""
        game = Game("1")
        game.game = {"players": ["john"]}
        disc = game.get_player_disc_colour("john")
        self.assertEqual("x", disc)

    def test_get_player_disc_colour_player_1_is_xs_2_players(self):
        """Player 1 is Xs"""
        game = Game("1")
        game.game = {"players": ["robin", "brian"]}
        disc = game.get_player_disc_colour("robin")
        self.assertEqual("x", disc)

    def test_get_player_disc_colour_player_2_is_ys_2_players(self):
        """Player 2 is Ys"""
        game = Game("1")
        game.game = {"players": ["robin", "brian"]}
        disc = game.get_player_disc_colour("brian")
        self.assertEqual("o", disc)

    @patch("src.server.game.db")
    def test_toggle_turn_player_1_moved(self, mock_db):
        game = Game("1")
        game.game = {"players": ["arthur", "billy"]}
        game.toggle_turn("arthur")
        mock_db.save_game.assert_called_once_with(
            '1', {'players': ['arthur', 'billy'], 'turn': 'billy'})

    @patch("src.server.game.db")
    def test_toggle_turn_player_2_moved(self, mock_db):
        game = Game("2")
        game.game = {
            "players": ["dingo", "zoot"],
            "max_players": 2,
        }
        game.toggle_turn("zoot")
        mock_db.save_game.assert_called_once_with(
            '2', {'players': ['dingo', 'zoot'],
                  'turn': 'dingo',
                  'max_players': 2})

    @patch("src.server.game.db")
    def test_toggle_turn_player_1_moved_no_player_2(self, mock_db):
        """2nd player hasn't joined yet, turn = None."""
        game = Game("3")
        game.game = {
            "players": ["galahad"],
            "max_players": 2,
        }
        game.toggle_turn("galahad")
        mock_db.save_game.assert_called_once_with(
            '3', {'players': ['galahad'], 'turn': None, 'max_players': 2})

    @patch("src.server.game.db")
    def test_game_over_won(self, mock_db):
        game = Game("1")
        game.game = {}
        game.game_over()
        mock_db.save_game.assert_called_once_with("1", {"game_status": "won"})

    @patch("src.server.game.db")
    def test_game_over_disconnected(self, mock_db):
        game = Game("1")
        game.game = {}
        game.game_over(won=False)
        mock_db.save_game.assert_called_once_with(
            "1", {"game_status": "disconnected"})
