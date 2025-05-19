from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("function_catalog")

functions = [
    {
        "function_id": "get_subscriptions",
        "title": "Get User Subscriptions",
        "tool_title": "Subscription Manager",
        "description": "Retrieves all active subscriptions for a user, including subscription name, amount, frequency, and category.",
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
        "tool_title": "Product Catalog",
        "description": "Retrieves available financial products including loans and tools, with details like interest rates, terms, and amount ranges.",
        "category": "products",
        "example_prompts": [
            "What financial products are available?",
            "Show me the loan options",
            "What are the current mortgage rates?",
        ],
    },
    {
        "function_id": "manage_goals",
        "title": "Manage Financial Goals",
        "tool_title": "Goal Tracker",
        "description": "Create, read, update, and delete financial goals. Track progress towards savings targets, emergency funds, and other financial objectives.",
        "category": "goals",
        "example_prompts": [
            "Create a new savings goal",
            "Update my vacation fund progress",
            "Show me my financial goals",
            "Delete my emergency fund goal",
        ],
    },
]

for item in functions:
    table.put_item(Item=item)
