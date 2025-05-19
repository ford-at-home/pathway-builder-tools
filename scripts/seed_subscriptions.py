"""Script to seed the subscriptions table with initial data.

This script populates the subscriptions DynamoDB table with sample subscription
data for testing purposes.
"""

import os
from decimal import Decimal
from typing import Dict, List

import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "subscriptions"))

# Sample subscription data
SUBSCRIPTIONS: List[Dict] = [
    {
        "user_id": "test_user",
        "subscription_id": "sub-001",
        "name": "Spotify",
        "amount": Decimal("9.99"),
        "frequency": "monthly",
        "category": "Entertainment",
        "start_date": "2024-01-01",
    },
    {
        "user_id": "test_user",
        "subscription_id": "sub-002",
        "name": "Netflix",
        "amount": Decimal("15.99"),
        "frequency": "monthly",
        "category": "Entertainment",
        "start_date": "2024-01-01",
    },
]


def seed_subscriptions() -> None:
    """Seed the subscriptions table with initial data."""
    for subscription in SUBSCRIPTIONS:
        table.put_item(Item=subscription)
        print(f"Added subscription: {subscription['name']}")


if __name__ == "__main__":
    seed_subscriptions()
