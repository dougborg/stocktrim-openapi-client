"""Tests for sales order bulk endpoint migration.

This test verifies that the sales order create method properly uses
the PUT /SalesOrdersBulk endpoint instead of POST /SalesOrders.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_public_api_client.generated.models.sales_order_request_dto import (
    SalesOrderRequestDto,
)
from stocktrim_public_api_client.generated.models.sales_order_response_dto import (
    SalesOrderResponseDto,
)
from stocktrim_public_api_client.generated.models.sales_order_with_line_items_request_dto import (
    SalesOrderWithLineItemsRequestDto,
)
from stocktrim_public_api_client.helpers.sales_orders import SalesOrders


@pytest.mark.asyncio
async def test_create_uses_bulk_endpoint(monkeypatch):
    """Test that create() uses PUT /SalesOrdersBulk endpoint."""
    # Mock the bulk endpoint
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.parsed = SalesOrderResponseDto(
        id=123,
        product_id="WIDGET-001",
        order_date=datetime(2025, 1, 15),
        quantity=10.0,
        external_reference_id="SO-001",
    )

    async_mock = AsyncMock(return_value=mock_response)

    # Mock the client
    mock_client = Mock()

    # Patch the bulk endpoint
    import stocktrim_public_api_client.generated.api.sales_orders_bulk.put_api_sales_orders_bulk as bulk_module

    monkeypatch.setattr(bulk_module, "asyncio_detailed", async_mock)

    # Create helper instance
    sales_orders = SalesOrders(mock_client)

    # Create a sales order request
    order = SalesOrderRequestDto(
        product_id="WIDGET-001",
        order_date=datetime(2025, 1, 15),
        quantity=10.0,
        external_reference_id="SO-001",
        unit_price=20.0,
        location_code="LOC-001",
        location_name="Warehouse 1",
        customer_code="CUST-001",
        customer_name="Test Customer",
    )

    # Call create
    result = await sales_orders.create(order)

    # Verify the bulk endpoint was called
    async_mock.assert_called_once()
    call_args = async_mock.call_args

    # Check that it was called with the right client
    assert call_args.kwargs["client"] == mock_client

    # Check that it was called with a bulk request
    bulk_request = call_args.kwargs["body"]
    assert isinstance(bulk_request, SalesOrderWithLineItemsRequestDto)

    # Verify the bulk request has the order as a line item
    assert bulk_request.sale_order_line_items is not None
    assert len(bulk_request.sale_order_line_items) == 1
    assert bulk_request.sale_order_line_items[0] == order

    # Verify the bulk request has the order's header fields
    assert bulk_request.order_date == order.order_date
    assert bulk_request.location_code == order.location_code
    assert bulk_request.location_name == order.location_name
    assert bulk_request.customer_code == order.customer_code
    assert bulk_request.customer_name == order.customer_name

    # Verify the result
    assert result.id == 123
    assert result.product_id == "WIDGET-001"


@pytest.mark.asyncio
async def test_create_handles_minimal_order(monkeypatch):
    """Test that create() works with minimal required fields."""
    # Mock the bulk endpoint
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.parsed = SalesOrderResponseDto(
        id=456,
        product_id="WIDGET-002",
        order_date=datetime(2025, 2, 1),
        quantity=5.0,
    )

    async_mock = AsyncMock(return_value=mock_response)

    # Mock the client
    mock_client = Mock()

    # Patch the bulk endpoint
    import stocktrim_public_api_client.generated.api.sales_orders_bulk.put_api_sales_orders_bulk as bulk_module

    monkeypatch.setattr(bulk_module, "asyncio_detailed", async_mock)

    # Create helper instance
    sales_orders = SalesOrders(mock_client)

    # Create a minimal sales order request (only required fields)
    order = SalesOrderRequestDto(
        product_id="WIDGET-002",
        order_date=datetime(2025, 2, 1),
        quantity=5.0,
    )

    # Call create
    result = await sales_orders.create(order)

    # Verify the bulk endpoint was called
    async_mock.assert_called_once()
    call_args = async_mock.call_args

    # Check the bulk request structure
    bulk_request = call_args.kwargs["body"]
    assert isinstance(bulk_request, SalesOrderWithLineItemsRequestDto)
    assert bulk_request.sale_order_line_items is not None
    assert len(bulk_request.sale_order_line_items) == 1

    # Verify the result
    assert result.id == 456
    assert result.product_id == "WIDGET-002"
