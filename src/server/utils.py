import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert a DynamoDB item to JSON."""

    def default(self, value):
        if isinstance(value, decimal.Decimal):
            if value % 1 > 0:
                return float(value)
            else:
                return int(value)
        return super(DecimalEncoder, self).default(value)
