"""Tests for session preferences (set/get + workflow tool fallback)."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.preferences import (
    STATE_KEY,
    PreferencesResponse,
    SessionPreferences,
    get_preferences,
    load_preferences,
    resolve,
    save_preferences,
    set_preferences,
)
from stocktrim_mcp_server.tools.tool_result_utils import unwrap_tool_result


@pytest.fixture
def stateful_context(mock_context):
    """Wrap mock_context so get_state/set_state act like a real session store."""
    store: dict[str, Any] = {}

    async def _get(key: str) -> Any:
        return store.get(key)

    async def _set(key: str, value: Any, *, serializable: bool = True) -> None:
        store[key] = value

    mock_context.get_state = AsyncMock(side_effect=_get)
    mock_context.set_state = AsyncMock(side_effect=_set)
    mock_context._state_store = store  # exposed for assertions
    return mock_context


# ============================================================================
# load_preferences / save_preferences
# ============================================================================


@pytest.mark.asyncio
async def test_load_preferences_returns_defaults_when_unset(mock_context):
    """get_state returns None → load_preferences returns empty defaults."""
    prefs = await load_preferences(mock_context)
    assert prefs == SessionPreferences()
    assert prefs.dry_run is False
    assert prefs.category is None


@pytest.mark.asyncio
async def test_save_then_load_round_trips(stateful_context):
    """Saved preferences survive a round-trip through ctx.set_state/get_state."""
    saved = SessionPreferences(
        category="Widgets",
        location_code="WH-01",
        days_threshold=14,
        dry_run=True,
    )
    await save_preferences(stateful_context, saved)

    loaded = await load_preferences(stateful_context)
    assert loaded == saved


@pytest.mark.asyncio
async def test_save_writes_json_serializable_dict(stateful_context):
    """state must hold a plain dict, not a Pydantic instance."""
    await save_preferences(
        stateful_context, SessionPreferences(category="Widgets", days_threshold=7)
    )
    raw = stateful_context._state_store[STATE_KEY]
    assert isinstance(raw, dict)
    assert raw["category"] == "Widgets"
    assert raw["days_threshold"] == 7


# ============================================================================
# resolve precedence
# ============================================================================


def test_resolve_explicit_arg_wins():
    prefs = SessionPreferences(category="from-prefs")
    assert resolve("explicit", prefs, "category", "default") == "explicit"


def test_resolve_falls_back_to_pref_when_arg_is_none():
    prefs = SessionPreferences(category="from-prefs")
    assert resolve(None, prefs, "category", "default") == "from-prefs"


def test_resolve_falls_back_to_default_when_neither_set():
    prefs = SessionPreferences()
    assert resolve(None, prefs, "category", "default") == "default"


def test_resolve_treats_zero_as_explicit_value():
    """0 is a real value, not absence — must not fall through to prefs/default."""
    prefs = SessionPreferences(days_threshold=14)
    assert resolve(0, prefs, "days_threshold", 30) == 0


# ============================================================================
# set_preferences / get_preferences tools
# ============================================================================


async def _call_set(**kwargs: Any) -> PreferencesResponse:
    result = await set_preferences(**kwargs)
    return unwrap_tool_result(result, PreferencesResponse)


async def _call_get(**kwargs: Any) -> PreferencesResponse:
    result = await get_preferences(**kwargs)
    return unwrap_tool_result(result, PreferencesResponse)


@pytest.mark.asyncio
async def test_set_preferences_stores_values(stateful_context):
    response = await _call_set(
        category="Widgets",
        location_code="WH-01",
        days_threshold=14,
        context=stateful_context,
    )
    assert response.preferences.category == "Widgets"
    assert response.preferences.location_code == "WH-01"
    assert response.preferences.days_threshold == 14
    # And it actually landed in the store.
    saved = await load_preferences(stateful_context)
    assert saved == response.preferences


@pytest.mark.asyncio
async def test_set_preferences_merges_with_existing(stateful_context):
    """Omitted fields keep their prior value (partial update)."""
    await save_preferences(
        stateful_context, SessionPreferences(category="Widgets", days_threshold=14)
    )
    response = await _call_set(location_code="WH-02", context=stateful_context)
    assert response.preferences.category == "Widgets"  # preserved
    assert response.preferences.days_threshold == 14  # preserved
    assert response.preferences.location_code == "WH-02"  # newly set


@pytest.mark.asyncio
async def test_set_preferences_can_toggle_dry_run(stateful_context):
    response = await _call_set(dry_run=True, context=stateful_context)
    assert response.preferences.dry_run is True
    response = await _call_set(dry_run=False, context=stateful_context)
    assert response.preferences.dry_run is False


@pytest.mark.asyncio
async def test_get_preferences_returns_current(stateful_context):
    await save_preferences(
        stateful_context,
        SessionPreferences(category="Widgets", days_threshold=14),
    )
    response = await _call_get(context=stateful_context)
    assert response.preferences.category == "Widgets"
    assert response.preferences.days_threshold == 14


@pytest.mark.asyncio
async def test_get_preferences_returns_defaults_when_unset(mock_context):
    response = await _call_get(context=mock_context)
    assert response.preferences == SessionPreferences()
