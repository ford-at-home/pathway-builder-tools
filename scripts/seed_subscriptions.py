from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("subscriptions")

subscriptions = [
    {
        "user_id": "user-123",
        "subscription_id": "sub-001",
        "name": "Spotify",
        "amount": Decimal("9.99"),
        "frequency": "monthly",
        "category": "Entertainment",
        "start_date": "2024-11-01",
    },
    {
        "user_id": "user-123",
        "subscription_id": "sub-002",
        "name": "Netflix",
        "amount": Decimal("15.99"),
        "frequency": "monthly",
        "category": "Entertainment",
        "start_date": "2024-10-15",
    },
]

for item in subscriptions:
    table.put_item(Item=item)
