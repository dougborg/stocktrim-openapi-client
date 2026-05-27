"""Tests for the PurchaseOrders helper class."""

from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_public_api_client.generated.models.purchase_order_response_dto import (
    PurchaseOrderResponseDto,
)
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


def test_get_purchase_order_handles_null_supplier_and_line_items():
    """Regression for issue #214.

    StockTrim's API has been observed returning purchase orders with both
    ``supplier`` and ``purchaseOrderLineItems`` set to ``null`` (reproducer:
    audit log 2026-05-27, PO-01066). The OpenAPI spec documents these as
    required + non-nullable, so the generated ``PurchaseOrderResponseDto``
    previously crashed in ``from_dict`` when trying to call
    ``PurchaseOrderSupplier.from_dict(None)`` and iterate ``None``. Both
    fields must now parse without raising and round-trip to ``None``."""
    payload = {
        "id": 1066,
        "referenceNumber": "PO-01066",
        "supplier": None,
        "purchaseOrderLineItems": None,
    }

    dto = PurchaseOrderResponseDto.from_dict(payload)

    assert dto.id == 1066
    assert dto.reference_number == "PO-01066"
    assert dto.supplier is None
    assert dto.purchase_order_line_items is None
