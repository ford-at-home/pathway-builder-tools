"""Lambda function for managing user subscriptions.

This module provides functionality to retrieve a user's active subscriptions
from the database.
"""

import os
from typing import Any, Dict

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve all subscriptions for a user.

    Args:
        event: The Lambda event containing the user_id
        context: The Lambda context (unused in this function)

    Returns:
        Dict containing a list of the user's subscriptions
    """
    user_id = event.get("user_id", "user-123")
    response = table.query(
        KeyConditionExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )
    return {"subscriptions": response.get("Items", [])}
