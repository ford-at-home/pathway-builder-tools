"""Script to seed the function catalog table with initial data.

This script populates the function catalog DynamoDB table with metadata about
available functions, including their descriptions and example prompts.
"""

import os
from typing import Dict, List

import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "function_catalog"))

# Function catalog data
FUNCTIONS: List[Dict] = [
    {
        "function_id": "get_subscriptions",
        "title": "Get User Subscriptions",
        "tool_title": "Subscription Manager",
        "description": (
            "Retrieves all active subscriptions for a user, including "
            "subscription name, amount, frequency, and category."
        ),
        "category": "subscriptions",
        "example_prompts": [
            "Show me my subscriptions",
            "What subscriptions do I have?",
            "List all my monthly subscriptions",
        ],
    },
    {
        "function_id": "get_products",
        "title": "Get Financial Products",
        "tool_title": "Financial Products Catalog",
        "description": (
            "Retrieves available financial products (e.g. loans) with details "
            "about interest rates, terms, and amount ranges."
        ),
        "category": "products",
        "example_prompts": [
            "Show me available financial products",
            "What loans are available?",
            "List all financial products",
        ],
    },
    {
        "function_id": "manage_goals",
        "title": "Manage Financial Goals",
        "tool_title": "Financial Goals Manager",
        "description": (
            "Create, read, update, and delete financial goals. Track progress "
            "towards savings targets, emergency funds, and other financial "
            "objectives."
        ),
        "category": "goals",
        "example_prompts": [
            "Show me my financial goals",
            "Create a new savings goal",
            "Update my emergency fund goal",
            "Delete my vacation fund goal",
        ],
    },
    {
        "function_id": "summarize",
        "title": "Summarize Financial Data",
        "tool_title": "Financial Summary Generator",
        "description": (
            "Generates a natural language summary of a user's financial data, "
            "including subscriptions, available products, and financial goals. "
            "Highlights key insights and patterns."
        ),
        "category": "summary",
        "example_prompts": [
            "Summarize my financial situation",
            "Give me an overview of my finances",
            "What's my current financial status?",
            "Show me a summary of my subscriptions and goals",
        ],
    },
]


def seed_function_catalog() -> None:
    """Seed the function catalog table with initial data."""
    for function in FUNCTIONS:
        table.put_item(Item=function)
        print(f"Added function: {function['title']}")


if __name__ == "__main__":
    seed_function_catalog()
