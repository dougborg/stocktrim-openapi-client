"""Unit tests for the ``ToolResult`` helpers, decoupled from any tool's
business logic.

These tests pin the JSON-content + structured_content shape that
``make_json_result`` is contractually required to produce. The migrated
tool tests (e.g. ``test_urgent_orders``) exercise the helper indirectly,
but if those tests break it's hard to tell whether the helper or the
tool's business logic changed — direct unit tests give a clearer failure
signal when ``make_json_result`` itself drifts.
"""

from __future__ import annotations

import json

import pytest
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field, ValidationError

from stocktrim_mcp_server.tools.tool_result_utils import (
    make_json_result,
    tool_result_text,
    unwrap_tool_result,
)


class _Sample(BaseModel):
    """Minimal model with mixed types to exercise model_dump_json behavior."""

    name: str = Field(description="A name field")
    count: int = Field(description="An integer count")
    ratio: float | None = Field(default=None, description="An optional ratio")
    tags: list[str] = Field(default_factory=list, description="A list of tags")


def test_make_json_result_content_is_indented_json() -> None:
    """``content`` must be ``model_dump_json(indent=2)`` so LLM context is
    human-readable."""
    sample = _Sample(name="widget", count=3, ratio=0.5, tags=["a", "b"])
    result = make_json_result(sample)

    assert isinstance(result, ToolResult)
    text = tool_result_text(result)
    assert text == sample.model_dump_json(indent=2)
    # Defensive: ensure the indent is actually applied.
    assert "\n  " in text


def test_make_json_result_structured_content_is_dict_dump() -> None:
    """``structured_content`` must be ``model_dump(mode="json")`` (a dict),
    not the model itself, so programmatic consumers can branch on shape."""
    sample = _Sample(name="widget", count=3)
    result = make_json_result(sample)

    assert isinstance(result.structured_content, dict)
    assert result.structured_content == sample.model_dump(mode="json")


def test_make_json_result_round_trips_via_unwrap() -> None:
    """The helpers form a round-trip: dump → ToolResult → recover same model."""
    original = _Sample(name="widget", count=3, ratio=0.5, tags=["x"])
    result = make_json_result(original)

    recovered = unwrap_tool_result(result, _Sample)
    assert recovered == original


def test_unwrap_tool_result_raises_on_missing_structured_content() -> None:
    """If somebody returns a ``ToolResult`` without using ``make_json_result``,
    the unwrap helper should fail loudly rather than silently returning
    a partial model."""
    bad_result = ToolResult(content="just a string", structured_content=None)

    with pytest.raises(ValueError, match="structured_content"):
        unwrap_tool_result(bad_result, _Sample)


def test_unwrap_tool_result_raises_on_schema_mismatch() -> None:
    """If the structured payload doesn't match the requested model, the
    Pydantic ValidationError surfaces — drift between tool and test should
    be loud, not silent."""

    class _Other(BaseModel):
        unrelated: int

    sample = _Sample(name="widget", count=3)
    result = make_json_result(sample)

    with pytest.raises(ValidationError):
        unwrap_tool_result(result, _Other)


def test_make_json_result_handles_optional_and_default_fields() -> None:
    """Defaulted and unset optional fields must serialize consistently in
    both channels (catches ``model_dump`` vs ``model_dump_json`` divergence
    on Pydantic optionals)."""
    sample = _Sample(name="bare", count=0)
    result = make_json_result(sample)

    parsed = json.loads(tool_result_text(result))
    assert parsed == result.structured_content
    assert parsed["ratio"] is None
    assert parsed["tags"] == []
