"""Helpers for building :class:`fastmcp.tools.ToolResult` responses with both
human-readable markdown and machine-readable structured payloads.

Why: LLM clients render JSON awkwardly in chat. ``ToolResult`` lets a tool
return both rendered markdown (``content``) and the typed Pydantic dump
(``structured_content``) so each consumer reads what suits it.

Templates live in ``stocktrim_mcp_server/templates/`` as ``.md.j2`` files in
domain-grouped subdirectories (e.g. ``workflows/urgent_orders/review.md.j2``)
and are rendered by :func:`stocktrim_mcp_server.templates.render_template`.
"""

from __future__ import annotations

from typing import Any, TypeVar

from fastmcp.tools import ToolResult
from pydantic import BaseModel

from stocktrim_mcp_server.templates import render_template

ResponseT = TypeVar("ResponseT", bound=BaseModel)


def make_tool_result(
    response: BaseModel,
    template_path: str,
    **template_vars: Any,
) -> ToolResult:
    """Build a ``ToolResult`` from a Pydantic response and a Jinja2 template.

    The response model is exposed inside the template as ``response``. Extra
    keyword args are passed through; passing ``response=`` is a programming
    error and will raise (Python's standard duplicate-keyword behavior).

    Args:
        response: The Pydantic response model. Its ``.model_dump(mode="json")``
            becomes the ``structured_content`` payload, which round-trips
            through :func:`unwrap_tool_result` for tests.
        template_path: Template path relative to ``templates/`` without the
            ``.md.j2`` suffix (e.g. ``"workflows/urgent_orders/review"``).
        **template_vars: Extra variables to expose in the template.

    Returns:
        A :class:`ToolResult` with both content (rendered markdown) and
        structured_content (the response dict).
    """
    markdown = render_template(template_path, response=response, **template_vars)
    return ToolResult(
        content=markdown,
        structured_content=response.model_dump(mode="json"),
    )


def unwrap_tool_result(result: ToolResult, model_class: type[ResponseT]) -> ResponseT:
    """Recover the typed Pydantic response from a :class:`ToolResult`.

    Tests use this to assert against the typed model rather than dict keys.

    Args:
        result: The ``ToolResult`` produced by :func:`make_tool_result`.
        model_class: The Pydantic model class to rebuild.

    Raises:
        ValueError: If ``result.structured_content`` is missing.
        pydantic.ValidationError: If the structured payload doesn't match
            ``model_class``.
    """
    if result.structured_content is None:
        raise ValueError(
            "ToolResult has no structured_content; did the tool use make_tool_result()?"
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
