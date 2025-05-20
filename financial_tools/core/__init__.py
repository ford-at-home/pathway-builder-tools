"""Core functionality for the financial tools system.

This module provides the core functionality that powers the financial tools system,
including function matching, execution, and response formatting. It serves as the
central hub for all financial operations, connecting the CLI interface with the
underlying AWS Lambda functions.

The module exports three main functions:
    - call_function_matcher: Determines which function to call based on user input
    - execute_function: Executes the matched function with provided parameters
    - format_response: Formats function responses for user-friendly display

These functions work together to provide a seamless experience:
1. User input is processed by call_function_matcher to determine intent
2. The matched function is executed with execute_function
3. The response is formatted for display using format_response

Example:
    >>> from financial_tools.core import call_function_matcher, execute_function, format_response
    >>> match = call_function_matcher("show my subscriptions")
    >>> result = execute_function(match["function_id"], match["parameters"])
    >>> print(format_response(result, match["function_id"]))
"""

from .function_executor import execute_function
from .function_matcher import call_function_matcher
from .response_formatter import format_response

__all__ = ["call_function_matcher", "execute_function", "format_response"]
