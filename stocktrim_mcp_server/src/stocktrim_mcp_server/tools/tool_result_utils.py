"""Helpers for building :class:`fastmcp.tools.ToolResult` responses.

Per MCP-Apps SEP-1865, ``content`` IS the model context the LLM reads, and
``structured_content`` is for UI binding (and is *not* added to model
context). For tools without a Prefab UI, both channels carry the same
JSON-serialized response: ``content`` as indented JSON for LLM context and
eyeball-debug, ``structured_content`` as a plain dict for programmatic
consumers that want to branch on response shape without re-parsing.

This module previously rendered hand-written Jinja2 markdown into the
``content`` channel. That pattern caused silent drift bugs across the
sibling katana-openapi-client project (their #565) — adding a field to
the response model degraded any host that consumed the markdown channel,
because the markdown formatter forgot to render the new field. JSON
content has no formatter to forget.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from fastmcp.tools import ToolResult
from pydantic import BaseModel

if TYPE_CHECKING:
    from prefab_ui.app import PrefabApp

ResponseT = TypeVar("ResponseT", bound=BaseModel)


def make_json_result(response: BaseModel) -> ToolResult:
    """Build a ``ToolResult`` for a tool with no Prefab UI.

    Use this for tools whose response is purely data — no rich card layer.
    Sibling of :func:`make_tool_result` (which handles the UI-emitting
    case). The two helpers differ in both the ``content`` formatting and
    the ``structured_content`` payload type, so don't assume they're
    interchangeable.

    Args:
        response: The Pydantic response model. ``model_dump_json(indent=2)``
            becomes ``content`` (LLM context); ``model_dump(mode="json")``
            becomes ``structured_content`` (programmatic consumers).

    Returns:
        A :class:`ToolResult` whose two channels carry the same payload in
        different shapes. Round-trips through :func:`unwrap_tool_result`
        for tests.
    """
    return ToolResult(
        content=response.model_dump_json(indent=2),
        structured_content=response.model_dump(mode="json"),
    )


def make_tool_result(response: BaseModel, *, ui: PrefabApp) -> ToolResult:
    """Build a ``ToolResult`` for a UI-emitting tool (reserved for future use).

    Per SEP-1865, ``content`` carries the JSON the LLM reads (no indent —
    UI hosts re-render anyway), and ``structured_content`` carries the
    ``PrefabApp`` envelope (NOT the data dict). Sibling of
    :func:`make_json_result`.
    """
    return ToolResult(
        content=response.model_dump_json(),
        structured_content=ui,
    )


def unwrap_tool_result(result: ToolResult, model_class: type[ResponseT]) -> ResponseT:
    """Recover the typed Pydantic response from a :class:`ToolResult`.

    Tests use this to assert against the typed model rather than dict keys.

    Args:
        result: The ``ToolResult`` produced by :func:`make_json_result`.
        model_class: The Pydantic model class to rebuild.

    Raises:
        ValueError: If ``result.structured_content`` is missing.
        pydantic.ValidationError: If the structured payload doesn't match
            ``model_class``.
    """
    if result.structured_content is None:
        raise ValueError(
            "ToolResult has no structured_content; did the tool use make_json_result()?"
        )
    return model_class.model_validate(result.structured_content)


def tool_result_text(result: ToolResult) -> str:
    """Coerce ``ToolResult.content`` to a single string for tests / logging.

    ``content`` may be a plain string or a ``list[ContentBlock]`` (e.g.
    ``TextContent``); join the latter into one string so callers don't have
    to special-case the shape.
    """
    if isinstance(result.content, str):
        return result.content
    return "\n".join(getattr(c, "text", str(c)) for c in result.content)
