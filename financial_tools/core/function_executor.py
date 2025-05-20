"""Function executor module for executing Lambda functions.

This module provides the core functionality for executing financial functions through
AWS Lambda. It maintains a mapping of function IDs to their corresponding Lambda
function names and handles the execution of these functions with appropriate parameters.

The module supports several types of financial operations:
    - Subscription management (get_subscriptions)
    - Financial product queries (get_products)
    - Goal management (get_goals, put_goal, delete_goal)

Each function execution is handled through AWS Lambda, with proper error handling
and response formatting. The module ensures that functions are called with the
correct parameters and that responses are properly processed.

Example:
    >>> from financial_tools.core.function_executor import execute_function
    >>> result = execute_function("get_subscriptions", {"user_id": "user123"})
    >>> print(f"Found {len(result.get('subscriptions', []))} subscriptions")
"""

import json
from typing import Dict, Any

import boto3

# Initialize AWS client for Lambda function invocation
lambda_client = boto3.client("lambda")

# Map function IDs to their Lambda function names
FUNCTION_MAP = {
    "get_subscriptions": "subscriptions",  # Get user's subscription list
    "get_products": "products",           # Get available financial products
    "get_goals": "goals",                 # Get user's financial goals
    "put_goal": "goals",                  # Add or update a financial goal
    "delete_goal": "goals",               # Delete a financial goal
    "manage_goals": "goals",              # General goal management
}

def execute_function(function_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the recommended function with the provided parameters.

    This function takes a function ID and parameters, maps the function ID to the
    appropriate Lambda function name, and executes the function with the given
    parameters. It handles special cases like goal management functions and
    ensures proper error handling.

    The function supports several operations:
    1. Subscription queries (get_subscriptions)
    2. Product listings (get_products)
    3. Goal management (get_goals, put_goal, delete_goal)
    4. General goal operations (manage_goals)

    Special handling is provided for goal-related functions:
    - manage_goals is mapped to get_goals with action="get"
    - Goal functions have their action parameter set based on the function ID

    Args:
        function_id: The ID of the function to execute. Must be one of the keys
            in FUNCTION_MAP. This determines which Lambda function will be called.
        parameters: The parameters to pass to the function. The required parameters
            vary by function:
            - get_subscriptions: {"user_id": str}
            - get_products: {} (no parameters required)
            - get_goals: {"user_id": str}
            - put_goal: {"user_id": str, "goal": dict}
            - delete_goal: {"user_id": str, "goal_id": str}

    Returns:
        Dict containing the function execution response. The structure varies by
        function:
        - get_subscriptions: {"subscriptions": list}
        - get_products: {"products": list}
        - get_goals: {"goals": list}
        - put_goal: {"message": str, "goal": dict}
        - delete_goal: {"message": str}

    Raises:
        ValueError: If the function_id is not recognized (not in FUNCTION_MAP)
        Exception: If there's an error executing the function, including:
            - AWS Lambda invocation errors
            - Invalid parameter errors
            - Function execution errors

    Example:
        >>> # Get user's subscriptions
        >>> result = execute_function("get_subscriptions", {"user_id": "user123"})
        >>> print(f"Found {len(result['subscriptions'])} subscriptions")
        
        >>> # Add a new goal
        >>> goal = {
        ...     "name": "Vacation Fund",
        ...     "target_amount": 5000,
        ...     "due_date": "2024-12-31"
        ... }
        >>> result = execute_function("put_goal", {"user_id": "user123", "goal": goal})
        >>> print(result["message"])
    """
    try:
        # Map manage_goals to get_goals for read actions
        if function_id == "manage_goals":
            function_id = "get_goals"
            parameters["action"] = "get"

        # Validate function ID
        if function_id not in FUNCTION_MAP:
            raise ValueError(f"Unknown function ID: {function_id}")

        # Get the Lambda function name
        lambda_name = FUNCTION_MAP[function_id]

        # Set action based on function ID for goal operations
        if function_id.startswith("get_goals"):
            parameters["action"] = "get"
        elif function_id.startswith("put_goal"):
            parameters["action"] = "put"
        elif function_id.startswith("delete_goal"):
            parameters["action"] = "delete"

        # Execute the Lambda function
        response = lambda_client.invoke(
            FunctionName=lambda_name,
            Payload=json.dumps(parameters)
        )
        payload = json.loads(response["Payload"].read())
        
        # Handle error messages
        if "errorMessage" in payload:
            raise Exception(f"Error from {function_id}: {payload['errorMessage']}")
            
        return payload
    except Exception as e:
        raise Exception(f"Error executing function {function_id}: {str(e)}")
