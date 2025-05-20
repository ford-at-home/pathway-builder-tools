"""Lambda function to summarize financial tool responses.

This module provides a Lambda function that takes responses from the subscriptions,
products, and goals tools and generates a natural language summary using Amazon
Bedrock's Claude model.
"""

import json
from typing import Any, Dict, List, Optional

import boto3

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime")

# Initialize Lambda client for invoking other functions
lambda_client = boto3.client("lambda")


def invoke_function(function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke a Lambda function and return its response.

    Args:
        function_name: Name of the Lambda function to invoke
        payload: Payload to send to the function

    Returns:
        Dict containing the function's response
    """
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload),
    )
    return json.loads(response["Payload"].read())


def get_summary_prompt(
    subscriptions: Optional[List[Dict[str, Any]]] = None,
    products: Optional[List[Dict[str, Any]]] = None,
    goals: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Generate a prompt for Claude to summarize the financial data.

    Args:
        subscriptions: List of subscription data
        products: List of product data
        goals: List of goal data

    Returns:
        A prompt string for Claude
    """
    prompt_parts = ["Please provide a concise summary of the following financial data:"]

    if subscriptions:
        prompt_parts.append("\nSubscriptions:")
        for sub in subscriptions:
            prompt_parts.append(
                f"- {sub['name']}: ${sub['amount']} {sub['frequency']} "
                f"({sub['category']})"
            )

    if products:
        prompt_parts.append("\nAvailable Financial Products:")
        for prod in products:
            prompt_parts.append(
                f"- {prod['name']}: {prod['description']} "
                f"(Interest: {prod['interest_rate']}%, "
                f"Term: {prod['term_years']} years)"
            )

    if goals:
        prompt_parts.append("\nFinancial Goals:")
        for goal in goals:
            progress = (goal["current_amount"] / goal["target_amount"]) * 100
            prompt_parts.append(
                f"- {goal['name']}: ${goal['current_amount']} of "
                f"${goal['target_amount']} ({progress:.1f}%) "
                f"by {goal['target_date']}"
            )

    prompt_parts.append(
        "\nPlease provide a natural, conversational summary of this information, "
        "highlighting key insights and any notable patterns or concerns. "
        "Keep the summary concise but informative."
    )

    return "\n".join(prompt_parts)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle requests to summarize financial data.

    This function can be called in two ways:
    1. With a user_id to fetch and summarize all data for that user
    2. With pre-fetched data in the event payload

    Args:
        event: The event payload containing either:
            - user_id: ID of the user to summarize data for
            - OR pre-fetched data in subscriptions, products, and goals fields
        context: Lambda context object

    Returns:
        Dict containing:
            - summary: Natural language summary of the financial data
            - statusCode: HTTP status code
    """
    try:
        # Get data either from event or by invoking other functions
        if "user_id" in event:
            user_id = event["user_id"]
            subscriptions = invoke_function("subscriptions", {"user_id": user_id}).get(
                "body", []
            )
            products = invoke_function("products", {}).get("body", [])
            goals = invoke_function("goals", {"user_id": user_id}).get("body", [])
        else:
            subscriptions = event.get("subscriptions", [])
            products = event.get("products", [])
            goals = event.get("goals", [])

        # Generate summary using Claude
        prompt = get_summary_prompt(subscriptions, products, goals)
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                }
            ),
        )
        response_body = json.loads(response["body"].read())
        summary = response_body["content"][0]["text"]

        return {
            "statusCode": 200,
            "body": summary,
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error generating summary: {str(e)}",
        }
