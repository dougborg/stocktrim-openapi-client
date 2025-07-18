"""
StockTrim Public API Client

A modern, pythonic StockTrim Inventory Management API client with automatic
retries and custom authentication.
"""

__version__ = "0.1.0"

from .stocktrim_client import StockTrimClient

__all__ = ["StockTrimClient"]
