"""Tests for the logging configuration."""

import logging
import unittest
from pathlib import Path

from ..core.logging_config import setup_logging


class TestLoggingConfig(unittest.TestCase):
    """Test cases for the logging configuration."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.log_dir = Path("logs")
        if not self.log_dir.exists():
            self.log_dir.mkdir()

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        # Remove test log files
        for log_file in self.log_dir.glob("test_*.log"):
            log_file.unlink()

    def test_setup_logging(self) -> None:
        """Test that logging is configured correctly."""
        logger = setup_logging("test_logger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.INFO)

        # Verify handlers
        self.assertTrue(
            any(isinstance(h, logging.FileHandler) for h in logger.handlers)
        )
        self.assertTrue(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        )

    def test_log_file_creation(self) -> None:
        """Test that log files are created correctly."""
        logger = setup_logging("test_file_logger")
        test_message = "Test log message"
        logger.info(test_message)

        # Find the log file
        log_files = list(self.log_dir.glob("test_file_logger_*.log"))
        self.assertEqual(len(log_files), 1)

        # Verify log content
        log_content = log_files[0].read_text()
        self.assertIn(test_message, log_content)
        self.assertIn("INFO", log_content)

    def test_log_format(self) -> None:
        """Test that log messages are formatted correctly."""
        logger = setup_logging("test_format_logger")
        test_message = "Test format message"
        logger.info(test_message)

        # Find the log file
        log_files = list(self.log_dir.glob("test_format_logger_*.log"))
        self.assertEqual(len(log_files), 1)

        # Verify log format
        log_content = log_files[0].read_text()
        self.assertIn("INFO", log_content)
        self.assertIn("test_format_logger", log_content)
        self.assertIn(test_message, log_content)
        # Verify timestamp format
        self.assertRegex(log_content, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


if __name__ == "__main__":
    unittest.main()
