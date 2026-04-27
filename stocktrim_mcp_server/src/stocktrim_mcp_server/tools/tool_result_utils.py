"""Helpers for building :class:`fastmcp.tools.ToolResult` responses with both
human-readable markdown and machine-readable structured payloads.

Background: under fastmcp v3, tools that return a plain Pydantic model are
serialized to JSON for the MCP protocol. That works fine for programmatic
consumers, but LLM clients render JSON awkwardly in chat. ``ToolResult`` lets
a tool return *both* — operators/agents read ``structured_content``; LLMs
render ``content`` (markdown) directly.

Usage::

    from stocktrim_mcp_server.tools.tool_result_utils import (
        make_tool_result,
    )

    response = ReviewUrgentOrdersResponse(...)
    return make_tool_result(
        response,
        template_name="urgent_orders_review",
        # extra Jinja vars (response is auto-exposed as ``response`` and ``r``):
        days_threshold=request.days_threshold,
    )

Templates live in ``stocktrim_mcp_server/templates/`` as ``.md.j2`` files and
are rendered by :func:`stocktrim_mcp_server.templates.render_template`.
"""

from __future__ import annotations

from typing import Any

from fastmcp.tools import ToolResult
from pydantic import BaseModel

from stocktrim_mcp_server.templates import render_template


def make_tool_result(
    response: BaseModel,
    template_name: str,
    **template_vars: Any,
) -> ToolResult:
    """Build a ``ToolResult`` from a Pydantic response and a Jinja2 template.

    The response model is exposed inside the template under two names:

    - ``response`` — the full Pydantic instance (use for explicit access)
    - ``r`` — same instance, shorter alias (use in tight templates)

    Args:
        response: The Pydantic response model. Its ``.model_dump()`` becomes
            the ``structured_content`` payload.
        template_name: Template basename (without ``.md.j2``). Resolved by
            :func:`stocktrim_mcp_server.templates.render_template`.
        **template_vars: Extra variables to expose in the template.

    Returns:
        A :class:`ToolResult` with both content (rendered markdown) and
        structured_content (the response dict).
    """
    markdown = render_template(
        template_name, response=response, r=response, **template_vars
    )
    return ToolResult(
        content=markdown,
        structured_content=response.model_dump(mode="json"),
    )
