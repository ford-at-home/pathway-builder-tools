"""Response formatter module for formatting function responses.

This module provides functionality for formatting responses from various financial
functions into user-friendly text output. It handles different types of responses
and formats them appropriately based on the function that generated them.

The module supports formatting for:
    - Subscription lists (get_subscriptions)
    - Financial product listings (get_products)
    - Goal management responses (get_goals, put_goal, delete_goal)
    - Generic responses for other functions

Each function type has its own formatting rules:
    - Subscriptions: Name, amount, and frequency
    - Products: Name, description, and amount range
    - Goals: Name, current amount, target amount, and due date
    - Operations: Success messages with details

Example:
    >>> from financial_tools.core.response_formatter import format_response
    >>> response = {
    ...     "subscriptions": [
    ...         {"name": "Netflix", "amount": 15.99, "frequency": "monthly"}
    ...     ]
    ... }
    >>> print(format_response(response, "get_subscriptions"))
    Subscriptions:
    - Netflix: $15.99 (monthly)
"""

import json
from typing import Dict, Any


def format_response(response: Dict[str, Any], function_id: str) -> str:
    """Format the function response for display.

    This function takes a response dictionary and a function ID, and formats the
    response into a user-friendly string based on the type of function that
    generated it. It handles various response formats and provides appropriate
    formatting for each function type.

    The function supports several types of responses:
    1. Subscription lists (get_subscriptions)
       - Formats each subscription with name, amount, and frequency
       - Handles empty subscription lists
    2. Product listings (get_products)
       - Formats each product with name, description, and amount range
       - Handles empty product lists
    3. Goal management (get_goals, put_goal, delete_goal)
       - Formats goals with name, amounts, and due date
       - Formats operation success messages
    4. Generic responses
       - Returns pretty-printed JSON for unknown function types

    The function looks for data in multiple possible keys:
    - Primary keys (e.g., 'subscriptions', 'products', 'goals')
    - Fallback key ('Items') for DynamoDB responses
    - Operation messages for put/delete operations

    Args:
        response: The response dictionary from the function execution. The structure
            varies by function type:
            - get_subscriptions: {"subscriptions": list} or {"Items": list}
            - get_products: {"products": list} or {"Items": list}
            - get_goals: {"goals": list} or {"Items": list}
            - put_goal/delete_goal: {"message": str, ...}
        function_id: The ID of the function that generated the response. This
            determines how the response should be formatted. Supported values:
            - "get_subscriptions"
            - "get_products"
            - "get_goals"
            - "put_goal"
            - "delete_goal"
            - "manage_goals"

    Returns:
        A formatted string representation of the response. The format varies by
        function type:
        - Subscriptions: "Subscriptions:\n- Name: $Amount (frequency)"
        - Products: "Available Products:\n- Name: Description\n  Amount Range: $min - $max"
        - Goals: "Financial Goals:\n- Name: $current / $target (Due: date)"
        - Operations: "Operation successful: message"
        - Other: Pretty-printed JSON

    Example:
        >>> # Format subscription list
        >>> response = {
        ...     "subscriptions": [
        ...         {"name": "Netflix", "amount": 15.99, "frequency": "monthly"},
        ...         {"name": "Spotify", "amount": 9.99, "frequency": "monthly"}
        ...     ]
        ... }
        >>> print(format_response(response, "get_subscriptions"))
        Subscriptions:
        - Netflix: $15.99 (monthly)
        - Spotify: $9.99 (monthly)

        >>> # Format product list
        >>> response = {
        ...     "products": [
        ...         {
        ...             "name": "Savings Account",
        ...             "description": "High-yield savings",
        ...             "min_amount": 100,
        ...             "max_amount": 100000
        ...         }
        ...     ]
        ... }
        >>> print(format_response(response, "get_products"))
        Available Products:
        - Savings Account: High-yield savings
          Amount Range: $100 - $100000
    """
    if function_id == "get_subscriptions":
        # Format subscription list
        items = response.get("subscriptions") or response.get("Items", [])
        if not items:
            return "No subscriptions found."
        return "\nSubscriptions:\n" + "\n".join(
            f"- {item['name']}: ${item['amount']} ({item['frequency']})"
            for item in items
        )
    elif function_id == "get_products":
        # Format product list
        items = response.get("products") or response.get("Items", [])
        if not items:
            return "No products found."
        return "\nAvailable Products:\n" + "\n".join(
            f"- {item['name']}: {item['description']}\n"
            f"  Amount Range: ${item['min_amount']} - ${item['max_amount']}"
            for item in items
        )
    elif function_id.startswith("get_goals") or function_id == "manage_goals":
        # Format goal list
        items = response.get("goals") or response.get("Items", [])
        if not items:
            return "No goals found."
        return "\nFinancial Goals:\n" + "\n".join(
            f"- {item['name']}: ${item['current_amount']} / "
            f"${item['target_amount']} (Due: {item['due_date']})"
            for item in items
        )
    elif function_id.startswith(("put_goal", "delete_goal")):
        # Format operation success message
        return f"Operation successful: {response.get('message', 'No message')}"
    # Format generic response as JSON
    return json.dumps(response, indent=2, default=str)
