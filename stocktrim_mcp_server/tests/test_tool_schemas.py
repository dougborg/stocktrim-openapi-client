"""Schema-shape invariants for every registered MCP tool.

This module is the regression net for GH #116 (flatten workflow-tool schemas).
It snapshots ``inputSchema`` for every registered tool and asserts that no tool
exposes the legacy ``{"request": {...}}`` wrapper. Spot-checks against one
foundation tool, one workflow tool, and one preferences tool lock in both
the flat shape and the preservation of ``Field(description=...)`` metadata.
"""

from __future__ import annotations

import pytest
from fastmcp.tools import Tool

from stocktrim_mcp_server.server import mcp
from stocktrim_mcp_server.tools.workflows.urgent_orders import (
    review_urgent_order_requirements,
)


@pytest.fixture
async def registered_tools() -> dict[str, Tool]:
    """Return ``{name: Tool}`` for every tool registered on the FastMCP server."""
    tools = await mcp.list_tools()
    return {t.name: t for t in tools}


# ---------------------------------------------------------------------------
# Global invariants — no tool should expose the legacy wrapper.
# ---------------------------------------------------------------------------


async def test_no_tool_exposes_request_wrapper(
    registered_tools: dict[str, Tool],
) -> None:
    """No tool's top-level properties should be exactly ``{"request"}``.

    This is the core invariant from GH #116. Before the fix, the 9 workflow
    tools had ``{"properties": {"request": {...}}, "required": ["request"]}``.
    After flattening, no tool should ever produce that shape again.
    """
    offenders = []
    for name, tool in registered_tools.items():
        schema = tool.parameters
        properties = schema.get("properties", {})
        if set(properties.keys()) == {"request"}:
            offenders.append(name)
    assert not offenders, (
        f"Tools still expose the legacy {{request: ...}} wrapper: {offenders}"
    )


async def test_no_tool_requires_only_request(
    registered_tools: dict[str, Tool],
) -> None:
    """No tool should have ``required == ["request"]``.

    Even if a tool defines other optional flat params, requiring ``request``
    as the sole field is a smell of the legacy wrapper shape.
    """
    offenders = []
    for name, tool in registered_tools.items():
        schema = tool.parameters
        required = schema.get("required", [])
        if required == ["request"]:
            offenders.append(name)
    assert not offenders, (
        f"Tools still mark `request` as the sole required field: {offenders}"
    )


# ---------------------------------------------------------------------------
# Spot checks — top-level keys + descriptions preserved.
# ---------------------------------------------------------------------------


async def test_foundation_tool_get_product_schema(
    registered_tools: dict[str, Tool],
) -> None:
    """Foundation tool ``get_product`` should be flat and have descriptions.

    The description-preservation side-fix means foundation tools now expose
    field descriptions that the pre-#116 ``Unpack`` machinery silently
    dropped. Confirm ``code`` has a non-empty description.
    """
    schema = registered_tools["get_product"].parameters
    assert set(schema["properties"].keys()) == {"code"}
    assert schema["required"] == ["code"]
    assert schema["properties"]["code"]["description"], (
        "get_product.code should now carry the FieldInfo description "
        "(previously dropped by Unpack); see #116"
    )


async def test_workflow_tool_review_urgent_orders_schema(
    registered_tools: dict[str, Tool],
) -> None:
    """Workflow tool should expose flat top-level keys, not a `request` wrapper."""
    schema = registered_tools["review_urgent_order_requirements"].parameters
    keys = set(schema["properties"].keys())
    assert "request" not in keys
    assert keys == {
        "days_threshold",
        "location_codes",
        "category",
        "supplier_codes",
    }
    # Description preservation
    assert schema["properties"]["days_threshold"]["description"], (
        "days_threshold should expose its FieldInfo description"
    )


async def test_preferences_tool_set_preferences_schema(
    registered_tools: dict[str, Tool],
) -> None:
    """Preferences tool ``set_preferences`` should be flat with descriptions."""
    schema = registered_tools["set_preferences"].parameters
    assert "request" not in schema["properties"]
    # At least one property must carry a non-empty description.
    assert any(prop.get("description") for prop in schema["properties"].values()), (
        "set_preferences should expose FieldInfo descriptions on its flat params"
    )


# ---------------------------------------------------------------------------
# #116 symptom repro — flat kwargs succeed, malformed legacy shape fails clearly.
# ---------------------------------------------------------------------------


async def test_flat_kwargs_invocation_succeeds(mock_context) -> None:
    """Calling a workflow tool with flat kwargs should reconstruct the model.

    This is the "happy path" for the symptom shape in #116 — the client
    that *correctly* serializes flat fields per the new schema. With the
    autospec'd ``mock_context`` (and a stubbed empty order-plan query), the
    call should succeed and return a structured response rather than raise.
    """
    # Stub the underlying order-plan query to return an empty list so the
    # workflow short-circuits to an empty response (no urgent items).
    mock_context.request_context.lifespan_context.client.order_plan.query.return_value = []

    # The flat-kwargs path validates, reconstructs the model, and runs the
    # wrapped function end-to-end without raising.
    result = await review_urgent_order_requirements(days_threshold=30, ctx=mock_context)
    assert result is not None, (
        "Flat-kwargs invocation should produce a structured response"
    )


async def test_legacy_string_request_produces_field_level_error(mock_context) -> None:
    """Repro of #116: ``request="<json string>"`` should error with field-level diagnostics.

    Before the fix, FastMCP would reject this with a generic ``"request"``
    error from Pydantic. After flattening (and the 0.16.0 removal of the
    transitional fallback), the wrapper rejects the legacy shape immediately
    with a ``TypeError`` that names the model's flat fields rather than the
    wrapper.
    """
    # Sending a string-serialized request payload — the legacy wrapper shape
    # is rejected immediately with a clear field-naming TypeError.
    with pytest.raises(TypeError) as exc_info:
        await review_urgent_order_requirements(
            request='{"days_threshold": 30}',
            ctx=mock_context,
        )
    msg = str(exc_info.value)
    # The error must name the actual flat field the caller should send so
    # the user gets actionable feedback (not a generic "request" complaint).
    assert "days_threshold" in msg, (
        f"Expected error to name the flat field `days_threshold`, got: {msg!r}"
    )
