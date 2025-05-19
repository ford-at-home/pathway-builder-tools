#!/usr/bin/env python3
"""Test script for function matcher and Lambda function execution."""

import argparse
import json
import sys
import unittest

import boto3

from financial_tools.core import (
    call_function_matcher,
    execute_function,
    format_response,
)

# Initialize AWS clients
lambda_client = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")


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
    try:
        match_result = call_function_matcher(args.prompt, args.user_id)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

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
    try:
        result = execute_function(
            match_result.get("function_id", "unknown"),
            match_result.get("parameters", {}),
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

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
