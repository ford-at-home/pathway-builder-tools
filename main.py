import json
from typing import Any, Dict, Optional

import boto3


class LambdaClient:
    """Handles all Lambda function invocations."""

    def __init__(self):
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

    def __init__(self, lambda_client: LambdaClient):
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
    ):
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


def main():
    """Main entry point for the CLI application."""
    cli = FinancialAssistantCLI()
    cli.display_welcome_message()

    while True:
        try:
            response = cli.handle_user_request()
            print(f"\n{response}\n")

            # Ask if the user wants to continue
            if input("Would you like to ask something else? (y/n): ").lower() != "y":
                print("\n👋 Thanks for using the financial assistant. Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using the financial assistant. Goodbye!")
            break


if __name__ == "__main__":
    main()
