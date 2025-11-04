"""Utility functions for StockTrim MCP Server."""

from __future__ import annotations

from typing import TypeVar

from stocktrim_public_api_client.client_types import Unset

T = TypeVar("T")


def unset_to_none(value: T | Unset) -> T | None:
    """Convert UNSET values to None for Pydantic compatibility.

    Args:
        value: Value that might be UNSET

    Returns:
        The value if not UNSET, otherwise None

    Example:
        >>> from stocktrim_public_api_client.client_types import UNSET
        >>> unset_to_none(UNSET)
        None
        >>> unset_to_none("test")
        'test'
        >>> unset_to_none(123)
        123
    """
    if isinstance(value, Unset):
        return None
    return value
