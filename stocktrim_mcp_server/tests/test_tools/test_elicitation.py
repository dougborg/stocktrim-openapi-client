"""Tests for the shared delete-tool elicitation helper."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from pydantic import BaseModel

from stocktrim_mcp_server.tools.elicitation import run_delete_elicitation


class _FakeDeleteResponse(BaseModel):
    success: bool
    message: str


def _make_helpers():
    """Build a (response_factory, on_accept) pair tracking the args passed in."""
    on_accept = AsyncMock(return_value=(True, "deleted ok"))

    def factory(success: bool, message: str) -> _FakeDeleteResponse:
        return _FakeDeleteResponse(success=success, message=message)

    return factory, on_accept


@pytest.mark.asyncio
async def test_accepted_success_prefixes_checkmark():
    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))
    factory, on_accept = _make_helpers()
    on_accept.return_value = (True, "supplier removed")

    result = await run_delete_elicitation(
        ctx,
        message="preview",
        entity_label="supplier WH-01",
        on_accept=on_accept,
        response_factory=factory,
    )

    assert isinstance(result, _FakeDeleteResponse)
    assert result.success is True
    assert result.message == "✅ supplier removed"
    on_accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_accepted_failure_preserves_raw_message():
    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))
    factory, on_accept = _make_helpers()
    on_accept.return_value = (False, "API rejected delete")

    result = await run_delete_elicitation(
        ctx,
        message="preview",
        entity_label="supplier WH-01",
        on_accept=on_accept,
        response_factory=factory,
    )

    assert result.success is False
    assert result.message == "API rejected delete"


@pytest.mark.asyncio
async def test_declined_skips_on_accept_and_includes_entity_label():
    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=DeclinedElicitation(data=None))
    factory, on_accept = _make_helpers()

    result = await run_delete_elicitation(
        ctx,
        message="preview",
        entity_label="supplier WH-01",
        on_accept=on_accept,
        response_factory=factory,
    )

    assert result.success is False
    assert result.message == "❌ Deletion of supplier WH-01 declined by user"
    on_accept.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancelled_skips_on_accept_and_includes_entity_label():
    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=CancelledElicitation(data=None))
    factory, on_accept = _make_helpers()

    result = await run_delete_elicitation(
        ctx,
        message="preview",
        entity_label="purchase order PO-42",
        on_accept=on_accept,
        response_factory=factory,
    )

    assert result.success is False
    assert result.message == "❌ Deletion of purchase order PO-42 cancelled by user"
    on_accept.assert_not_awaited()


@pytest.mark.asyncio
async def test_unexpected_response_falls_through_to_safety_branch():
    """Critical: any non-Accepted/Declined/Cancelled response must land in
    the safety branch (success=False), not silently invoke on_accept.

    Guards a destructive code path against unexpected fastmcp response types.
    """

    class UnknownResponse:
        pass

    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=UnknownResponse())
    factory, on_accept = _make_helpers()

    result = await run_delete_elicitation(
        ctx,
        message="preview",
        entity_label="sales orders for product X",
        on_accept=on_accept,
        response_factory=factory,
    )

    assert result.success is False
    assert (
        result.message
        == "Unexpected elicitation response for sales orders for product X"
    )
    on_accept.assert_not_awaited()
