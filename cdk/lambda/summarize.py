"""Lambda function to summarize financial tool responses.

This module provides a serverless function that generates natural language
summaries of financial data using Amazon Bedrock's Claude model. It can
summarize data from multiple sources:
    - Subscription information
    - Available financial products
    - Financial goals and progress

The function supports two modes of operation:
    1. Direct data summarization: Takes pre-fetched data and generates a summary
    2. User-based summarization: Fetches all data for a user and generates a summary

The summarization process:
    1. Collects data from various sources (direct or via Lambda invocation)
    2. Formats the data into a structured prompt for Claude
    3. Generates a natural language summary
    4. Returns the summary with appropriate status codes

The function is designed to be deployed as an AWS Lambda and can be invoked
via API Gateway or directly from other AWS services.

Example:
    >>> # Direct data summarization
    >>> event = {
    ...     "subscriptions": [
    ...         {"name": "Netflix", "amount": 15.99, "frequency": "monthly"}
    ...     ],
    ...     "goals": [
    ...         {"name": "Vacation", "current_amount": 1000, "target_amount": 5000}
    ...     ]
    ... }
    >>> response = handler(event, None)
    >>> print(json.loads(response["body"]))
    "You have one monthly subscription to Netflix at $15.99..."

    >>> # User-based summarization
    >>> event = {"user_id": "user123"}
    >>> response = handler(event, None)
    >>> print(json.loads(response["body"]))
    "Here's a summary of your financial situation..."
"""

import json
from typing import Any, Dict, List, Optional

import boto3

# Initialize AWS clients
bedrock = boto3.client("bedrock-runtime")
lambda_client = boto3.client("lambda")


def invoke_function(function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke another Lambda function and process its response.

    This function is used to fetch data from other Lambda functions in the
    system, such as subscriptions, products, or goals. It handles the
    invocation and response parsing, including error handling.

    Args:
        function_name: The name of the Lambda function to invoke. This should
            be one of:
            - "subscriptions": For fetching user's subscriptions
            - "products": For fetching available financial products
            - "goals": For fetching user's financial goals
        payload: The payload to send to the function. The structure varies by
            function:
            - subscriptions: {"user_id": str}
            - products: {} (no parameters required)
            - goals: {"user_id": str}

    Returns:
        Dict[str, Any]: The parsed response from the invoked function. The
            structure varies by function type, but typically includes:
            - statusCode: HTTP status code
            - body: The function's response data

    Raises:
        Exception: If there's an error invoking the function or parsing
            its response.

    Example:
        >>> response = invoke_function("subscriptions", {"user_id": "user123"})
        >>> print(response["statusCode"])
        200
        >>> print(response["body"])
        [{"name": "Netflix", "amount": 15.99, ...}]
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
    """Generate a structured prompt for Claude to summarize financial data.

    This function creates a well-formatted prompt that guides Claude to generate
    a natural language summary of the provided financial data. The prompt:
        1. Introduces the summarization task
        2. Presents each data type in a clear, structured format
        3. Includes specific formatting for each data type
        4. Requests a concise but informative summary

    The prompt is designed to help Claude understand:
        - The context of the financial data
        - The relationships between different data types
        - The key insights to highlight
        - The desired tone and style of the summary

    Args:
        subscriptions: Optional list of subscription data. Each subscription
            should have:
            - name: Subscription service name
            - amount: Monthly/annual cost
            - frequency: Payment frequency
            - category: Subscription category
        products: Optional list of financial product data. Each product
            should have:
            - name: Product name
            - description: Product description
            - interest_rate: Annual interest rate
            - term_years: Product term in years
        goals: Optional list of financial goal data. Each goal should have:
            - name: Goal name
            - current_amount: Current saved amount
            - target_amount: Target amount
            - target_date: Target completion date

    Returns:
        str: A structured prompt string for Claude that includes:
            - Introduction to the summarization task
            - Formatted lists of each data type
            - Instructions for the summary style
            - Request for key insights

    Example:
        >>> prompt = get_summary_prompt(
        ...     subscriptions=[
        ...         {
        ...             "name": "Netflix",
        ...             "amount": 15.99,
        ...             "frequency": "monthly",
        ...             "category": "Entertainment"
        ...         }
        ...     ],
        ...     goals=[
        ...         {
        ...             "name": "Vacation",
        ...             "current_amount": 1000,
        ...             "target_amount": 5000,
        ...             "target_date": "2024-12-31"
        ...         }
        ...     ]
        ... )
        >>> print(prompt)
        Please provide a concise summary of the following financial data:
        ...
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

    This function serves as the Lambda handler, processing requests to generate
    natural language summaries of financial data. It supports two modes:
        1. User-based summarization: Fetches all data for a specific user
        2. Direct summarization: Uses pre-fetched data from the event

    The function implements a complete summarization pipeline:
        1. Data collection (direct or via Lambda invocation)
        2. Prompt generation for Claude
        3. Summary generation
        4. Response formatting

    The function handles various error cases:
        - Invalid user ID
        - Missing or malformed data
        - Function invocation errors
        - Summary generation errors

    Args:
        event: The Lambda event containing either:
            - user_id: ID of the user to summarize data for
            OR
            - subscriptions: List of subscription data
            - products: List of product data
            - goals: List of goal data
        context: The Lambda context object (unused)

    Returns:
        Dict[str, Any]: An HTTP response with:
            - statusCode: HTTP status code (200 for success, 500 for errors)
            - body: Either the generated summary or an error message

    Example:
        >>> # User-based summarization
        >>> event = {"user_id": "user123"}
        >>> response = handler(event, None)
        >>> print(response["statusCode"])
        200
        >>> print(response["body"])
        "Here's a summary of your financial situation..."

        >>> # Direct summarization
        >>> event = {
        ...     "subscriptions": [
        ...         {"name": "Netflix", "amount": 15.99, ...}
        ...     ]
        ... }
        >>> response = handler(event, None)
        >>> print(response["statusCode"])
        200
        >>> print(response["body"])
        "You have one monthly subscription..."

    Raises:
        Exception: Any unhandled errors are caught and returned as 500
            responses with error details.
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
