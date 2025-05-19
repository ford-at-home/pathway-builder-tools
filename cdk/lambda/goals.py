"""Lambda function for managing financial goals.

This module provides CRUD operations for financial goals, including:
- Getting a user's goals
- Creating/updating a goal
- Deleting a goal
"""

import os
from typing import Any, Dict

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle CRUD operations for financial goals.

    Args:
        event: The Lambda event containing the action and goal data
        context: The Lambda context

    Returns:
        Dict containing the operation result or error message

    Actions:
        - get: Retrieve all goals for a user
        - put: Create or update a goal
        - delete: Delete a goal by ID
    """
    action = event.get("action")
    user_id = event.get("user_id", "user-123")

    if action == "get":
        response = table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
        )
        return {"goals": response.get("Items", [])}
    elif action == "put":
        item = event.get("goal")
        table.put_item(Item=item)
        return {"status": "put success"}
    elif action == "delete":
        goal_id = event["goal_id"]
        table.delete_item(Key={"user_id": user_id, "goal_id": goal_id})
        return {"status": "delete success"}
    return {"error": "unknown action"}
