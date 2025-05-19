from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("financial_goals")

goals = [
    {
        "user_id": "user-123",
        "goal_id": "goal-001",
        "name": "Vacation Fund",
        "target_amount": Decimal("3000"),
        "current_amount": Decimal("1200"),
        "due_date": "2024-12-31",
        "category": "Travel",
    },
    {
        "user_id": "user-123",
        "goal_id": "goal-002",
        "name": "Emergency Fund",
        "target_amount": Decimal("10000"),
        "current_amount": Decimal("3500"),
        "due_date": "2024-06-30",
        "category": "Savings",
    },
]

for item in goals:
    table.put_item(Item=item)
