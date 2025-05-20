"""Function matcher module for determining which function to call based on user input.

This module provides the core functionality for matching natural language user requests
to appropriate financial functions. It uses AWS Lambda to invoke a function matcher
service that analyzes the user's input and returns a recommendation for which function
to execute.

The module handles:
    - Natural language processing of user requests
    - Mapping requests to appropriate financial functions
    - Parameter extraction for function execution
    - Error handling and response formatting

The function matcher uses Amazon Bedrock (Claude 3) to analyze user input and match
it to the most appropriate function from the function catalog. This allows users to
interact with the system using natural language while ensuring their requests are
properly routed to the correct financial functions.

Example:
    >>> from financial_tools.core.function_matcher import call_function_matcher
    >>> result = call_function_matcher("show my monthly subscriptions")
    >>> print(f"Matched function: {result['function_id']}")
    >>> print(f"Parameters: {result['parameters']}")
"""

import json
import sys
from typing import Dict, Any

import boto3

# Initialize AWS client for Lambda function invocation
lambda_client = boto3.client("lambda")

def call_function_matcher(prompt: str, user_id: str = "test_user") -> Dict[str, Any]:
    """Call the function matcher Lambda to get a function recommendation.

    This function sends a user's natural language prompt to the function matcher
    Lambda, which uses Amazon Bedrock (Claude 3) to analyze the request and determine
    the most appropriate function to execute. The response includes the function ID,
    parameters, title, and description.

    The function handles several response formats:
    1. Direct response with function details
    2. Response with a 'body' field containing JSON
    3. Response with nested 'matched_function' details

    Args:
        prompt: The natural language prompt to process. This should be a user's
            request in plain English, such as "show my subscriptions" or
            "add a new savings goal".
        user_id: The user ID for the request. This is used to provide context
            for the function matcher and is included in the parameters for
            user-specific functions. Defaults to "test_user".

    Returns:
        Dict containing the function recommendation details:
            - function_id: The ID of the matched function
            - parameters: Dict of parameters to pass to the function
            - title: Human-readable title of the function
            - description: Detailed description of what the function does

    Raises:
        Exception: If there's an error calling the function matcher or parsing
            the response. This includes:
            - AWS Lambda invocation errors
            - JSON parsing errors
            - Missing required fields in the response

    Example:
        >>> result = call_function_matcher("show my subscriptions", "user123")
        >>> print(f"Function: {result['function_id']}")
        >>> print(f"Parameters: {result['parameters']}")
    """
    try:
        # Invoke the function matcher Lambda
        response = lambda_client.invoke(
            FunctionName="function_matcher",
            Payload=json.dumps({"prompt": prompt, "user_id": user_id}),
        )
        payload = json.loads(response["Payload"].read())
        
        # Handle response with 'body' field
        if "body" in payload:
            try:
                body = json.loads(payload["body"])
                # Handle nested 'matched_function' structure
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
        
        # Handle error messages
        if "errorMessage" in payload:
            raise Exception(f"Error from function matcher: {payload['errorMessage']}")
        
        return payload
    except Exception as e:
        raise Exception(f"Error calling function matcher: {str(e)}")
