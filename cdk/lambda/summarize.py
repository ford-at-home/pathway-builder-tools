"""Lambda function for summarizing financial data using Claude.

This module provides a Lambda function that takes responses from various financial
tools (subscriptions, products, goals) and generates natural language summaries
using Amazon Bedrock's Claude model.
"""

import json
from typing import Any, Dict

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize AWS client and logger
# We use Bedrock for the Claude model to generate natural language summaries
# The logger helps track summarization requests and any errors
bedrock = boto3.client("bedrock-runtime")
logger = Logger()


def summarize_data(data: Dict[str, Any], function_id: str) -> str:
    """Summarize financial data using Claude.

    Args:
        data: The financial data to summarize
        function_id: The ID of the function that generated the data

    Returns:
        A natural language summary of the data
    """
    # Construct the prompt based on the function type
    # Each function type gets a specialized prompt that guides Claude
    # to summarize the data in a context-appropriate way
    if function_id == "get_subscriptions":
        # For subscriptions, focus on monthly costs and notable services
        system_prompt = (
            "You are a financial assistant. Summarize the user's subscription "
            "data in a friendly, conversational way. Include the total monthly "
            "cost and highlight any notable subscriptions.\n\n"
            "Data:\n{data}\n\n"
            "Summary:"
        )
    elif function_id == "get_products":
        # For products, group similar offerings and highlight key features
        system_prompt = (
            "You are a financial advisor. Summarize the available financial "
            "products in a helpful way. Group similar products and highlight "
            "key features that would be relevant to the user.\n\n"
            "Data:\n{data}\n\n"
            "Summary:"
        )
    elif function_id == "get_goals":
        # For goals, focus on progress and next steps
        system_prompt = (
            "You are a financial coach. Summarize the user's financial goals "
            "in an encouraging way. Include progress towards each goal and "
            "suggest next steps if appropriate.\n\n"
            "Data:\n{data}\n\n"
            "Summary:"
        )
    else:
        # Generic prompt for unknown function types
        system_prompt = (
            "You are a financial assistant. Summarize the following data in a "
            "clear, helpful way. Focus on the most important information and "
            "present it in a user-friendly format.\n\n"
            "Data:\n{data}\n\n"
            "Summary:"
        )

    try:
        # Call Claude via Bedrock
        # We use a higher temperature (0.7) for more natural summaries
        # and allow more tokens for detailed responses
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(
                {
                    "max_tokens": 500,  # Allow longer summaries for detailed data
                    "temperature": 0.7,  # Higher temperature for more natural language
                    "messages": [
                        {
                            "role": "user",
                            "content": system_prompt.format(
                                data=json.dumps(
                                    data, indent=2
                                )  # Pretty-print data for clarity
                            ),
                        }
                    ],
                }
            ),
        )

        # Parse and return the summary
        # Strip whitespace to clean up the response
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"].strip()

    except Exception as e:
        # Log the full error for debugging
        # This helps track down issues with Bedrock or response parsing
        logger.error(f"Error summarizing data: {str(e)}", exc_info=True)
        raise


@logger.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Handle Lambda invocation to summarize financial data.

    Args:
        event: Lambda event containing the data to summarize
        context: Lambda context

    Returns:
        Dict containing either:
        - The summarized data
        - An error response with statusCode
    """
    try:
        # Get and validate input data from event
        # The function_id helps determine how to summarize the data
        data = event.get("data", {})
        function_id = event.get("function_id", "")

        if not data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No data provided"}),
            }

        # Generate summary using Claude
        # The summary will be tailored to the type of data
        summary = summarize_data(data, function_id)

        # Return the summary in a consistent format
        # This makes it easy for clients to parse the response
        return {"statusCode": 200, "body": json.dumps({"summary": summary})}

    except Exception as e:
        # Log the full error for debugging
        # This helps track down issues with the Lambda function
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
