"""Tests for the PurchaseOrders helper class."""

from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_public_api_client.helpers.purchase_orders import PurchaseOrders


@pytest.mark.asyncio
async def test_get_all_returns_empty_list_on_404(monkeypatch):
    """StockTrim returns 404 (not 200-with-empty-array) when there are no
    purchase orders. The helper must translate this to an empty list."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.parsed = None

    async_mock = AsyncMock(return_value=mock_response)

    import stocktrim_public_api_client.generated.api.purchase_orders.get_api_purchase_orders as get_module

    monkeypatch.setattr(get_module, "asyncio_detailed", async_mock)

    purchase_orders = PurchaseOrders(Mock())
    result = await purchase_orders.get_all()

    assert result == []
    async_mock.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_reference_returns_none_on_404(monkeypatch):
    """When filtering by reference number returns 404, find_by_reference
    should yield None (via the empty-list translation in get_all)."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.parsed = None

    async_mock = AsyncMock(return_value=mock_response)

    import stocktrim_public_api_client.generated.api.purchase_orders.get_api_purchase_orders as get_module

    monkeypatch.setattr(get_module, "asyncio_detailed", async_mock)

    purchase_orders = PurchaseOrders(Mock())
    result = await purchase_orders.find_by_reference("MISSING-PO")

    assert result is None
