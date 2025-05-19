import json

import pytest

from cdk.lambda_functions.subscriptions import handler


def test_get_subscriptions(dynamodb):
    """Test getting subscriptions for a user."""
    # Arrange
    table = dynamodb.Table("Subscriptions")
    test_user_id = "test_user_123"
    test_subscription = {
        "user_id": test_user_id,
        "subscription_id": "sub_123",
        "product_id": "prod_123",
        "status": "active",
        "amount": 29.99,
    }
    table.put_item(Item=test_subscription)

    # Act
    event = {"pathParameters": {"user_id": test_user_id}, "httpMethod": "GET"}
    response = handler(event, {})

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body) == 1
    assert body[0]["user_id"] == test_user_id
    assert body[0]["subscription_id"] == "sub_123"


def test_get_subscriptions_not_found(dynamodb):
    """Test getting subscriptions for a non-existent user."""
    # Act
    event = {"pathParameters": {"user_id": "non_existent_user"}, "httpMethod": "GET"}
    response = handler(event, {})

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body) == 0


def test_get_subscriptions_invalid_request():
    """Test getting subscriptions with invalid request."""
    # Act
    event = {
        "httpMethod": "GET"
        # Missing user_id
    }
    response = handler(event, {})

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
