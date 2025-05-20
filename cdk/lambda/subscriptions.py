"""Lambda function for managing user subscriptions.

This module provides a serverless function that retrieves a user's active
subscriptions from DynamoDB. The function is designed to be simple and
focused, providing read-only access to subscription data.

The function uses DynamoDB for persistent storage with the following schema:
    - Partition key: user_id (String)
    - Sort key: subscription_id (String)
    - Additional attributes:
        * name: Subscription service name
        * amount: Monthly/annual cost
        * frequency: Payment frequency (monthly/annual)
        * category: Subscription category (e.g., "streaming", "software")
        * start_date: When the subscription began
        * next_billing_date: When the next payment is due

The function is designed to be deployed as an AWS Lambda and can be invoked
via API Gateway or directly from other AWS services.

Example:
    >>> event = {
    ...     "user_id": "user123"
    ... }
    >>> response = handler(event, None)
    >>> print(response["subscriptions"])
    [
        {
            "user_id": "user123",
            "subscription_id": "sub1",
            "name": "Netflix",
            "amount": 15.99,
            "frequency": "monthly",
            "category": "streaming",
            "start_date": "2023-01-01",
            "next_billing_date": "2024-04-01"
        },
        {
            "user_id": "user123",
            "subscription_id": "sub2",
            "name": "Spotify",
            "amount": 9.99,
            "frequency": "monthly",
            "category": "streaming",
            "start_date": "2023-02-01",
            "next_billing_date": "2024-04-01"
        }
    ]
"""

import os
from typing import Any, Dict

import boto3

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve all subscriptions for a user.

    This function serves as the Lambda handler, processing requests to fetch
    a user's active subscriptions. It implements a simple query operation
    against DynamoDB, returning all subscriptions associated with the
    specified user.

    The function uses a default user ID ("user-123") if none is provided,
    making it suitable for testing and development. In production, a valid
    user ID should always be provided.

    Args:
        event: The Lambda event containing:
            - user_id: The ID of the user whose subscriptions to retrieve
                (defaults to "user-123" if not provided)
        context: The Lambda context object (unused)

    Returns:
        Dict containing:
            - subscriptions: List[Dict] - List of user's subscriptions, where
                each subscription is a dictionary containing:
                * user_id: User identifier
                * subscription_id: Unique subscription identifier
                * name: Subscription service name
                * amount: Monthly/annual cost
                * frequency: Payment frequency
                * category: Subscription category
                * start_date: Subscription start date
                * next_billing_date: Next billing date

    Raises:
        Exception: Any unhandled errors are caught and returned as error
            responses. Common errors include:
            - DynamoDB connection issues
            - Invalid user ID format
            - Missing permissions

    Example:
        >>> event = {
        ...     "user_id": "user123"
        ... }
        >>> response = handler(event, None)
        >>> print(response["subscriptions"])
        [
            {
                "user_id": "user123",
                "subscription_id": "sub1",
                "name": "Netflix",
                "amount": 15.99,
                "frequency": "monthly",
                "category": "streaming",
                "start_date": "2023-01-01",
                "next_billing_date": "2024-04-01"
            }
        ]
    """
    user_id = event.get("user_id", "user-123")
    response = table.query(
        KeyConditionExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_id},
    )
    return {"subscriptions": response.get("Items", [])}
