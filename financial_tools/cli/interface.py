"""CLI interface for the financial tools system."""

import sys
from typing import Optional

from ..core import call_function_matcher, execute_function, format_response


class FinancialAssistantCLI:
    """CLI interface for the financial assistant."""

    def __init__(self, user_id: str = "test_user"):
        """Initialize the CLI interface.

        Args:
            user_id: The user ID to use for requests
        """
        self.user_id = user_id

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

    def handle_user_request(self) -> Optional[str]:
        """Process a single user request through the complete flow.

        Returns:
            Optional[str]: The formatted response, or None if the user wants to exit
        """
        try:
            # Get user input
            user_input = input("> ").strip()
            if not user_input:
                return "Please provide a request."
            if user_input.lower() in ("exit", "quit", "q"):
                return None

            # Determine which tool to use
            match_result = call_function_matcher(user_input, self.user_id)
            function_id = match_result.get("function_id")

            if function_id == "none":
                return "🤷‍♂️ I'm not equipped to help with that request. Try rephrasing or ask about subscriptions, products, or goals."

            # Call the appropriate tool
            result = execute_function(function_id, match_result.get("parameters", {}))

            # Format and return the response
            return format_response(result, function_id)

        except Exception as e:
            return f"❌ Error: {str(e)}"


def main() -> None:
    """Main entry point for the CLI application."""
    cli = FinancialAssistantCLI()
    cli.display_welcome_message()

    while True:
        try:
            response = cli.handle_user_request()
            if response is None:
                print("\n👋 Thanks for using the financial assistant. Goodbye!")
                break

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
