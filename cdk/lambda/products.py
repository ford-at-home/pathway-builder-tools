"""Lambda function for retrieving available financial products.

This module provides functionality to list all available financial products
from the catalog.
"""

import os
from typing import Any, Dict

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve all available financial products.

    Args:
        event: The Lambda event (unused in this function)
        context: The Lambda context (unused in this function)

    Returns:
        Dict containing a list of available products
    """
    response = table.scan()
    return {"products": response.get("Items", [])}
