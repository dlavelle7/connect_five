from unittest import TestCase
from unittest.mock import patch, call, Mock

from src import client


@patch("src.client.requests")
class TestClient(TestCase):

    @patch("src.client.prompt_user", return_value='1')
    def test_make_move_positive(self, mock_prompt, mock_requests):
        client.make_move("foo")
        expected_message = "It's your turn foo, please enter column (1 - 9): "
        mock_prompt.assert_called_once_with(expected_message)
        expected_payload = {
            "name": "foo",
            "column": 1,
        }
        expected_url = "http://127.0.0.1:5000/move"
        mock_requests.patch.assert_called_once_with(
            expected_url, json=expected_payload)

    @patch("src.client.prompt_user", side_effect=["", "a", '0', '10', '9'])
    def test_make_move_negative(self, mock_prompt, mock_requests):
        """Assert the user is prompted until a valid column is chosen."""
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
        mock_requests.patch.assert_called_once_with(
            expected_url, json=expected_payload)

    @patch("src.client.prompt_user", side_effect=['2', '3'])
    def skip_test_make_move_negative_2(self, mock_prompt, mock_requests):
        """Assert user is informed if column is full and is re-prompted."""
        retry_prompt = 'Column 2 is full, please try another: '
        mock_body = {"message": retry_prompt}
        mock_response = Mock(status_code=400, json=lambda: mock_body)
        mock_requests.patch.return_value = mock_response
        # FIXME: all of requests is mocked, so too the status codes!
        client.make_move("lola")
        first_promt = "It's your turn lola, please enter column (1 - 9): "
        expected_calls = [
            call(first_promt),
            call(retry_prompt),
        ]
        self.assertListEqual(mock_prompt.call_args_list, expected_calls)
        expected_payload = {
            "name": "lola",
            "column": 3,
        }
        expected_url = "http://127.0.0.1:5000/move"
        mock_requests.patch.assert_called_once_with(
            expected_url, json=expected_payload)
