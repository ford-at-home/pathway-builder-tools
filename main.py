"""Main entry point for the financial tools application.

This module provides the main entry point for running the financial tools
application, including both CLI and API interfaces.
"""

import json
from typing import Any, Dict, Optional

import boto3

from financial_tools.cli.interface import CLI
from financial_tools.core.function_matcher import FunctionMatcher
from financial_tools.core.logging_config import setup_logging

# Set up logging for the main module
# This helps track application startup and any errors
logger = setup_logging(__name__)


class LambdaClient:
    """Handles all Lambda function invocations."""

    def __init__(self) -> None:
        """Initialize the Lambda client with AWS clients and function mappings.

        Sets up the boto3 Lambda client and defines the mapping of tool names
        to their corresponding Lambda function names.
        """
        self.lambda_client = boto3.client("lambda")
        self.tool_picker_function = "tool_picker"
        self.summarizer_function = "summarizer"
        self.tool_functions = {
            "subscriptions": "subscriptions_tool",
            "products": "financial_products_tool",
            "goals": "financial_goals_tool",
        }

    def _invoke_lambda(
        self, function_name: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke a Lambda function and return its response."""
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name, Payload=json.dumps(payload)
            )
            return json.loads(response["Payload"].read())
        except Exception as e:
            raise Exception(f"Error invoking Lambda {function_name}: {str(e)}")

    def pick_tool(self, query: str) -> Dict[str, str]:
        """Determine which tool to use based on the user's query."""
        return self._invoke_lambda(self.tool_picker_function, {"query": query})

    def call_tool(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call the appropriate tool Lambda function."""
        if tool_name not in self.tool_functions:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._invoke_lambda(self.tool_functions[tool_name], payload)

    def summarize_response(self, response: Dict[str, Any], tool_name: str) -> str:
        """Summarize the tool's response using the summarizer Lambda."""
        payload = {"response": response, "tool": tool_name}
        result = self._invoke_lambda(self.summarizer_function, payload)
        return result.get("summary", "No summary available")


class ResponseFormatter:
    """Handles formatting and displaying responses to the user."""

    def __init__(self, lambda_client: LambdaClient) -> None:
        """Initialize the response formatter with a Lambda client.

        Args:
            lambda_client: The Lambda client to use for summarizing responses
        """
        self.lambda_client = lambda_client

    def format_summary(self, response: Dict[str, Any], tool_name: str) -> str:
        """Format the response using the summarizer Lambda."""
        return self.lambda_client.summarize_response(response, tool_name)

    def format_error(self, error_message: str) -> str:
        """Format error messages for display."""
        return f"❌ Error: {error_message}"

    def format_unknown_request(self) -> str:
        """Format the message for unknown requests."""
        return "🤷‍♂️ I'm not equipped to help with that request. Try rephrasing or ask about subscriptions, products, or goals."


class FinancialAssistantCLI:
    """Main CLI interface for the financial assistant."""

    def __init__(
        self,
        lambda_client: Optional[LambdaClient] = None,
        response_formatter: Optional[ResponseFormatter] = None,
    ) -> None:
        """Initialize the financial assistant CLI.

        Args:
            lambda_client: Optional Lambda client for function execution
            response_formatter: Optional formatter for response display
        """
        self.lambda_client = lambda_client or LambdaClient()
        self.response_formatter = response_formatter or ResponseFormatter(
            self.lambda_client
        )

    def display_welcome_message(self) -> None:
        """Display the welcome message and available capabilities."""
        welcome_message = """
👋 Hi, I'm your CLI financial tool assistant.

I can help you with 3 things:
  1. 🧾 Subscriptions – "Show me my recurring payments"
  2. 🧰 Financial Products – "List some financial tools I could use"
  3. 🎯 Financial Goals – "Add a new goal to save for vacation"

If your request doesn't match one of those, I'll let you know I can't help.

How can I help today?
"""
        print(welcome_message.strip())

    def handle_user_request(self) -> str:
        """Process a single user request through the complete flow."""
        try:
            # Get user input
            user_input = input("> ").strip()
            if not user_input:
                return "Please provide a request."

            # Determine which tool to use
            tool_response = self.lambda_client.pick_tool(user_input)
            tool_name = tool_response.get("tool")

            if tool_name == "none":
                return self.response_formatter.format_unknown_request()

            # Call the appropriate tool
            tool_result = self.lambda_client.call_tool(tool_name, {})

            # Format and return the response
            return self.response_formatter.format_summary(tool_result, tool_name)

        except Exception as e:
            return self.response_formatter.format_error(str(e))


class FinancialToolsAPI:
    """API interface for financial tools.

    This class provides a programmatic interface to the financial tools system,
    allowing other applications to interact with it via function calls rather
    than the CLI.
    """

    def __init__(self) -> None:
        """Initialize the API with a function matcher."""
        # Create function matcher for handling requests
        # This will be used to match natural language to specific functions
        self.function_matcher = FunctionMatcher()

    def process_request(self, request: str) -> Dict[str, Any]:
        """Process a request and return the response.

        Args:
            request: The natural language request to process

        Returns:
            Dict containing the response data or error information
        """
        try:
            # Match the request to a function
            # This uses natural language processing to understand intent
            match_result = self.function_matcher.match_function(request)

            # Handle case where no function matches
            if match_result.get("statusCode") == 404:
                return {"status": "error", "message": "No matching function found"}

            # Get the matched function ID
            function_id = match_result.get("function_id")
            if not function_id or function_id.lower() == "none":
                return {"status": "error", "message": "Could not understand request"}

            # Execute the matched function
            # This will call the appropriate Lambda function
            response = self.function_matcher.execute_function(function_id)
            return {"status": "success", "data": response}

        except Exception as e:
            # Log any errors that occur
            # This helps with debugging and improving the system
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}


def main() -> None:
    """Run the financial tools application.

    This function serves as the main entry point for the application.
    It can be used to start either the CLI or API interface.
    """
    # Create and run the CLI
    # This is the default interface for users
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
