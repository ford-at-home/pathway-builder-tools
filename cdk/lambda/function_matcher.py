"""Lambda function for matching user prompts to available functions.

This module provides functionality to match natural language prompts to the most
appropriate function from a catalog of available functions using Amazon Bedrock's
Claude model.
"""

import json
import os
from typing import Dict, List, Optional

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
bedrock = boto3.client("bedrock-runtime")


def get_all_functions() -> List[Dict]:
    """Retrieve all functions from the catalog.

    Returns:
        List of dictionaries containing function details from the catalog.
    """
    response = table.scan()
    return response.get("Items", [])


def match_function(prompt: str, functions: List[Dict]) -> Optional[Dict]:
    """Use Amazon Bedrock to match the prompt to the most appropriate function.

    Args:
        prompt: The user's natural language request
        functions: List of available functions with their descriptions

    Returns:
        The matched function details if found, None otherwise
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
    """Handle the function matching request.

    Args:
        event: The Lambda event containing the user's prompt
        context: The Lambda context

    Returns:
        Dict containing the HTTP response with either the matched function
        or an error message
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
