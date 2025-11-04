"""
StockTrim Public API Client

A modern, pythonic StockTrim Inventory Management API client with automatic
retries and custom authentication.
"""

__version__ = "0.7.0"

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

__all__ = [
    # Exceptions
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "PermissionError",
    "ServerError",
    # Main client
    "StockTrimClient",
    "ValidationError",
    # Utility functions
    "get_error_message",
    "is_error",
    "is_success",
    "unwrap",
]
