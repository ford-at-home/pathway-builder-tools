"""Core functionality for matching user requests to financial tools.

This module provides the FunctionMatcher class which uses Amazon Bedrock's Claude
model to match natural language user requests to specific financial tool
functions. It also handles the execution of matched functions via AWS Lambda.
"""

import json
from typing import Any, Dict, Optional, TypedDict, Union

import boto3

from .logging_config import setup_logging

# Initialize AWS clients and logger
# We use Bedrock for natural language processing and Lambda for function execution
# The logger helps track matching and execution of functions
bedrock = boto3.client("bedrock-runtime")
lambda_client = boto3.client("lambda")
logger = setup_logging(__name__)


class FunctionMatchResult(TypedDict, total=False):
    """Type definition for function match results."""

    function_id: str
    statusCode: int
    body: str


class FunctionMatcher:
    """Matches user requests to financial tool functions.

    This class uses Amazon Bedrock's Claude model to understand natural language
    requests and match them to specific financial tool functions. It also handles
    the execution of matched functions via AWS Lambda.
    """

    def __init__(self) -> None:
        """Initialize the function matcher."""
        # Set up logging for this instance
        # This helps track matching and execution of functions
        self.logger = logger

    def match_function(self, prompt: str) -> FunctionMatchResult:
        """Match a user prompt to a financial tool function.

        Args:
            prompt: The user's natural language request

        Returns:
            Dict containing either:
            - The matched function ID and parameters
            - An error response with statusCode
        """
        try:
            # Construct the prompt for Claude
            # This helps Claude understand how to match requests to functions
            system_prompt = (
                "You are a function matcher for a financial tools system. "
                "Your job is to analyze user requests and determine which "
                "function should handle them.\n\n"
                "Available functions:\n"
                "1. get_subscriptions - For questions about recurring payments "
                "   and subscriptions\n"
                "2. get_products - For questions about available financial "
                "   products and tools\n"
                "3. get_goals - For questions about financial goals and "
                "   progress\n\n"
                "Rules for matching:\n"
                "1. Match similar phrases and variations (e.g., 'financial "
                "   tools', 'financial products', 'available loans' all match "
                "   to get_products)\n"
                "2. Consider the intent behind the request, not just exact "
                "   wording\n"
                "3. Choose the most specific function if multiple could handle "
                "   the request\n"
                "4. Return only the function ID of the most appropriate "
                "   function, or null if none match\n\n"
                "User request: {prompt}\n\n"
                "Function ID:"
            )

            # Call Claude via Bedrock
            # We use a low temperature (0.1) for consistent matching
            # and limit tokens since we only need the function ID
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(
                    {
                        "max_tokens": 100,  # We only need the function ID
                        "temperature": 0.1,  # Low temperature for consistent matching
                        "messages": [
                            {
                                "role": "user",
                                "content": system_prompt.format(prompt=prompt),
                            }
                        ],
                    }
                ),
            )

            # Parse the response
            # Strip whitespace and handle variations of "null"
            response_body = json.loads(response["body"].read())
            function_id = response_body["content"][0]["text"].strip().lower()

            # Handle cases where no function matches
            if function_id in ("null", "none", "no match"):
                self.logger.info(f"No function matched for prompt: {prompt}")
                return {"statusCode": 404, "body": "No matching function"}

            # Return the matched function
            # This will be used to execute the appropriate Lambda
            self.logger.info(f"Matched function {function_id} for prompt: {prompt}")
            return {"function_id": function_id}

        except Exception as e:
            # Log the full error for debugging
            # This helps track down issues with Bedrock or response parsing
            self.logger.error(f"Error matching function: {str(e)}", exc_info=True)
            return {"statusCode": 500, "body": str(e)}

    def execute_function(self, function_id: str) -> Dict[str, Any]:
        """Execute a financial tool function.

        Args:
            function_id: The ID of the function to execute

        Returns:
            The function's response data

        Raises:
            Exception: If the function execution fails
        """
        try:
            # Construct the Lambda payload
            # This includes the function ID and any parameters
            payload = json.dumps(
                {
                    "function_id": function_id,
                    "parameters": {},  # Add parameters if needed
                }
            )

            # Call the Lambda function
            # This executes the actual financial tool
            self.logger.info(f"Executing function {function_id}")
            response = lambda_client.invoke(
                FunctionName=f"FinancialToolsStack-{function_id}Function",
                Payload=payload,
            )

            # Parse and return the response
            # This includes the function's output data
            response_payload = json.loads(response["Payload"].read())
            if "FunctionError" in response:
                raise Exception(response_payload.get("errorMessage", "Unknown error"))

            return dict(response_payload)  # Ensure we return a Dict[str, Any]

        except Exception as e:
            # Log the full error for debugging
            # This helps track down issues with Lambda execution
            self.logger.error(f"Error executing function: {str(e)}", exc_info=True)
            raise
