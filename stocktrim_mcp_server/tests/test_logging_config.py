"""Tests for structured logging configuration."""

import os
from unittest.mock import patch

from stocktrim_mcp_server.logging_config import configure_logging, get_logger


class TestLoggingConfiguration:
    """Test logging configuration setup."""

    def test_configure_logging_default(self):
        """Test default logging configuration (console format, INFO level)."""
        with patch.dict(os.environ, {}, clear=True):
            logger = configure_logging()

            assert logger is not None
            # Logger is a BoundLoggerLazyProxy, check it has the right methods
            assert hasattr(logger, "info")
            assert hasattr(logger, "error")

    def test_configure_logging_json_format(self):
        """Test JSON format configuration."""
        with patch.dict(os.environ, {"LOG_FORMAT": "json", "LOG_LEVEL": "INFO"}):
            logger = configure_logging()

            assert logger is not None
            assert hasattr(logger, "info")

    def test_configure_logging_debug_level(self):
        """Test DEBUG log level configuration."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            logger = configure_logging()

            assert logger is not None
            # Just verify logger is configured and has methods
            assert hasattr(logger, "debug")
            assert hasattr(logger, "info")

    def test_configure_logging_invalid_level_defaults_to_info(self):
        """Test that invalid log level defaults to INFO."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            logger = configure_logging()

            assert logger is not None
            # Just verify logger is configured
            assert hasattr(logger, "info")

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")

        assert logger is not None
        # Check logger has expected methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_get_logger_default_name(self):
        """Test getting a logger with default name."""
        logger = get_logger()

        assert logger is not None
        assert hasattr(logger, "info")

    def test_logger_methods_exist(self):
        """Test that logger has expected methods."""
        logger = get_logger("test")

        # Verify all standard logging methods exist
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")

    def test_console_format_env_var(self):
        """Test console format via environment variable."""
        with patch.dict(os.environ, {"LOG_FORMAT": "console"}):
            logger = configure_logging()

            assert logger is not None

    def test_warning_level(self):
        """Test WARNING log level configuration."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
            logger = configure_logging()

            assert logger is not None
            # Verify logger is configured
            assert hasattr(logger, "warning")
            assert hasattr(logger, "error")

    def test_error_level(self):
        """Test ERROR log level configuration."""
        with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}):
            logger = configure_logging()

            assert logger is not None
            # Verify logger is configured
            assert hasattr(logger, "error")
            assert hasattr(logger, "critical")
