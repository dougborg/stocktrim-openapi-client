"""
StockTrim Public API Client

A modern, pythonic StockTrim Inventory Management API client with automatic
retries and custom authentication.
"""

import logging

from .stocktrim_client import StockTrimClient
from .utils import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PermissionError,
    ServerError,
    ValidationError,
    get_error_message,
    is_error,
    is_success,
    unwrap,
)

__version__ = "0.4.1"

# Define TRACE level (below DEBUG=10, above NOTSET=0)
# This follows the pattern used by urllib3 and httpx for detailed logging
TRACE = 5
logging.addLevelName(TRACE, "TRACE")


# Add trace() method to Logger class
def _trace(self: logging.Logger, message: str, *args, **kwargs) -> None:
    """Log a message with severity 'TRACE'.

    TRACE level (5) is below DEBUG (10) and is used for extremely detailed
    logging such as full response bodies. This is useful for deep debugging
    when DEBUG level doesn't provide enough detail.

    Args:
        message: The log message
        *args: Positional arguments for message formatting
        **kwargs: Keyword arguments passed to _log()
    """
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)


logging.Logger.trace = _trace  # type: ignore[attr-defined]

__all__ = [
    "TRACE",
    # Exceptions
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "PermissionError",
    "ServerError",
    "StockTrimClient",
    "ValidationError",
    "get_error_message",
    "is_error",
    "is_success",
    "unwrap",
]
