"""Script to seed the goals table with initial data.

This script populates the financial goals DynamoDB table with sample goal data
for testing purposes.
"""

import os
from decimal import Decimal
from typing import Dict, List

import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "financial_goals"))

# Sample goal data
GOALS: List[Dict] = [
    {
        "user_id": "user-001",
        "goal_id": "goal-001",
        "name": "Buy a House",
        "description": "Save for a down payment on a house",
        "target_amount": Decimal("50000"),
        "current_amount": Decimal("10000"),
        "target_date": "2025-12-31",
        "status": "in_progress",
    },
    {
        "user_id": "user-001",
        "goal_id": "goal-002",
        "name": "Emergency Fund",
        "description": "Build emergency fund",
        "target_amount": Decimal("25000"),
        "current_amount": Decimal("15000"),
        "target_date": "2024-12-31",
        "status": "in_progress",
    },
]


def seed_goals() -> None:
    """Seed the goals table with initial data."""
    for goal in GOALS:
        table.put_item(Item=goal)
        print(f"Added goal: {goal['name']}")


if __name__ == "__main__":
    seed_goals()
