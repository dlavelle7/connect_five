from unittest import TestCase
from unittest.mock import patch, call, Mock

from src import client


board_fixture = [["-"] * client.BOARD_ROWS] * client.BOARD_COLS


@patch("src.client.requests.get")
class TestClientGetRequests(TestCase):

    @patch("src.client.exit_game")
    def test_get_game_state_game_won(self, mock_exit, mock_get):
        """Server responds game won, display board and exit game."""
        mock_response_body = {
            "turn": "foo",
            "game_status": "won",
            "board": board_fixture,
        }
        mock_response = Mock(json=lambda: mock_response_body)
        mock_get.return_value = mock_response
        test_client = client.Client("bar", "123")
        test_client.get_game_state()
        mock_get.assert_called_once_with('http://127.0.0.1/game/123')
        mock_exit.assert_called_once_with("Game over, foo has won.")

    @patch("src.client.exit_game")
    def test_get_game_state_game_disconnected(self, mock_exit, mock_get):
        """Server responds game disconnected, exit game."""
        mock_response_body = {
            "turn": "foo",
            "game_status": "disconnected",
            "board": board_fixture,
        }
        mock_response = Mock(json=lambda: mock_response_body)
        mock_get.return_value = mock_response
        test_client = client.Client("bar", "123")
        test_client.get_game_state()
        mock_get.assert_called_once_with('http://127.0.0.1/game/123')
        mock_exit.assert_called_once_with(
            "Game over, other player disconnected.")

    @patch("src.client.Client.make_move")
    def test_get_game_state_your_turn(self, mock_move, mock_get):
        """Server responds it's this players turn, call make move."""
        mock_response_body = {
            "turn": "bar",
            "game_status": "playing",
            "board": board_fixture,
        }
        mock_response = Mock(json=lambda: mock_response_body)
        mock_get.return_value = mock_response
        test_client = client.Client("bar", "123")
        test_client.get_game_state()
        mock_get.assert_called_once_with('http://127.0.0.1/game/123')
        mock_move.assert_called_once_with()

    @patch("src.client.time.sleep")
    def test_get_game_state_started_new_game(self, mock_sleep, mock_get):
        """Server responds it's waiting on a player to join game, wait."""
        mock_response_body = {
            "turn": None,
            "game_status": "playing",
            "board": board_fixture,
        }
        mock_response = Mock(json=lambda: mock_response_body)
        mock_get.return_value = mock_response
        test_client = client.Client("bar", "123")
        test_client.get_game_state()
        mock_get.assert_called_once_with('http://127.0.0.1/game/123')
        mock_sleep.assert_called_once_with(2)

    @patch("src.client.time.sleep")
    def test_get_game_state_wait_for_turn(self, mock_sleep, mock_get):
        """Server responds it's the other player's turn, wait."""
        mock_response_body = {
            "turn": "foo",
            "game_status": "playing",
            "board": board_fixture,
        }
        mock_response = Mock(json=lambda: mock_response_body)
        mock_get.return_value = mock_response
        test_client = client.Client("bar", "123")
        test_client.get_game_state()
        mock_get.assert_called_once_with('http://127.0.0.1/game/123')
        mock_sleep.assert_called_once_with(2)


@patch("src.client.requests.patch")
class TestClientPatchRequests(TestCase):

    @patch("src.client.display_board")
    @patch("src.client.prompt_user", return_value='1')
    def test_make_move_acceptable_move(self, mock_prompt, mock_display,
                                       mock_patch):
        mock_patch.return_value = Mock(status_code=200)
        test_client = client.Client("foo", "123")
        test_client.make_move()
        expected_message = "It's your turn foo, please enter column (1 - 9): "
        mock_prompt.assert_called_once_with(expected_message)
        expected_payload = {
            "name": "foo",
            "column": 1,
        }
        expected_url = "http://127.0.0.1/game/123"
        mock_patch.assert_called_once_with(
            expected_url, json=expected_payload)
        mock_display.assert_called_once()

    @patch("src.client.display_board")
    @patch("src.client.prompt_user", side_effect=["", "a", '0', '10', '9'])
    def test_make_move_invalid_column(
            self, mock_prompt, mock_display, mock_patch):
        """Assert the user is prompted until a valid column is chosen."""
        mock_patch.return_value = Mock(status_code=200)
        test_client = client.Client("bar", "456")
        test_client.make_move()
        first_promt = "It's your turn bar, please enter column (1 - 9): "
        retry_prompt = 'Invalid choice, please enter column (1 - 9): '
        expected_calls = [
            call(first_promt),
            call(retry_prompt),
            call(retry_prompt),
            call(retry_prompt),
            call(retry_prompt)
        ]
        self.assertListEqual(mock_prompt.call_args_list, expected_calls)
        expected_payload = {
            "name": "bar",
            "column": 9,
        }
        expected_url = "http://127.0.0.1/game/456"
        mock_patch.assert_called_once_with(
            expected_url, json=expected_payload)
        mock_display.assert_called_once()

    @patch("src.client.display_board")
    @patch("src.client.prompt_user", side_effect=['2', '3'])
    def test_make_move_column_full(self, mock_prompt, mock_display,
                                   mock_patch):
        """Assert user is informed if column is full and is re-prompted."""
        retry_prompt = 'Column 2 is full, please try another: '
        # mock response from server, column is full
        mock_body = {"message": retry_prompt}
        mock_response = Mock(status_code=400, json=lambda: mock_body)
        mock_patch.side_effect = [mock_response, Mock(status_code=200)]

        test_client = client.Client("lola", "789")
        test_client.make_move()
        first_promt = "It's your turn lola, please enter column (1 - 9): "
        expected_prompts = [
            call(first_promt),
            call(retry_prompt),
        ]
        self.assertListEqual(mock_prompt.call_args_list, expected_prompts)
        expected_url = "http://127.0.0.1/game/789"
        expected_calls = [
            call(expected_url, json={'column': 2, 'name': 'lola'}),
            call(expected_url, json={'column': 3, 'name': 'lola'})]
        self.assertListEqual(mock_patch.call_args_list,
                             expected_calls)
        mock_display.assert_called_once()


@patch("src.client.requests.post")
class TestClientPostRequests(TestCase):

    @patch("src.client.prompt_user", side_effect=["eric", "2"])
    @patch("src.client.exit")
    def test_connect_acceptable_name(self, mock_exit, mock_prompt, mock_post):
        """Assert that with an acceptable name, user is prompted once."""
        json = {"game_id": "123"}
        mock_post.return_value = Mock(status_code=201, json=lambda: json)
        self.assertEqual(client.connect(), ("eric", "123"))
        self.assertFalse(mock_exit.called)
        mock_post.assert_called_once_with(
            'http://127.0.0.1/game', json={'name': 'eric', 'max_players': 2})
