"""Script to seed the products table with initial data.

This script populates the financial products DynamoDB table with sample product
data for testing purposes.
"""

import os
from typing import Dict, List

import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "financial_products"))

# Sample product data
PRODUCTS: List[Dict] = [
    {
        "product_id": "prod-001",
        "name": "Mortgage",
        "description": "30-year fixed rate mortgage",
        "min_amount": 50000,
        "max_amount": 500000,
        "interest_rate": 6.5,
        "term_years": 30,
        "type": "loan",
    },
    {
        "product_id": "prod-002",
        "name": "Auto Loan",
        "description": "5-year auto loan",
        "min_amount": 10000,
        "max_amount": 100000,
        "interest_rate": 5.5,
        "term_years": 5,
        "type": "loan",
    },
]


def seed_products() -> None:
    """Seed the products table with initial data."""
    for product in PRODUCTS:
        table.put_item(Item=product)
        print(f"Added product: {product['name']}")


if __name__ == "__main__":
    seed_products()
