"""Logging configuration for the financial tools system.

This module provides a centralized logging configuration that sets up consistent
logging across all components of the system. It configures both file and console
handlers with appropriate formatting.
"""

import logging
from pathlib import Path

# Create logs directory if it doesn't exist
# This ensures we have a place to write log files
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logging(name: str) -> logging.Logger:
    """Set up logging for a module.

    This function configures a logger with both file and console handlers.
    The file handler writes to a timestamped log file, while the console
    handler provides immediate feedback during development.

    Args:
        name: The name of the module to set up logging for

    Returns:
        A configured logger instance
    """
    # Create a logger for this module
    # This allows us to track logs from different parts of the system
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    # This writes logs to a file with timestamps for later review
    file_handler = logging.FileHandler(
        log_dir / f"{name}.log", mode="a", encoding="utf-8"  # Append to existing logs
    )
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler
    # This provides immediate feedback during development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters
    # The file formatter includes timestamps and module names
    # The console formatter is simpler for readability
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"  # Simpler format for console
    )

    # Set the formatters
    # This ensures consistent log formatting
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add the handlers to the logger
    # This allows logs to go to both file and console
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
