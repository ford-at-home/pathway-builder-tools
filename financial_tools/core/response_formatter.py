"""Response formatter module for formatting function responses."""

import json
from typing import Any, Dict


def format_response(response: Dict[str, Any], function_id: str) -> str:
    """Format the function response for display.

    For get_subscriptions, get_products, and get_goals, the function checks for
    a key (e.g. 'subscriptions', 'products', or 'goals') and falls back to
    'Items' if not present. For put_goal and delete_goal, a success message is
    printed. For any other function, the raw JSON is returned.

    Args:
        response: The response from the function execution
        function_id: The ID of the function that was executed

    Returns:
        Formatted string representation of the response
    """
    if function_id == "get_subscriptions":
        items = response.get("subscriptions") or response.get("Items", [])
        if not items:
            return "No subscriptions found."
        return "\nSubscriptions:\n" + "\n".join(
            f"- {item['name']}: ${item['amount']} ({item['frequency']})"
            for item in items
        )
    elif function_id == "get_products":
        items = response.get("products") or response.get("Items", [])
        if not items:
            return "No products found."
        return "\nAvailable Products:\n" + "\n".join(
            f"- {item['name']}: {item['description']}\n"
            f"  Amount Range: ${item['min_amount']} - ${item['max_amount']}"
            for item in items
        )
    elif function_id.startswith("get_goals") or function_id == "manage_goals":
        items = response.get("goals") or response.get("Items", [])
        if not items:
            return "No goals found."
        return "\nFinancial Goals:\n" + "\n".join(
            f"- {item['name']}: ${item['current_amount']} / "
            f"${item['target_amount']} (Due: {item['due_date']})"
            for item in items
        )
    elif function_id.startswith(("put_goal", "delete_goal")):
        return f"Operation successful: {response.get('message', 'No message')}"
    return json.dumps(response, indent=2, default=str)
