"""Tests for the function matcher module."""

import unittest
from unittest.mock import patch

from ..core.function_matcher import call_function_matcher


class TestFunctionMatcher(unittest.TestCase):
    """Test cases for the function matcher."""

    def test_match_subscriptions_request(self) -> None:
        """Test matching a subscription-related request."""
        with patch("boto3.client") as mock_boto3:
            # Mock the Lambda response
            mock_lambda = mock_boto3.return_value
            mock_lambda.invoke.return_value = {
                "StatusCode": 200,
                "Payload": b'{"function_id": "get_subscriptions", "parameters": {}}',
            }

            result = call_function_matcher("show my subscriptions")
            self.assertEqual(result["function_id"], "get_subscriptions")
            self.assertEqual(result["parameters"], {})

    def test_match_products_request(self) -> None:
        """Test matching a products-related request."""
        with patch("boto3.client") as mock_boto3:
            # Mock the Lambda response
            mock_lambda = mock_boto3.return_value
            mock_lambda.invoke.return_value = {
                "StatusCode": 200,
                "Payload": b'{"function_id": "get_products", "parameters": {}}',
            }

            result = call_function_matcher("what financial products are available")
            self.assertEqual(result["function_id"], "get_products")
            self.assertEqual(result["parameters"], {})

    def test_match_goals_request(self) -> None:
        """Test matching a goals-related request."""
        with patch("boto3.client") as mock_boto3:
            # Mock the Lambda response
            mock_lambda = mock_boto3.return_value
            mock_lambda.invoke.return_value = {
                "StatusCode": 200,
                "Payload": b'{"function_id": "get_goals", "parameters": {}}',
            }

            result = call_function_matcher("show my financial goals")
            self.assertEqual(result["function_id"], "get_goals")
            self.assertEqual(result["parameters"], {})

    def test_handle_unknown_request(self) -> None:
        """Test handling an unknown request."""
        with patch("boto3.client") as mock_boto3:
            # Mock the Lambda response for unknown request
            mock_lambda = mock_boto3.return_value
            mock_lambda.invoke.return_value = {
                "StatusCode": 200,
                "Payload": b'{"function_id": null, "parameters": {}}',
            }

            result = call_function_matcher("tell me a joke")
            self.assertIsNone(result.get("function_id"))

    def test_handle_lambda_error(self) -> None:
        """Test handling Lambda invocation errors."""
        with patch("boto3.client") as mock_boto3:
            # Mock Lambda error
            mock_lambda = mock_boto3.return_value
            mock_lambda.invoke.side_effect = Exception("Lambda error")

            with self.assertRaises(Exception) as context:
                call_function_matcher("show subscriptions")
            self.assertIn("Lambda error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
