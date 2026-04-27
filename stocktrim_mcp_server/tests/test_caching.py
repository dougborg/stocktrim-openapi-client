"""Tests for ResponseCachingMiddleware wiring on the StockTrim MCP server.

Behavior of the caching middleware itself is fastmcp's responsibility; these
tests verify our wiring choices: the middleware is registered, mutating tools
are excluded, and TTLs are sane.
"""

from __future__ import annotations

import pytest
from fastmcp.server.middleware.caching import ResponseCachingMiddleware


@pytest.fixture(autouse=True)
def _credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide fake creds so server.py can import without raising at lifespan time."""
    monkeypatch.setenv("STOCKTRIM_API_AUTH_ID", "test-id")
    monkeypatch.setenv("STOCKTRIM_API_AUTH_SIGNATURE", "test-sig")


def _get_caching_middleware() -> ResponseCachingMiddleware:
    """Import the configured server and return its caching middleware."""
    # Import is inside the function so fixtures run first.
    from stocktrim_mcp_server.server import mcp

    matching = [m for m in mcp.middleware if isinstance(m, ResponseCachingMiddleware)]
    assert matching, "ResponseCachingMiddleware not registered on mcp"
    return matching[0]


def test_response_caching_middleware_registered() -> None:
    """ResponseCachingMiddleware is wired on the production server."""
    assert _get_caching_middleware() is not None


def test_mutating_tools_are_excluded_from_cache() -> None:
    """Every create/delete/set/configure tool is in the cache exclusion list.

    Caching a mutation would return a no-op success on subsequent calls within
    the TTL — silent data loss. The exclusion list is the safety guard.
    """
    middleware = _get_caching_middleware()
    excluded = set(middleware._call_tool_settings.get("excluded_tools", []))

    # Every mutation surface the server exposes today.
    expected = {
        "create_product",
        "delete_product",
        "create_supplier",
        "delete_supplier",
        "create_purchase_order",
        "delete_purchase_order",
        "create_sales_order",
        "delete_sales_orders",
        "create_location",
        "set_product_inventory",
        "configure_product",
        "products_configure_lifecycle",
        "manage_forecast_group",
        "update_forecast_settings",
        "forecasts_update_and_monitor",
        "create_supplier_with_products",
        "generate_purchase_orders_from_urgent_items",
    }
    missing = expected - excluded
    assert not missing, f"mutating tools missing from cache exclusion: {missing}"


def test_call_tool_ttl_is_bounded() -> None:
    """call_tool TTL stays under 10 minutes — bounds the staleness window."""
    middleware = _get_caching_middleware()
    ttl = middleware._call_tool_settings.get("ttl")
    assert ttl is not None, "call_tool TTL should be set explicitly"
    assert 0 < ttl <= 600, f"call_tool TTL out of bounds: {ttl}"


def test_read_resource_ttl_favors_freshness() -> None:
    """read_resource TTL is short — resources are for discovery, freshness wins."""
    middleware = _get_caching_middleware()
    ttl = middleware._read_resource_settings.get("ttl")
    assert ttl is not None, "read_resource TTL should be set explicitly"
    assert 0 < ttl <= 120, f"read_resource TTL too long for discovery: {ttl}"
