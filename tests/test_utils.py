import json

from unittest import TestCase
from decimal import Decimal

from src.server.utils import DecimalEncoder


class TestUtils(TestCase):

    def test_decimal_type_converted_to_int(self):
        """Dynamodb returns numbers as decimal, convert to json int/float."""
        game = {
            "max_players": Decimal("2.00"),
            "game_id": "1234",
        }
        dumped = json.dumps(game, cls=DecimalEncoder)
        # assert max_player decimal value is serialized as an int
        expected_dumped = '{"max_players": 2, "game_id": "1234"}'
        self.assertEqual(dumped, expected_dumped)
        self.assertIs(json.loads(dumped)["max_players"], 2)
