from unittest.mock import Mock, patch

import pytest

from main import FinancialAssistantCLI, LambdaClient, ResponseFormatter


class TestFinancialAssistantCLI:
    @pytest.fixture
    def mock_lambda_client(self):
        return Mock(spec=LambdaClient)

    @pytest.fixture
    def mock_response_formatter(self):
        return Mock(spec=ResponseFormatter)

    @pytest.fixture
    def cli(self, mock_lambda_client, mock_response_formatter):
        return FinancialAssistantCLI(mock_lambda_client, mock_response_formatter)

    def test_display_welcome_message(self, cli, capsys):
        cli.display_welcome_message()
        captured = capsys.readouterr()
        assert "👋 Hi, I'm your CLI financial tool assistant" in captured.out
        assert "I can help you with 3 things:" in captured.out
        assert "1. 🧾 Subscriptions" in captured.out
        assert "2. 🧰 Financial Products" in captured.out
        assert "3. 🎯 Financial Goals" in captured.out

    def test_handle_valid_subscriptions_request(
        self, cli, mock_lambda_client, mock_response_formatter
    ):
        # Mock Lambda responses
        mock_lambda_client.pick_tool.return_value = {"tool": "subscriptions"}
        mock_lambda_client.call_tool.return_value = {
            "subscriptions": [
                {"name": "Netflix", "amount": 15.99, "frequency": "monthly"}
            ]
        }
        mock_response_formatter.format_summary.return_value = (
            "You have 1 active subscription: Netflix at $15.99/month"
        )

        # Simulate user input
        with patch("builtins.input", return_value="show me my subscriptions"):
            response = cli.handle_user_request()

        assert response == "You have 1 active subscription: Netflix at $15.99/month"
        mock_lambda_client.pick_tool.assert_called_once_with("show me my subscriptions")
        mock_lambda_client.call_tool.assert_called_once_with("subscriptions", {})
        mock_response_formatter.format_summary.assert_called_once()

    def test_handle_invalid_request(self, cli, mock_lambda_client):
        mock_lambda_client.pick_tool.return_value = {"tool": "none"}

        with patch("builtins.input", return_value="tell me a joke"):
            response = cli.handle_user_request()

        assert "🤷‍♂️ I'm not equipped to help with that request" in response
        mock_lambda_client.pick_tool.assert_called_once_with("tell me a joke")
        mock_lambda_client.call_tool.assert_not_called()

    def test_handle_lambda_error(self, cli, mock_lambda_client):
        mock_lambda_client.pick_tool.side_effect = Exception("Lambda error")

        with patch("builtins.input", return_value="show my subscriptions"):
            response = cli.handle_user_request()

        assert "Sorry, I encountered an error" in response


class TestLambdaClient:
    @pytest.fixture
    def lambda_client(self):
        return LambdaClient()

    def test_pick_tool(self, lambda_client):
        # This would be an integration test with actual Lambda
        # For now, we'll mock the boto3 client
        with patch("boto3.client") as mock_boto:
            mock_lambda = Mock()
            mock_boto.return_value = mock_lambda
            mock_lambda.invoke.return_value = {"Payload": '{"tool": "subscriptions"}'}

            result = lambda_client.pick_tool("show my subscriptions")
            assert result == {"tool": "subscriptions"}


class TestResponseFormatter:
    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    def test_format_summary(self, formatter):
        raw_response = {
            "goals": [
                {"name": "Vacation", "target_amount": 3000, "current_amount": 1200}
            ]
        }

        with patch("boto3.client") as mock_boto:
            mock_lambda = Mock()
            mock_boto.return_value = mock_lambda
            mock_lambda.invoke.return_value = {
                "Payload": '"You have saved $1200 towards your $3000 vacation goal"'
            }

            summary = formatter.format_summary(raw_response, "goals")
            assert "You have saved $1200" in summary
