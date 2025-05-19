"""Lambda function for matching user requests to available functions.

This module provides functionality to match natural language prompts to the most
appropriate function from a catalog of available functions using Amazon Bedrock's
Claude model.
"""

import json
from typing import Any, Dict, List, Optional

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize AWS clients and logger
# We use Bedrock for the Claude model and DynamoDB for the function catalog
# The function catalog stores metadata about available functions
bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
logger = Logger()


def get_available_functions() -> List[Dict[str, Any]]:
    """Get list of available functions from DynamoDB.

    Returns:
        List of function definitions with their metadata.
    """
    # Scan the function catalog table to get all available functions
    # This includes function IDs, descriptions, and other metadata
    table = dynamodb.Table("function_catalog")
    response = table.scan()
    return response.get("Items", [])


def match_function(prompt: str, functions: list[Dict[str, Any]]) -> Optional[str]:
    """Match user prompt to most appropriate function using Claude.

    Args:
        prompt: The user's natural language request
        functions: List of available functions with metadata

    Returns:
        ID of the matched function, or None if no match
    """
    # Format functions list for the prompt
    # Each function is listed with its ID and description for Claude to analyze
    functions_text = "\n".join(
        f"- {f['function_id']}: {f['description']}" for f in functions
    )

    # Construct the prompt for Claude
    # The system prompt defines the rules for matching and provides context
    # We keep temperature low (0.1) for consistent matching behavior
    system_prompt = (
        "You are a function matcher. Your job is to analyze user requests and "
        "determine which function from the catalog is most appropriate.\n\n"
        "Rules:\n"
        "1. Match similar phrases and variations (e.g., 'financial tools', "
        "'financial products', 'available loans' all match to get_products)\n"
        "2. Consider the intent behind the request, not just exact wording\n"
        "3. Choose the most specific function if multiple could handle it\n"
        "4. Return ONLY the function_id of the most appropriate function, "
        "or null if none match\n\n"
        "Available functions:\n"
        f"{functions_text}\n\n"
        "User request: {prompt}\n"
        "Function ID:"
    )

    try:
        # Call Claude via Bedrock
        # We use Claude 3 Sonnet for its strong understanding of natural language
        # and ability to follow instructions precisely
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(
                {
                    "max_tokens": 100,  # Keep response short - we only need the function ID
                    "temperature": 0.1,  # Low temperature for consistent matching
                    "messages": [
                        {"role": "user", "content": system_prompt.format(prompt=prompt)}
                    ],
                }
            ),
        )

        # Parse response and clean up the function ID
        # Claude might return variations of "null" or include extra whitespace
        response_body = json.loads(response["body"].read())
        function_id = response_body["content"][0]["text"].strip().lower()

        # Handle variations of "null" responses
        # This ensures consistent handling of no-match cases
        if function_id in ("null", "none", "no match"):
            return None

        # Verify the function exists in our catalog
        # This is a safety check in case Claude returns an invalid function ID
        if not any(f["function_id"] == function_id for f in functions):
            logger.warning(f"Claude returned unknown function_id: {function_id}")
            return None

        return function_id

    except Exception as e:
        # Log the full error for debugging
        # This helps track down issues with Bedrock or response parsing
        logger.error(f"Error matching function: {str(e)}", exc_info=True)
        raise


@logger.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Handle Lambda invocation to match user request to function.

    Args:
        event: Lambda event containing the user's prompt
        context: Lambda context

    Returns:
        Dict containing either:
        - The matched function details
        - An error response with statusCode
    """
    try:
        # Get and validate user request from event
        # Strip whitespace to handle empty or whitespace-only prompts
        prompt = event.get("prompt", "").strip()
        if not prompt:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No prompt provided"}),
            }

        # Get available functions from the catalog
        # If no functions are available, return an error
        functions = get_available_functions()
        if not functions:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "No functions available"}),
            }

        # Match request to function using Claude
        # If no match is found, return a 404
        function_id = match_function(prompt, functions)
        if not function_id:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No matching function found"}),
            }

        # Get full function details from the catalog
        # This includes metadata like title and description
        function = next((f for f in functions if f["function_id"] == function_id), None)
        if not function:
            # This should never happen due to our earlier check,
            # but we include it as a safety measure
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Function not found in catalog"}),
            }

        # Return matched function with empty parameters
        # The parameters will be filled in by the calling function if needed
        return {
            "statusCode": 200,
            "body": json.dumps({"matched_function": function, "parameters": {}}),
        }

    except Exception as e:
        # Log the full error for debugging
        # This helps track down issues with the Lambda function
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
