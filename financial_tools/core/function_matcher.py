"""Function matcher module for determining which function to call based on user input."""

import json
import sys
from typing import Any, Dict

import boto3

# Initialize AWS client
lambda_client = boto3.client("lambda")


def call_function_matcher(prompt: str, user_id: str = "test_user") -> Dict[str, Any]:
    """Call the function matcher Lambda to get a function recommendation.

    The response is parsed so that if a 'body' field is present (a JSON string),
    it is parsed and flattened (e.g. if 'matched_function' is present, the
    function_id, parameters, title, and description are returned at the top level).

    Args:
        prompt: The natural language prompt to process
        user_id: The user ID for the request

    Returns:
        Dict containing the function recommendation details

    Raises:
        Exception: If there's an error calling the function matcher or parsing the response
    """
    try:
        response = lambda_client.invoke(
            FunctionName="function_matcher",
            Payload=json.dumps({"prompt": prompt, "user_id": user_id}),
        )
        payload = json.loads(response["Payload"].read())

        # If the payload has a 'body' field, parse it
        if "body" in payload:
            try:
                body = json.loads(payload["body"])
                # If the function info is nested under 'matched_function', flatten it
                if "matched_function" in body:
                    matched = body["matched_function"]
                    return {
                        "function_id": matched.get("function_id"),
                        "parameters": body.get("parameters", {}),
                        "title": matched.get("title"),
                        "description": matched.get("description"),
                    }
                return body
            except json.JSONDecodeError as e:
                raise Exception(f"Error parsing body from function matcher: {str(e)}")

        if "errorMessage" in payload:
            raise Exception(f"Error from function matcher: {payload['errorMessage']}")

        return payload
    except Exception as e:
        raise Exception(f"Error calling function matcher: {str(e)}")
