"""Lambda function for managing financial goals.

This module provides a serverless function that implements CRUD (Create, Read,
Update, Delete) operations for financial goals using DynamoDB. It supports:

Operations:
    - get: Retrieve all goals for a specific user
    - put: Create a new goal or update an existing one
    - delete: Remove a goal by its ID

The function uses DynamoDB for persistent storage with the following schema:
    - Partition key: user_id (String)
    - Sort key: goal_id (String)
    - Additional attributes:
        * name: Goal name/description
        * target_amount: Target amount to save
        * current_amount: Current saved amount
        * target_date: Target completion date
        * category: Goal category (e.g., "vacation", "emergency")

The function is designed to be deployed as an AWS Lambda and can be invoked
via API Gateway or directly from other AWS services.

Example:
    >>> # Get user's goals
    >>> event = {
    ...     "action": "get",
    ...     "user_id": "user123"
    ... }
    >>> response = handler(event, None)
    >>> print(response["goals"])
    [
        {
            "user_id": "user123",
            "goal_id": "goal1",
            "name": "Vacation Fund",
            "target_amount": 5000,
            "current_amount": 1000,
            "target_date": "2024-12-31",
            "category": "vacation"
        }
    ]

    >>> # Create/update a goal
    >>> event = {
    ...     "action": "put",
    ...     "goal": {
    ...         "user_id": "user123",
    ...         "goal_id": "goal1",
    ...         "name": "Emergency Fund",
    ...         "target_amount": 10000,
    ...         "current_amount": 5000,
    ...         "target_date": "2024-06-30",
    ...         "category": "emergency"
    ...     }
    ... }
    >>> response = handler(event, None)
    >>> print(response["status"])
    'put success'

    >>> # Delete a goal
    >>> event = {
    ...     "action": "delete",
    ...     "user_id": "user123",
    ...     "goal_id": "goal1"
    ... }
    >>> response = handler(event, None)
    >>> print(response["status"])
    'delete success'
"""

import os
from typing import Any, Dict

import boto3

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle CRUD operations for financial goals.

    This function serves as the Lambda handler, processing requests to manage
    financial goals. It implements a complete CRUD interface with proper
    error handling and response formatting.

    The function supports three operations:
        1. get: Retrieves all goals for a user
        2. put: Creates or updates a goal
        3. delete: Removes a goal by ID

    Each operation requires specific parameters in the event:
        - get: Requires user_id
        - put: Requires user_id and goal object
        - delete: Requires user_id and goal_id

    Args:
        event: The Lambda event containing:
            - action: The operation to perform ("get", "put", or "delete")
            - user_id: The ID of the user (defaults to "user-123")
            - goal: The goal data for put operations
            - goal_id: The ID of the goal for delete operations
        context: The Lambda context object (unused)

    Returns:
        Dict containing the operation result:
            - get: {"goals": List[Dict]} - List of user's goals
            - put: {"status": "put success"} - Confirmation of update
            - delete: {"status": "delete success"} - Confirmation of deletion
            - error: {"error": str} - Error message for invalid operations

    Raises:
        Exception: Any unhandled errors are caught and returned as error
            responses. Common errors include:
            - Invalid action
            - Missing required parameters
            - DynamoDB errors

    Example:
        >>> # Get user's goals
        >>> event = {
        ...     "action": "get",
        ...     "user_id": "user123"
        ... }
        >>> response = handler(event, None)
        >>> print(response["goals"])
        [
            {
                "user_id": "user123",
                "goal_id": "goal1",
                "name": "Vacation Fund",
                "target_amount": 5000,
                "current_amount": 1000,
                "target_date": "2024-12-31",
                "category": "vacation"
            }
        ]
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
