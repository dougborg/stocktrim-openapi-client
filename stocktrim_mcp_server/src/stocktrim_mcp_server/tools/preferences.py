"""Session-scoped preferences for stocktrim MCP tools.

Persists user filter/behavior preferences across multiple tool calls in the same
MCP session via FastMCP v3's ``ctx.set_state`` / ``ctx.get_state``. Workflow
tools that take filter arguments (``category``, ``location_code``,
``days_threshold``) fall back to stored preferences when an arg is omitted, so
the user can say "use category=Widgets" once and subsequent tools inherit it.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypeVar

from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

STATE_KEY = "stocktrim.preferences"

T = TypeVar("T")

PreferenceKey = Literal[
    "category",
    "location_code",
    "supplier_code",
    "days_threshold",
    "dry_run",
]


class SessionPreferences(BaseModel):
    """User preferences scoped to the current MCP session.

    All fields are optional. ``None`` means "not set" — workflow tools fall
    back to their hard-coded default when the field is unset both here and in
    the call's explicit args.
    """

    category: str | None = Field(
        default=None, description="Default product category filter"
    )
    location_code: str | None = Field(
        default=None, description="Default single-location filter"
    )
    supplier_code: str | None = Field(
        default=None, description="Default supplier filter"
    )
    days_threshold: int | None = Field(
        default=None,
        description="Default days-until-stockout threshold for urgent-orders queries",
    )
    dry_run: bool = Field(
        default=False,
        description="When True, mutation tools log what they would do but skip the API call",
    )


async def load_preferences(ctx: Context) -> SessionPreferences:
    """Read the current session preferences (empty defaults if never set)."""
    raw = await ctx.get_state(STATE_KEY)
    if raw is None:
        return SessionPreferences()
    # State round-trips as a plain dict (set_state default is JSON-serializable).
    return SessionPreferences.model_validate(raw)


async def save_preferences(ctx: Context, prefs: SessionPreferences) -> None:
    """Persist preferences for the rest of this MCP session."""
    await ctx.set_state(STATE_KEY, prefs.model_dump())


def resolve(
    explicit: T | None,
    prefs: SessionPreferences,
    attr: PreferenceKey,
    default: T,
) -> T:
    """Pick the first non-None of: explicit arg → stored preference → tool default.

    Use this in workflow tools where a request field defaults to ``None`` so
    the impl can distinguish "user didn't specify" from "user said no value."

    ``attr`` is typed as a ``Literal`` of the ``SessionPreferences`` field
    names so typos are caught by the type checker rather than silently
    falling through to ``default`` at runtime.
    """
    if explicit is not None:
        return explicit
    pref_val = getattr(prefs, attr, None)
    if pref_val is not None:
        return pref_val
    return default


# ============================================================================
# Tool: set_preferences
# ============================================================================


class SetPreferencesRequest(BaseModel):
    """Partial update of session preferences.

    Only fields you provide are written; omitted-or-``None`` fields keep
    their current stored value (the impl uses ``model_dump(exclude_none=True)``
    so explicit ``None`` is treated the same as "omitted" and cannot clear an
    existing preference). To clear a preference today, set it to a sentinel
    your workflow ignores (e.g. empty string for ``category``) or call the
    relevant tool with an explicit empty/zero argument instead.
    """

    category: str | None = Field(
        default=None, description="New category filter (omit to keep current)"
    )
    location_code: str | None = Field(
        default=None, description="New single-location filter (omit to keep current)"
    )
    supplier_code: str | None = Field(
        default=None, description="New supplier filter (omit to keep current)"
    )
    days_threshold: int | None = Field(
        default=None,
        description="New default days-until-stockout threshold (omit to keep current)",
    )
    dry_run: bool | None = Field(
        default=None,
        description="Enable/disable dry-run mode for mutation tools (omit to keep current)",
    )


class PreferencesResponse(BaseModel):
    """Response wrapper so the typed payload round-trips through
    ``unwrap_tool_result``."""

    preferences: SessionPreferences


@unpack_pydantic_params
async def set_preferences(
    request: Annotated[SetPreferencesRequest, Unpack()], context: Context
) -> ToolResult:
    """Update session preferences. Returns the merged preferences after the
    update so the caller can confirm the new state.

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, PreferencesResponse)``.
    """
    current = await load_preferences(context)
    update = request.model_dump(exclude_none=True)
    merged = current.model_copy(update=update)
    await save_preferences(context, merged)
    return make_json_result(PreferencesResponse(preferences=merged))


# ============================================================================
# Tool: get_preferences
# ============================================================================


@unpack_pydantic_params
async def get_preferences(context: Context) -> ToolResult:
    """Return the current session preferences (empty defaults if never set).

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, PreferencesResponse)``.
    """
    prefs = await load_preferences(context)
    return make_json_result(PreferencesResponse(preferences=prefs))


# ============================================================================
# Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register session preference tools with the FastMCP server."""
    mcp.tool()(set_preferences)
    mcp.tool()(get_preferences)


__all__ = [
    "STATE_KEY",
    "PreferenceKey",
    "PreferencesResponse",
    "SessionPreferences",
    "SetPreferencesRequest",
    "get_preferences",
    "load_preferences",
    "register_tools",
    "resolve",
    "save_preferences",
    "set_preferences",
]
