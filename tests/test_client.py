from unittest import TestCase
from unittest.mock import patch

from src import client


@patch("src.client.requests")
class TestClient(TestCase):

    @patch("src.client.prompt_user", return_value='1')
    def test_make_move_positive_1(self, mock_prompt, mock_requests):
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
