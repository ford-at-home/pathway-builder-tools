"""Command-line interface for the financial tools system.

This module provides a user-friendly command-line interface for interacting with
the financial tools system. It allows users to manage their subscriptions,
explore financial products, and track their financial goals through natural
language commands.

The interface is built around the FinancialAssistantCLI class, which handles:
    - User interaction and input processing
    - Natural language request matching
    - Function execution and response formatting
    - Error handling and user feedback

The CLI supports three main capabilities:
    1. Subscription Management
       - View recurring payments
       - Track subscription costs
    2. Financial Product Discovery
       - Browse available financial tools
       - Compare product features
    3. Goal Management
       - Set financial goals
       - Track progress
       - Update or delete goals

The interface uses the core module's functions for:
    - Natural language processing (call_function_matcher)
    - Function execution (execute_function)
    - Response formatting (format_response)

Example:
    >>> from financial_tools.cli.interface import FinancialAssistantCLI
    >>> cli = FinancialAssistantCLI(user_id="user123")
    >>> cli.display_welcome_message()
    >>> response = cli.handle_user_request()
    >>> print(response)
"""

import sys
from typing import Optional

from ..core import call_function_matcher, execute_function, format_response


class FinancialAssistantCLI:
    """Command-line interface for interacting with the financial tools system.

    This class provides a conversational interface for users to interact with
    the financial tools system using natural language. It handles the complete
    flow from user input to formatted response, including error handling and
    user feedback.

    The interface is designed to be intuitive and user-friendly, with:
        - Clear welcome message explaining capabilities
        - Natural language input processing
        - Formatted, easy-to-read responses
        - Graceful error handling
        - Interactive session management

    The class maintains a user context (user_id) and provides methods for:
        - Displaying the welcome message
        - Processing user requests
        - Managing the interactive session

    Example:
        >>> cli = FinancialAssistantCLI(user_id="user123")
        >>> cli.display_welcome_message()
        >>> while True:
        ...     response = cli.handle_user_request()
        ...     if response is None:
        ...         break
        ...     print(response)
    """

    def __init__(self, user_id: str = "test_user"):
        """Initialize the CLI interface.

        Args:
            user_id: The user ID to use for requests. This ID is used to
                identify the user in all function calls and is included in
                the parameters for user-specific operations. Defaults to
                "test_user" for testing purposes.

        Example:
            >>> cli = FinancialAssistantCLI(user_id="john_doe")
            >>> print(cli.user_id)
            'john_doe'
        """
        self.user_id = user_id

    def display_welcome_message(self) -> None:
        """Display the welcome message and available capabilities.

        This method prints a friendly welcome message that:
            - Introduces the assistant
            - Lists the three main capabilities
            - Provides example requests
            - Sets user expectations

        The message is formatted with emojis and clear sections to make it
        visually appealing and easy to read.

        Example:
            >>> cli = FinancialAssistantCLI()
            >>> cli.display_welcome_message()
            👋 Hi, I'm your CLI financial tool assistant.
            ...
        """
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

        This method handles the complete flow of processing a user request:
        1. Gets and validates user input
        2. Matches the input to an appropriate function
        3. Executes the matched function
        4. Formats and returns the response

        The method includes error handling for:
            - Empty input
            - Exit commands
            - Function matching errors
            - Function execution errors
            - Response formatting errors

        Args:
            None

        Returns:
            Optional[str]: The formatted response if successful, or None if the
                user wants to exit. The response can be:
                - A formatted list of subscriptions/products/goals
                - A success message for operations
                - An error message if something goes wrong
                - None if the user wants to exit

        Example:
            >>> cli = FinancialAssistantCLI()
            >>> response = cli.handle_user_request()
            > show my subscriptions
            >>> print(response)
            Subscriptions:
            - Netflix: $15.99 (monthly)
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
    """Main entry point for the CLI application.

    This function serves as the main entry point for the CLI application. It:
        1. Creates a FinancialAssistantCLI instance
        2. Displays the welcome message
        3. Enters an interactive loop to:
            - Process user requests
            - Display responses
            - Handle session continuation
        4. Manages graceful exit on:
            - User request
            - Keyboard interrupt
            - Error conditions

    The function provides a complete interactive session with:
        - Clear user prompts
        - Formatted responses
        - Session continuation options
        - Graceful exit handling

    Example:
        >>> main()
        👋 Hi, I'm your CLI financial tool assistant.
        ...
        > show my subscriptions
        Subscriptions:
        - Netflix: $15.99 (monthly)
        ...
        Would you like to ask something else? (y/n):
    """
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
