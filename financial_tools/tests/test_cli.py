"""Tests for the CLI interface.

This module contains tests for the command-line interface of the financial tools
system, including input handling, function matching, and response formatting.
"""

import unittest
from unittest.mock import patch

from financial_tools.cli.interface import CLI


class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli = CLI()

    def test_handle_user_request(self) -> None:
        """Test handling of user requests."""
        test_cases = [
            (
                "what are my recurring payments",
                "get_subscriptions",
                {
                    "subscriptions": [
                        {"name": "Spotify", "amount": "9.99", "frequency": "monthly"},
                        {"name": "Netflix", "amount": "15.99", "frequency": "monthly"},
                    ]
                },
            ),
            (
                "show me available financial products",
                "get_products",
                {
                    "products": [
                        {
                            "name": "High-Yield Savings",
                            "category": "Savings",
                            "features": ["4.5% APY", "No minimum balance"],
                        }
                    ]
                },
            ),
            (
                "what are my financial goals",
                "get_goals",
                {
                    "goals": [
                        {"name": "Emergency Fund", "current": 5000, "target": 10000}
                    ]
                },
            ),
        ]

        for cmd, expected_function, mock_response in test_cases:
            with self.subTest(cmd=cmd), patch(
                "financial_tools.core.function_matcher.FunctionMatcher"
                ".match_function"
            ) as mock_match, patch(
                "financial_tools.core.function_matcher.FunctionMatcher"
                ".execute_function"
            ) as mock_execute:
                # Set up mock responses
                mock_match.return_value = {"function_id": expected_function}
                mock_execute.return_value = mock_response

                # Test the request handling
                response = self.cli.handle_user_request(cmd)
                self.assertIsNotNone(response)
                self.assertIn(expected_function, str(mock_match.call_args))

    def test_format_response(self) -> None:
        """Test response formatting for different data types."""
        # Test subscription formatting
        sub_response = {
            "subscriptions": [
                {"name": "Spotify", "amount": "9.99", "frequency": "monthly"},
                {"name": "Netflix", "amount": "15.99", "frequency": "monthly"},
            ]
        }
        formatted = self.cli.format_response(sub_response)
        self.assertIn("Spotify", formatted)
        self.assertIn("Netflix", formatted)
        self.assertIn("$9.99", formatted)
        self.assertIn("$15.99", formatted)

        # Test product formatting
        product_response = {
            "products": [
                {
                    "name": "High-Yield Savings",
                    "category": "Savings",
                    "features": ["4.5% APY", "No minimum balance"],
                }
            ]
        }
        formatted = self.cli.format_response(product_response)
        self.assertIn("High-Yield Savings", formatted)
        self.assertIn("Savings", formatted)
        self.assertIn("4.5% APY", formatted)

        # Test goal formatting
        goal_response = {
            "goals": [{"name": "Emergency Fund", "current": 5000, "target": 10000}]
        }
        formatted = self.cli.format_response(goal_response)
        self.assertIn("Emergency Fund", formatted)
        self.assertIn("$5000", formatted)
        self.assertIn("$10000", formatted)
        self.assertIn("50.0%", formatted)


if __name__ == "__main__":
    unittest.main()
