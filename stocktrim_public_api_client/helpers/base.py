"""Base class for domain helper classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stocktrim_public_api_client.stocktrim_client import StockTrimClient


class Base:
    """Base class for all domain helper classes.

    Provides common functionality and access to the StockTrimClient instance.

    Args:
        client: The StockTrimClient instance to use for API calls.
    """

    def __init__(self, client: StockTrimClient) -> None:
        """Initialize with a client instance.

        Args:
            client: The StockTrimClient instance to use for API calls.
        """
        self._client = client
