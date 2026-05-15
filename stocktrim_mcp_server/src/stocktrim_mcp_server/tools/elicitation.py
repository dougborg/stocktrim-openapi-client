"""Shared MCP elicitation helpers for destructive tools."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from fastmcp import Context
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from pydantic import BaseModel

R = TypeVar("R", bound=BaseModel)


async def run_delete_elicitation(
    context: Context,
    *,
    message: str,
    entity_label: str,
    on_accept: Callable[[], Awaitable[tuple[bool, str]]],
    response_factory: Callable[[bool, str], R],
) -> R:
    """Run the standard MCP elicitation flow for a destructive delete tool.

    Wraps the four-arm match block (Accepted / Declined / Cancelled / fallthrough)
    that every ``_delete_*_impl`` repeats. ``on_accept`` performs the actual
    deletion and must return a ``(success, message)`` tuple; the helper formats
    the user-facing message and delegates response construction to
    ``response_factory``, which preserves the concrete ``Delete*Response`` type
    at the call site (so callers don't need a cast).

    Args:
        context: FastMCP request context used to issue the elicitation.
        message: Preview text shown to the user before they confirm.
        entity_label: User-facing label inserted into declined/cancelled/
            unexpected messages (e.g. ``"supplier WH-01"`` or
            ``"sales orders for product P123"``).
        on_accept: Async callable invoked when the user accepts. Must return
            ``(success, message)`` from the underlying service delete.
        response_factory: Constructor for the concrete response model;
            called with ``(success, formatted_message)``.

    Returns:
        The response model produced by ``response_factory``.
    """
    result = await context.elicit(message=message, response_type=None)
    match result:
        case AcceptedElicitation():
            success, msg = await on_accept()
            return response_factory(success, f"✅ {msg}" if success else msg)
        case DeclinedElicitation():
            return response_factory(
                False, f"❌ Deletion of {entity_label} declined by user"
            )
        case CancelledElicitation():
            return response_factory(
                False, f"❌ Deletion of {entity_label} cancelled by user"
            )
        case _:
            return response_factory(
                False, f"Unexpected elicitation response for {entity_label}"
            )
