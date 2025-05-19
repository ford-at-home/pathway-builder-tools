"""Function executor module for executing Lambda functions."""

import json
from typing import Any, Dict

import boto3

# Initialize AWS client
lambda_client = boto3.client("lambda")

# Map function IDs to their Lambda function names
FUNCTION_MAP = {
    "get_subscriptions": "subscriptions",
    "get_products": "products",
    "get_goals": "goals",
    "put_goal": "goals",
    "delete_goal": "goals",
    "manage_goals": "goals",
}


def execute_function(function_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the recommended function with the provided parameters.

    For example, if function_id is 'manage_goals', it is mapped to 'get_goals'
    (with action='get') for read actions. The function is invoked via the AWS
    Lambda client, and the response (or error) is returned.

    Args:
        function_id: The ID of the function to execute
        parameters: The parameters to pass to the function

    Returns:
        Dict containing the function execution response

    Raises:
        ValueError: If the function_id is unknown
        Exception: If there's an error executing the function
    """
    try:
        # Map manage_goals to get_goals for read actions
        if function_id == "manage_goals":
            function_id = "get_goals"
            parameters["action"] = "get"

        if function_id not in FUNCTION_MAP:
            raise ValueError(f"Unknown function ID: {function_id}")

        lambda_name = FUNCTION_MAP[function_id]

        # Set action based on function ID
        if function_id.startswith("get_goals"):
            parameters["action"] = "get"
        elif function_id.startswith("put_goal"):
            parameters["action"] = "put"
        elif function_id.startswith("delete_goal"):
            parameters["action"] = "delete"

        response = lambda_client.invoke(
            FunctionName=lambda_name, Payload=json.dumps(parameters)
        )
        payload = json.loads(response["Payload"].read())

        if "errorMessage" in payload:
            raise Exception(f"Error from {function_id}: {payload['errorMessage']}")

        return payload
    except Exception as e:
        raise Exception(f"Error executing function {function_id}: {str(e)}")
