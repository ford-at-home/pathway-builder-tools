"""Tests for the main application module."""

import unittest
from unittest.mock import patch

from financial_tools.cli.interface import FinancialAssistantCLI, main


class TestMainCLI(unittest.TestCase):
    """Test cases for the main CLI application."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cli = FinancialAssistantCLI()

    def test_cli_initialization(self) -> None:
        """Test CLI initialization with default user ID."""
        self.assertEqual(self.cli.user_id, "test_user")

    def test_cli_custom_user_id(self) -> None:
        """Test CLI initialization with custom user ID."""
        cli = FinancialAssistantCLI(user_id="custom_user")
        self.assertEqual(cli.user_id, "custom_user")

    def test_main_flow(self) -> None:
        """Test the main CLI flow with a complete interaction."""
        input_sequence = ["show subscriptions", "n"]
        with (
            patch("builtins.input", side_effect=input_sequence),
            patch("builtins.print") as mock_print,
            patch(
                "financial_tools.core.function_matcher.call_function_matcher",
                return_value={
                    "function_id": "get_subscriptions",
                    "parameters": {},
                },
            ),
            patch(
                "financial_tools.core.function_executor.execute_function",
                return_value={
                    "subscriptions": [
                        {
                            "name": "Netflix",
                            "amount": 15.99,
                            "frequency": "monthly",
                        }
                    ]
                },
            ),
        ):
            main()
            # Verify welcome message was displayed
            welcome_calls = [
                call
                for call in mock_print.call_args_list
                if "CLI financial tool assistant" in str(call)
            ]
            self.assertTrue(len(welcome_calls) > 0)

            # Verify subscription info was displayed
            sub_calls = [
                call for call in mock_print.call_args_list if "Netflix" in str(call)
            ]
            self.assertTrue(len(sub_calls) > 0)


class TestCLIErrorHandling(unittest.TestCase):
    """Test cases for CLI error handling."""

    def test_handle_function_matcher_error(self) -> None:
        """Test handling of function matcher errors."""
        input_sequence = ["show subscriptions", "n"]
        with (
            patch("builtins.input", side_effect=input_sequence),
            patch("builtins.print") as mock_print,
            patch(
                "financial_tools.core.function_matcher.call_function_matcher",
                side_effect=Exception("Test error"),
            ),
        ):
            main()
            error_calls = [
                call for call in mock_print.call_args_list if "Error" in str(call)
            ]
            self.assertTrue(len(error_calls) > 0)


class TestCLIExitHandling(unittest.TestCase):
    """Test cases for CLI exit handling."""

    def test_handle_keyboard_interrupt(self) -> None:
        """Test handling of keyboard interrupt."""
        with (
            patch("builtins.input", side_effect=KeyboardInterrupt()),
            patch("builtins.print") as mock_print,
        ):
            main()
            goodbye_calls = [
                call for call in mock_print.call_args_list if "Goodbye" in str(call)
            ]
            self.assertTrue(len(goodbye_calls) > 0)


if __name__ == "__main__":
    unittest.main()
