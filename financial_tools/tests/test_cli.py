"""Tests for the CLI interface."""

from unittest.mock import Mock, patch

import pytest

from ..cli.interface import FinancialAssistantCLI
from ..core import call_function_matcher, execute_function


@pytest.fixture
def cli():
    """Create a CLI instance for testing."""
    return FinancialAssistantCLI(user_id="test_user")


@pytest.fixture
def mock_function_matcher():
    """Mock the function matcher response."""
    with patch("financial_tools.cli.interface.call_function_matcher") as mock:
        yield mock


@pytest.fixture
def mock_function_executor():
    """Mock the function executor response."""
    with patch("financial_tools.cli.interface.execute_function") as mock:
        yield mock


def test_cli_initialization(cli):
    """Test that the CLI initializes with the correct user ID."""
    assert cli.user_id == "test_user"


def test_handle_user_request_exit(cli):
    """Test that the CLI handles exit commands correctly."""
    with patch("builtins.input", return_value="exit"):
        assert cli.handle_user_request() is None


def test_handle_user_request_empty(cli):
    """Test that the CLI handles empty input correctly."""
    with patch("builtins.input", return_value=""):
        assert cli.handle_user_request() == "Please provide a request."


def test_handle_user_request_subscriptions(
    cli, mock_function_matcher, mock_function_executor
):
    """Test that the CLI handles subscription requests correctly."""
    # Mock the function matcher response
    mock_function_matcher.return_value = {
        "function_id": "get_subscriptions",
        "parameters": {},
        "title": "Get Subscriptions",
        "description": "List all subscriptions",
    }

    # Mock the function executor response
    mock_function_executor.return_value = {
        "subscriptions": [{"name": "Netflix", "amount": 15.99, "frequency": "monthly"}]
    }

    with patch("builtins.input", return_value="show my subscriptions"):
        response = cli.handle_user_request()
        assert "Netflix" in response
        assert "15.99" in response
        assert "monthly" in response


def test_handle_user_request_unknown(cli, mock_function_matcher):
    """Test that the CLI handles unknown requests correctly."""
    mock_function_matcher.return_value = {
        "function_id": "none",
        "parameters": {},
        "title": "Unknown Request",
        "description": "Could not match request",
    }

    with patch("builtins.input", return_value="tell me a joke"):
        response = cli.handle_user_request()
        assert "not equipped to help" in response


def test_handle_user_request_error(cli, mock_function_matcher):
    """Test that the CLI handles errors correctly."""
    mock_function_matcher.side_effect = Exception("Test error")

    with patch("builtins.input", return_value="show subscriptions"):
        response = cli.handle_user_request()
        assert "Error" in response
        assert "Test error" in response


def test_main_flow(cli, mock_function_matcher, mock_function_executor):
    """Test the main CLI flow with a complete interaction."""
    # Mock the function matcher response
    mock_function_matcher.return_value = {
        "function_id": "get_products",
        "parameters": {},
        "title": "Get Products",
        "description": "List available products",
    }

    # Mock the function executor response
    mock_function_executor.return_value = {
        "products": [
            {
                "name": "Savings Account",
                "description": "High-yield savings",
                "min_amount": 100,
                "max_amount": 100000,
            }
        ]
    }

    # Mock user input sequence
    input_sequence = ["show products", "n"]
    with patch("builtins.input", side_effect=input_sequence):
        with patch("builtins.print") as mock_print:
            cli.main()

            # Verify welcome message was displayed
            welcome_calls = [
                call
                for call in mock_print.call_args_list
                if "Hi, I'm your CLI financial tool assistant" in str(call)
            ]
            assert len(welcome_calls) > 0

            # Verify product information was displayed
            product_calls = [
                call
                for call in mock_print.call_args_list
                if "Savings Account" in str(call)
            ]
            assert len(product_calls) > 0
