"""Entry point module for the financial tools CLI.

This module serves as the entry point for the financial tools command-line
interface. It provides a simple way to run the CLI application by importing
and executing the main function from the interface module.

The module is designed to be run directly using Python's -m flag:
    python -m financial_tools.cli

This allows the CLI to be executed as a module, ensuring proper package
imports and resource management.

Example:
    $ python -m financial_tools.cli
    👋 Hi, I'm your CLI financial tool assistant.
    ...
"""

from .interface import main

if __name__ == "__main__":
    main()
