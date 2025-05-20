"""Lambda function for matching user prompts to available functions.

This module provides a serverless function that matches natural language user
prompts to the most appropriate function from a catalog of available functions.
It uses Amazon Bedrock's Claude model for natural language understanding and
DynamoDB for function catalog storage.

The function implements a complete matching pipeline:
    1. Retrieves available functions from DynamoDB catalog
    2. Uses Claude to analyze the user's prompt
    3. Matches the prompt to the most appropriate function
    4. Returns the matched function details or an error

The matching process uses a carefully crafted system prompt that:
    - Explains the matching task to Claude
    - Provides the function catalog in a structured format
    - Requests only the function_id as output
    - Handles cases where no function matches

The function is designed to be deployed as an AWS Lambda and can be invoked
via API Gateway or directly from other AWS services.

Example:
    >>> event = {
    ...     "prompt": "show me my monthly subscriptions"
    ... }
    >>> response = handler(event, None)
    >>> print(json.loads(response["body"]))
    {
        "matched_function": {
            "function_id": "get_subscriptions",
            "title": "Get Subscriptions",
            "description": "Retrieve user's subscription list"
        },
        "confidence": "high"
    }
"""

import json
import os
from typing import Dict, List, Optional, Any

import boto3

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
bedrock = boto3.client("bedrock-runtime")


def get_all_functions() -> List[Dict]:
    """Retrieve all functions from the DynamoDB catalog.

    This function scans the DynamoDB table specified by the TABLE_NAME
    environment variable to retrieve all available functions. The table
    should contain function records with at least:
        - function_id: Unique identifier for the function
        - title: Human-readable function name
        - description: Detailed function description

    Returns:
        List[Dict]: A list of dictionaries containing function details.
            Each dictionary represents a function with its metadata.
            Example:
                [
                    {
                        "function_id": "get_subscriptions",
                        "title": "Get Subscriptions",
                        "description": "Retrieve user's subscription list"
                    },
                    ...
                ]

    Raises:
        Exception: If there's an error accessing DynamoDB or if the
            TABLE_NAME environment variable is not set.
    """
    response = table.scan()
    return response.get("Items", [])


def match_function(prompt: str, functions: List[Dict]) -> Optional[Dict]:
    """Use Amazon Bedrock's Claude model to match a prompt to a function.

    This function uses Claude to analyze a user's natural language prompt
    and determine which function from the catalog would best handle the
    request. It employs a carefully crafted system prompt that guides
    Claude to:
        1. Understand the available functions
        2. Analyze the user's request
        3. Select the most appropriate function
        4. Return only the function_id

    The matching process uses a low temperature (0.1) to ensure consistent
    and reliable function selection.

    Args:
        prompt: The user's natural language request to analyze. This should
            be a plain English description of what the user wants to do.
            Example: "show me my monthly subscriptions"
        functions: List of available functions with their metadata. Each
            function should have at least:
            - function_id: Unique identifier
            - title: Human-readable name
            - description: Detailed description

    Returns:
        Optional[Dict]: The matched function's details if a match is found,
            None if no function matches the prompt. The returned dictionary
            contains the complete function metadata.

    Example:
        >>> functions = [
        ...     {
        ...         "function_id": "get_subscriptions",
        ...         "title": "Get Subscriptions",
        ...         "description": "Retrieve user's subscription list"
        ...     }
        ... ]
        >>> match = match_function("show my subscriptions", functions)
        >>> print(match["function_id"])
        'get_subscriptions'

    Raises:
        Exception: If there's an error calling Bedrock or parsing the
            response.
    """
    # Create the prompt for Claude
    system_prompt = (
        "You are a function matching assistant. Your job is to analyze a user's "
        "request and determine which function would best handle it.\n"
        "You will be given a list of available functions with their descriptions. "
        "Return ONLY the function_id of the most appropriate function.\n"
        "If no function is appropriate, return null.\n\n"
        "Available functions:\n{functions}\n\n"
        "User request: {prompt}\n\n"
        "Return ONLY the function_id of the most appropriate function, or null "
        "if none match."
    )

    # Format the functions list for the prompt
    functions_str = json.dumps(functions, indent=2)
    prompt_text = system_prompt.format(functions=functions_str, prompt=prompt)

    # Call Bedrock with Claude
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt_text}],
            }
        ),
    )

    # Parse the response
    response_body = json.loads(response["body"].read())
    function_id = response_body["content"][0]["text"].strip()

    if function_id.lower() == "null":
        return None

    # Find and return the full function details
    return next((f for f in functions if f["function_id"] == function_id), None)


def handler(event: Dict, context: Any) -> Dict:
    """Handle the function matching request from API Gateway or direct invocation.

    This function serves as the Lambda handler, processing incoming requests
    to match user prompts to available functions. It implements a complete
    request handling pipeline:
        1. Validates the incoming request
        2. Retrieves the function catalog
        3. Matches the prompt to a function
        4. Returns a properly formatted HTTP response

    The function handles various error cases:
        - Missing prompt
        - Empty function catalog
        - No matching function
        - Internal errors

    Args:
        event: The Lambda event containing the request details. Expected format:
            {
                "prompt": str,  # The user's natural language request
                "user_id": str  # Optional user identifier
            }
        context: The Lambda context object (unused)

    Returns:
        Dict: An HTTP response with appropriate status code and body:
            - 200: Successful match
                {
                    "statusCode": 200,
                    "body": {
                        "matched_function": {
                            "function_id": str,
                            "title": str,
                            "description": str
                        },
                        "confidence": "high"
                    }
                }
            - 400: Missing prompt
            - 404: No functions or no match
            - 500: Internal error

    Example:
        >>> event = {
        ...     "prompt": "show my subscriptions",
        ...     "user_id": "user123"
        ... }
        >>> response = handler(event, None)
        >>> print(response["statusCode"])
        200
        >>> print(json.loads(response["body"])["matched_function"]["function_id"])
        'get_subscriptions'

    Raises:
        Exception: Any unhandled errors are caught and returned as 500
            responses with error details.
    """
    try:
        prompt = event.get("prompt")
        if not prompt:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No prompt provided"}),
            }

        # Get all available functions
        functions = get_all_functions()
        if not functions:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No functions available in catalog"}),
            }

        # Match the prompt to a function
        matched_function = match_function(prompt, functions)
        if not matched_function:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No matching function found"}),
            }

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "matched_function": matched_function,
                    "confidence": "high",  # We could add confidence scoring if needed
                }
            ),
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
