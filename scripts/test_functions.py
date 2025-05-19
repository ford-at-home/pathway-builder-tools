#!/usr/bin/env python3
"""Test script for function matcher and Lambda function execution."""
import argparse
import json
import sys
import unittest
from typing import Any, Dict

import boto3

# Initialize AWS clients
lambda_client = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")


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
            except Exception as e:
                print(f"Error parsing body from function matcher: {str(e)}")
                sys.exit(1)
        if "errorMessage" in payload:
            print(f"Error from function matcher: {payload['errorMessage']}")
            sys.exit(1)
        return payload
    except Exception as e:
        print(f"Error calling function matcher: {str(e)}")
        sys.exit(1)


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
    """
    try:
        # Map function IDs to their Lambda function names
        function_map = {
            "get_subscriptions": "subscriptions",
            "get_products": "products",
            "get_goals": "goals",
            "put_goal": "goals",
            "delete_goal": "goals",
            "manage_goals": "goals",
        }

        # Map manage_goals to get_goals for read actions
        if function_id == "manage_goals":
            function_id = "get_goals"
            parameters["action"] = "get"

        if function_id not in function_map:
            print(f"Unknown function ID: {function_id}")
            sys.exit(1)

        lambda_name = function_map[function_id]

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
            print(f"Error from {function_id}: {payload['errorMessage']}")
            sys.exit(1)
        return payload
    except Exception as e:
        print(f"Error executing function {function_id}: {str(e)}")
        sys.exit(1)


def format_response(response: Dict[str, Any], function_id: str) -> str:
    """Format the function response for display.

    For get_subscriptions, get_products, and get_goals, the function checks for
    a key (e.g. 'subscriptions', 'products', or 'goals') and falls back to
    'Items' if not present. For put_goal and delete_goal, a success message is
    printed. For any other function, the raw JSON is returned.

    Args:
        response: The response from the function execution
        function_id: The ID of the function that was executed

    Returns:
        Formatted string representation of the response
    """
    if function_id == "get_subscriptions":
        items = response.get("subscriptions") or response.get("Items", [])
        if not items:
            return "No subscriptions found."
        return "\nSubscriptions:\n" + "\n".join(
            f"- {item['name']}: ${item['amount']} ({item['frequency']})"
            for item in items
        )
    elif function_id == "get_products":
        items = response.get("products") or response.get("Items", [])
        if not items:
            return "No products found."
        return "\nAvailable Products:\n" + "\n".join(
            f"- {item['name']}: {item['description']}\n"
            f"  Amount Range: ${item['min_amount']} - ${item['max_amount']}"
            for item in items
        )
    elif function_id.startswith("get_goals") or function_id == "manage_goals":
        items = response.get("goals") or response.get("Items", [])
        if not items:
            return "No goals found."
        return "\nFinancial Goals:\n" + "\n".join(
            f"- {item['name']}: ${item['current_amount']} / "
            f"${item['target_amount']} (Due: {item['due_date']})"
            for item in items
        )
    elif function_id.startswith(("put_goal", "delete_goal")):
        return f"Operation successful: {response.get('message', 'No message')}"
    return json.dumps(response, indent=2, default=str)


def main() -> None:
    """Run the main script to process a prompt and execute functions."""
    parser = argparse.ArgumentParser(
        description="Test the function matcher and execute functions"
    )
    parser.add_argument("prompt", help="The natural language prompt to process")
    parser.add_argument(
        "--user-id",
        default="test_user",
        help="User ID for the request (default: test_user)",
    )
    parser.add_argument(
        "--skip-execution",
        action="store_true",
        help="Only show the function matcher response without executing",
    )

    args = parser.parse_args()

    # Step 1: Get function recommendation
    print("\n🤖 Processing your request...")
    match_result = call_function_matcher(args.prompt, args.user_id)

    print("\n📋 Function Matcher Recommendation:")
    print(
        f"Function: {match_result.get('title', match_result.get('function_id', 'unknown'))}"
    )
    print(f"Description: {match_result.get('description', '(No description)')}")
    print(f"Parameters: {json.dumps(match_result.get('parameters', {}), indent=2)}")

    if args.skip_execution:
        return

    # Step 2: Execute the recommended function
    print("\n⚡ Executing function...")
    result = execute_function(
        match_result.get("function_id", "unknown"),
        match_result.get("parameters", {}),
    )

    # Debug: Print the raw Lambda response
    print("\n🐞 Raw Lambda Response:")
    print(json.dumps(result, indent=2, default=str))

    # Step 3: Format and display the result
    print("\n📊 Result:")
    print(format_response(result, match_result["function_id"]))


class TestFunctionMatcher(unittest.TestCase):
    """Test cases for the function matcher."""

    def test_subscription_query(self) -> None:
        """Test that subscription-related queries return the correct function ID."""
        test_cases = [
            ("Show me all my monthly subscriptions", "get_subscriptions"),
            ("What subscriptions do I have?", "get_subscriptions"),
            ("List my recurring payments", "get_subscriptions"),
        ]

        for prompt, expected_function in test_cases:
            with self.subTest(prompt=prompt):
                try:
                    result = call_function_matcher(prompt)
                    print(f"\nTesting prompt: {prompt}")
                    print(f"Expected function: {expected_function}")
                    print(f"Actual result: {json.dumps(result, indent=2)}")

                    self.assertEqual(
                        result.get("function_id"),
                        expected_function,
                        f"Function ID mismatch for prompt: {prompt}",
                    )
                    self.assertIn(
                        "parameters",
                        result,
                        f"Missing parameters in response for prompt: {prompt}",
                    )
                    self.assertIsInstance(
                        result["parameters"],
                        dict,
                        f"Parameters should be a dict for prompt: {prompt}",
                    )
                except Exception as e:
                    self.fail(f"Test failed for prompt '{prompt}' with error: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=["first-arg-is-ignored"], verbosity=2)
    else:
        main()
