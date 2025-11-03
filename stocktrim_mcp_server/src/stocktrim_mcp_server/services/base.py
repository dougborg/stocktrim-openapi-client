"""Base service classes for MCP tools."""

from __future__ import annotations

from stocktrim_public_api_client import StockTrimClient


class BaseService:
    """Base class for all MCP services.

    Provides common functionality and patterns for service implementations.
    Services encapsulate business logic and orchestrate calls to the
    StockTrim API client.
    """

    def __init__(self, client: StockTrimClient):
        """Initialize service with StockTrim client.

        Args:
            client: StockTrim API client instance
        """
        self._client = client

    @staticmethod
    def validate_not_empty(value: str | None, field_name: str) -> None:
        """Validate that a string field is not empty.

        Args:
            value: String value to validate
            field_name: Name of the field (for error messages)

        Raises:
            ValueError: If value is None, empty, or whitespace-only
        """
        if not value or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")

    @staticmethod
    def validate_positive(value: float | None, field_name: str) -> None:
        """Validate that a numeric field is positive.

        Args:
            value: Numeric value to validate
            field_name: Name of the field (for error messages)

        Raises:
            ValueError: If value is None or <= 0
        """
        if value is None or value <= 0:
            raise ValueError(f"{field_name} must be greater than 0")
