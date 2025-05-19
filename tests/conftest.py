"""Test configuration and fixtures.

This module provides pytest fixtures for testing AWS services using moto,
including mocked AWS credentials, DynamoDB tables, and Lambda functions.
"""

import os
from typing import Generator

import boto3
import pytest
from moto import mock_dynamodb, mock_lambda


@pytest.fixture(scope="function")
def aws_credentials() -> None:
    """Set up mocked AWS credentials for testing.

    This fixture sets environment variables for AWS credentials to use with moto.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def dynamodb(aws_credentials) -> Generator:
    """Create and provide a mocked DynamoDB resource.

    This fixture creates test tables for subscriptions, products, and goals
    using moto's DynamoDB mock.

    Args:
        aws_credentials: Fixture that sets up AWS credentials

    Yields:
        A boto3 DynamoDB resource with test tables created
    """
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb")
        # Create test tables
        tables = [
            {
                "TableName": "Subscriptions",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
            },
            {
                "TableName": "Products",
                "KeySchema": [{"AttributeName": "product_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "product_id", "AttributeType": "S"}
                ],
            },
            {
                "TableName": "Goals",
                "KeySchema": [{"AttributeName": "goal_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "goal_id", "AttributeType": "S"}
                ],
            },
        ]
        for table in tables:
            dynamodb.create_table(**table)
        yield dynamodb


@pytest.fixture(scope="function")
def lambda_client(aws_credentials) -> Generator:
    """Create and provide a mocked Lambda client.

    This fixture provides a boto3 Lambda client using moto's Lambda mock.

    Args:
        aws_credentials: Fixture that sets up AWS credentials

    Yields:
        A boto3 Lambda client
    """
    with mock_lambda():
        yield boto3.client("lambda")
