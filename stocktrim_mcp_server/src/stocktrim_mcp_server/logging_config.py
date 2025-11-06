"""Structured logging configuration for StockTrim MCP Server.

This module configures structlog for structured, machine-readable logging with:
- JSON output in production for log aggregation systems
- Human-readable output in development
- Correlation IDs for request tracing
- Performance timing and metrics
- Error categorization
"""

import logging
import os
import sys
from typing import Any

import structlog


def configure_logging() -> structlog.BoundLogger:
    """Configure structlog for the MCP server.

    Configures structured logging based on environment:
    - Development: Human-readable colored output
    - Production: JSON output for log aggregation

    Returns:
        Configured structlog logger instance
    """
    # Get log level from environment
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Get log format from environment (json or console)
    log_format = os.getenv("LOG_FORMAT", "console").lower()

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    # Shared processors for all formats
    shared_processors: list[structlog.types.Processor] = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add exception info
        structlog.processors.ExceptionRenderer(),
        # Add call site information (module, function, line)
        structlog.processors.CallsiteParameterAdder(
            parameters={
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    # Configure output format based on environment
    if log_format == "json":
        # Production: JSON output for log aggregation
        processors = [
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Human-readable colored output
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Create and return logger
    logger = structlog.get_logger("stocktrim_mcp_server")
    logger.info(
        "logging_configured",
        log_level=log_level_str,
        log_format=log_format,
    )

    return logger


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Optional logger name. Defaults to "stocktrim_mcp_server"

    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name or "stocktrim_mcp_server")


class LoggerMixin:
    """Mixin class to add structured logging to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger bound to this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def log_tool_invocation(
    tool_name: str,
    params: dict[str, Any],
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Create a structured log context for tool invocation.

    Args:
        tool_name: Name of the tool being invoked
        params: Tool parameters
        correlation_id: Optional correlation ID for tracing

    Returns:
        Dictionary with log context
    """
    context = {
        "event": "tool_invoked",
        "tool_name": tool_name,
        "params": params,
    }
    if correlation_id:
        context["correlation_id"] = correlation_id

    return context


def log_tool_result(
    tool_name: str,
    success: bool,
    duration_ms: float,
    error: str | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Create a structured log context for tool result.

    Args:
        tool_name: Name of the tool
        success: Whether the tool succeeded
        duration_ms: Duration in milliseconds
        error: Optional error message
        correlation_id: Optional correlation ID for tracing

    Returns:
        Dictionary with log context
    """
    context = {
        "event": "tool_completed" if success else "tool_failed",
        "tool_name": tool_name,
        "success": success,
        "duration_ms": duration_ms,
    }
    if error:
        context["error"] = error
    if correlation_id:
        context["correlation_id"] = correlation_id

    return context
