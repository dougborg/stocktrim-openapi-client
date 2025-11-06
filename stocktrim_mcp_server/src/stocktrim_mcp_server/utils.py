"""Utility functions for StockTrim MCP Server."""

from __future__ import annotations

from enum import IntEnum
from typing import TypeVar

from stocktrim_public_api_client.client_types import Unset

T = TypeVar("T")


def unset_to_none(value: T | Unset) -> T | None:
    """Convert UNSET values to None for Pydantic compatibility.

    The OpenAPI-generated client uses UNSET as a sentinel value to distinguish
    between "field not provided" and "field explicitly set to None". Pydantic
    models expect None for optional fields, so this helper converts UNSET to None.

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


def get_status_name(status: IntEnum | None | Unset) -> str | None:
    """Get the name of an IntEnum status, handling None and UNSET values.

    This helper safely extracts the name from IntEnum status fields (like
    PurchaseOrderStatus) while properly handling None and UNSET sentinel values.

    Args:
        status: IntEnum status value, None, or UNSET

    Returns:
        The status name as a string if status is a valid IntEnum, None otherwise

    Example:
        >>> from stocktrim_public_api_client.client_types import UNSET
        >>> from enum import IntEnum
        >>> class Status(IntEnum):
        ...     DRAFT = 0
        ...     APPROVED = 1
        >>> get_status_name(Status.DRAFT)
        'DRAFT'
        >>> get_status_name(None)
        None
        >>> get_status_name(UNSET)
        None
    """
    if status not in (None, Unset()):
        return status.name
    return None
