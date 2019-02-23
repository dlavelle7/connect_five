from unittest import TestCase

from src.server import app


class TestApp(TestCase):

    def setUp(self):
        """Test client for testing requests to the application."""
        app.app.testing = True
        self.client = app.app.test_client()

    def test_state(self):
        response = self.client.get("/state")
        self.assertEqual(200, response.status_code)
        self.assertListEqual(["board", "game_status", "turn"],
                             list(response.json.keys()))

    # TODO: Test other endpoints
