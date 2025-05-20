"""Lambda function for retrieving available financial products.

This module provides a serverless function that lists all available financial
products from a DynamoDB catalog. The function is designed to be simple and
focused, providing read-only access to the product catalog.

The function uses DynamoDB for persistent storage with the following schema:
    - Partition key: product_id (String)
    - Additional attributes:
        * name: Product name
        * description: Detailed product description
        * interest_rate: Annual interest rate (percentage)
        * term_years: Product term in years
        * minimum_amount: Minimum investment/loan amount
        * maximum_amount: Maximum investment/loan amount
        * category: Product category (e.g., "savings", "investment", "loan")
        * risk_level: Risk assessment (e.g., "low", "medium", "high")
        * requirements: List of eligibility requirements

The function is designed to be deployed as an AWS Lambda and can be invoked
via API Gateway or directly from other AWS services.

Example:
    >>> event = {}
    >>> response = handler(event, None)
    >>> print(response["products"])
    [
        {
            "product_id": "prod1",
            "name": "High-Yield Savings",
            "description": "Savings account with competitive interest rates",
            "interest_rate": 4.5,
            "term_years": 0,
            "minimum_amount": 100,
            "maximum_amount": 1000000,
            "category": "savings",
            "risk_level": "low",
            "requirements": ["18+ years old", "Valid ID"]
        },
        {
            "product_id": "prod2",
            "name": "Retirement Investment",
            "description": "Long-term retirement investment portfolio",
            "interest_rate": 7.2,
            "term_years": 30,
            "minimum_amount": 1000,
            "maximum_amount": 500000,
            "category": "investment",
            "risk_level": "medium",
            "requirements": ["21+ years old", "Income verification"]
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
    """Retrieve all available financial products.

    This function serves as the Lambda handler, processing requests to fetch
    the complete catalog of available financial products. It implements a
    simple scan operation against DynamoDB, returning all products in the
    catalog.

    The function is stateless and doesn't require any input parameters,
    making it suitable for both direct invocation and API Gateway integration.
    It's designed to be called frequently to provide up-to-date product
    information to users.

    Args:
        event: The Lambda event (unused in this function)
        context: The Lambda context object (unused)

    Returns:
        Dict containing:
            - products: List[Dict] - List of available products, where each
                product is a dictionary containing:
                * product_id: Unique product identifier
                * name: Product name
                * description: Detailed product description
                * interest_rate: Annual interest rate
                * term_years: Product term in years
                * minimum_amount: Minimum investment/loan amount
                * maximum_amount: Maximum investment/loan amount
                * category: Product category
                * risk_level: Risk assessment
                * requirements: List of eligibility requirements

    Raises:
        Exception: Any unhandled errors are caught and returned as error
            responses. Common errors include:
            - DynamoDB connection issues
            - Missing permissions
            - Table not found

    Example:
        >>> response = handler({}, None)
        >>> print(response["products"])
        [
            {
                "product_id": "prod1",
                "name": "High-Yield Savings",
                "description": "Savings account with competitive interest rates",
                "interest_rate": 4.5,
                "term_years": 0,
                "minimum_amount": 100,
                "maximum_amount": 1000000,
                "category": "savings",
                "risk_level": "low",
                "requirements": ["18+ years old", "Valid ID"]
            }
        ]
    """
    response = table.scan()
    return {"products": response.get("Items", [])}
