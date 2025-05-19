"""Command-line interface for financial tools.

This module provides a user-friendly CLI for interacting with financial tools.
It handles user input, matches it to appropriate functions, and displays results
in a clear, formatted way.
"""

import json
from typing import Any, Dict, List, Optional, TypedDict, Union

from financial_tools.core.function_matcher import FunctionMatcher
from financial_tools.core.logging_config import setup_logging

# Set up logging for the CLI
# This helps track user interactions and any errors
logger = setup_logging(__name__)


class Subscription(TypedDict):
    """Type definition for subscription data."""

    name: str
    amount: str
    frequency: str


class Product(TypedDict):
    """Type definition for product data."""

    name: str
    category: str
    features: List[str]


class Goal(TypedDict):
    """Type definition for goal data."""

    name: str
    current: int
    target: int


class CLI:
    """Command-line interface for financial tools.

    This class handles the main CLI loop, user input processing, and result
    display. It uses the function matcher to determine which financial tool
    to invoke based on user input.
    """

    def __init__(self) -> None:
        """Initialize the CLI with a function matcher."""
        # Create function matcher for handling user requests
        # This will be used to match natural language to specific functions
        self.function_matcher = FunctionMatcher()

    def display_welcome_message(self) -> None:
        """Display welcome message and available commands."""
        # Show a friendly welcome message
        # Include examples to help users get started
        print("\nWelcome to Financial Tools CLI!")
        print("You can ask questions like:")
        print("  - What are my recurring payments?")
        print("  - Show me available financial products")
        print("  - What are my financial goals?")
        print("\nType 'exit' to quit.\n")

    def format_response(self, response: Dict[str, Any]) -> str:
        """Format the response for display.

        Args:
            response: The response data to format

        Returns:
            A formatted string representation of the response
        """
        # Format different types of responses appropriately
        # This makes the output more readable and user-friendly
        if "subscriptions" in response:
            # Format subscription data as a list with monthly costs
            return self._format_subscriptions(response["subscriptions"])
        elif "products" in response:
            # Format product data as a categorized list
            return self._format_products(response["products"])
        elif "goals" in response:
            # Format goals with progress information
            return self._format_goals(response["goals"])
        elif "summary" in response:
            # Use the summary directly if available
            return str(response["summary"])
        else:
            # Fallback to pretty-printed JSON
            return json.dumps(response, indent=2)

    def _format_subscriptions(self, subscriptions: List[Subscription]) -> str:
        """Format subscription data for display.

        Args:
            subscriptions: List of subscription data

        Returns:
            Formatted string of subscriptions
        """
        # Format each subscription with name and cost
        # Group by frequency for better organization
        result = ["Your Subscriptions:"]
        for sub in subscriptions:
            result.append(f"  • {sub['name']}: ${sub['amount']} {sub['frequency']}")
        return "\n".join(result)

    def _format_products(self, products: List[Product]) -> str:
        """Format product data for display.

        Args:
            products: List of product data

        Returns:
            Formatted string of products
        """
        # Group products by category
        # Show key features for each product
        result = ["Available Financial Products:"]
        categories: Dict[str, List[Product]] = {}
        for product in products:
            cat = product["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)

        for category, items in categories.items():
            result.append(f"\n{category}:")
            for item in items:
                result.append(f"  • {item['name']}")
                if "features" in item:
                    for feature in item["features"]:
                        result.append(f"    - {feature}")
        return "\n".join(result)

    def _format_goals(self, goals: List[Goal]) -> str:
        """Format goal data for display.

        Args:
            goals: List of goal data

        Returns:
            Formatted string of goals
        """
        # Show progress towards each goal
        # Include target and current amounts
        result = ["Your Financial Goals:"]
        for goal in goals:
            progress = (goal["current"] / goal["target"]) * 100
            result.append(
                f"  • {goal['name']}:"
                f" ${goal['current']} / ${goal['target']}"
                f" ({progress:.1f}%)"
            )
        return "\n".join(result)

    def handle_user_request(self, user_input: str) -> Optional[str]:
        """Process a user request and return the response.

        Args:
            user_input: The user's input text

        Returns:
            Formatted response string or None if no function matched
        """
        try:
            # Log the user's request for debugging
            logger.info(f"Processing request: {user_input}")

            # Match the request to a function
            # This uses natural language processing to understand intent
            match_result = self.function_matcher.match_function(user_input)

            # Handle case where no function matches
            if match_result.get("statusCode") == 404:
                return (
                    "I'm not sure how to help with that. Try asking about your "
                    "subscriptions, available products, or financial goals."
                )

            # Get the matched function ID
            function_id = match_result.get("function_id")
            if not function_id or function_id.lower() == "none":
                return (
                    "I couldn't understand what you're asking for. "
                    "Try rephrasing your question."
                )

            # Execute the matched function
            # This will call the appropriate Lambda function
            logger.info(f"Executing function: {function_id}")
            response = self.function_matcher.execute_function(function_id)

            # Format and return the response
            # This makes the output user-friendly
            return self.format_response(response)

        except Exception as e:
            # Log any errors that occur
            # This helps with debugging and improving the system
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"

    def run(self) -> None:
        """Run the main CLI loop."""
        # Display welcome message
        # This helps users understand what they can do
        self.display_welcome_message()

        while True:
            try:
                # Get user input
                # Strip whitespace to handle empty input gracefully
                user_input = input("What would you like to know? ").strip()

                # Check for exit command
                if user_input.lower() in ("exit", "quit", "q"):
                    print("\nGoodbye!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Process the request and display response
                # This is the main interaction loop
                response = self.handle_user_request(user_input)
                if response:
                    print(f"\n{response}\n")

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n\nGoodbye!")
                break
            except Exception as e:
                # Log any unexpected errors
                # This helps track down issues in the CLI
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                print(f"\nAn unexpected error occurred: {str(e)}\n")


def main() -> None:
    """Run the CLI application."""
    # Create and run the CLI
    # This is the entry point for the application
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
