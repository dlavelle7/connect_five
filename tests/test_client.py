from unittest import TestCase
from unittest.mock import patch, call, Mock

from src import client


@patch("src.client.requests.patch")
class TestClient(TestCase):

    @patch("src.client.prompt_user", return_value='1')
    def test_make_move_positive(self, mock_prompt, mock_patch):
        mock_patch.return_value = Mock(status_code=200)
        client.make_move("foo")
        expected_message = "It's your turn foo, please enter column (1 - 9): "
        mock_prompt.assert_called_once_with(expected_message)
        expected_payload = {
            "name": "foo",
            "column": 1,
        }
        expected_url = "http://127.0.0.1:5000/move"
        mock_patch.assert_called_once_with(
            expected_url, json=expected_payload)

    @patch("src.client.prompt_user", side_effect=["", "a", '0', '10', '9'])
    def test_make_move_negative(self, mock_prompt, mock_patch):
        """Assert the user is prompted until a valid column is chosen."""
        mock_patch.return_value = Mock(status_code=200)
        client.make_move("bar")
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
        expected_url = "http://127.0.0.1:5000/move"
        mock_patch.assert_called_once_with(
            expected_url, json=expected_payload)

    @patch("src.client.prompt_user", side_effect=['2', '3'])
    def test_make_move_negative_2(self, mock_prompt, mock_patch):
        """Assert user is informed if column is full and is re-prompted."""
        retry_prompt = 'Column 2 is full, please try another: '
        # mock response from server, column is full
        mock_body = {"message": retry_prompt}
        mock_response = Mock(status_code=400, json=lambda: mock_body)
        mock_patch.side_effect = [mock_response,
                                           Mock(status_code=200)]

        client.make_move("lola")
        first_promt = "It's your turn lola, please enter column (1 - 9): "
        expected_prompts = [
            call(first_promt),
            call(retry_prompt),
        ]
        self.assertListEqual(mock_prompt.call_args_list, expected_prompts)
        expected_url = "http://127.0.0.1:5000/move"
        expected_calls = [
            call(expected_url, json={'column': 2, 'name': 'lola'}),
            call(expected_url, json={'column': 3, 'name': 'lola'})]
        self.assertListEqual(mock_patch.call_args_list,
                             expected_calls)
