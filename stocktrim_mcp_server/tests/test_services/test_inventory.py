"""Tests for inventory service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.inventory import InventoryService
from stocktrim_public_api_client.generated.models import (
    PurchaseOrderLineItem,
    PurchaseOrderResponseDto,
    PurchaseOrderSupplier,
)


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    mock = MagicMock()
    mock.inventory = MagicMock()
    mock.inventory.set_for_product = AsyncMock()
    return mock


@pytest.fixture
def inventory_service(mock_client):
    """Create an InventoryService instance with mock client."""
    return InventoryService(mock_client)


@pytest.fixture
def sample_purchase_order_response():
    """Create a sample PurchaseOrderResponseDto for testing."""
    supplier = PurchaseOrderSupplier(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
    )
    line_item = PurchaseOrderLineItem(
        product_id="WIDGET-001",
        quantity=10.0,
    )
    return PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=[line_item],
    )


@pytest.mark.asyncio
async def test_set_for_product_success(
    inventory_service, mock_client, sample_purchase_order_response
):
    """Test successfully setting inventory for a product."""
    # Setup
    mock_client.inventory.set_for_product.return_value = sample_purchase_order_response

    # Execute
    result = await inventory_service.set_for_product(
        product_id="WIDGET-001",
        stock_on_hand=50.0,
        stock_on_order=100.0,
        location_code="WAREHOUSE-A",
        location_name="Warehouse A",
    )

    # Verify
    assert result == sample_purchase_order_response
    mock_client.inventory.set_for_product.assert_called_once()

    # Check the call arguments
    call_args = mock_client.inventory.set_for_product.call_args
    assert call_args.kwargs["product_id"] == "WIDGET-001"
    assert call_args.kwargs["stock_on_hand"] == 50.0
    assert call_args.kwargs["stock_on_order"] == 100.0
    assert call_args.kwargs["location_code"] == "WAREHOUSE-A"
    assert call_args.kwargs["location_name"] == "Warehouse A"


@pytest.mark.asyncio
async def test_set_for_product_with_optional_params(
    inventory_service, mock_client, sample_purchase_order_response
):
    """Test setting inventory with some optional parameters."""
    # Setup
    mock_client.inventory.set_for_product.return_value = sample_purchase_order_response

    # Execute
    result = await inventory_service.set_for_product(
        product_id="WIDGET-001",
        stock_on_hand=50.0,
    )

    # Verify
    assert result == sample_purchase_order_response
    mock_client.inventory.set_for_product.assert_called_once()


@pytest.mark.asyncio
async def test_set_for_product_empty_product_id(inventory_service, mock_client):
    """Test error when product_id is empty."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await inventory_service.set_for_product(
            product_id="",
            stock_on_hand=50.0,
        )

    mock_client.inventory.set_for_product.assert_not_called()


@pytest.mark.asyncio
async def test_set_for_product_whitespace_product_id(inventory_service, mock_client):
    """Test error when product_id is only whitespace."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await inventory_service.set_for_product(
            product_id="   ",
            stock_on_hand=50.0,
        )

    mock_client.inventory.set_for_product.assert_not_called()


@pytest.mark.asyncio
async def test_set_for_product_api_error(inventory_service, mock_client):
    """Test handling of API errors."""
    # Setup
    mock_client.inventory.set_for_product.side_effect = Exception("API Error")

    # Execute & Verify
    with pytest.raises(Exception, match="API Error"):
        await inventory_service.set_for_product(
            product_id="WIDGET-001",
            stock_on_hand=50.0,
        )


@pytest.mark.asyncio
async def test_set_for_product_all_none_params(
    inventory_service, mock_client, sample_purchase_order_response
):
    """Test setting inventory with all optional params as None."""
    # Setup
    mock_client.inventory.set_for_product.return_value = sample_purchase_order_response

    # Execute
    result = await inventory_service.set_for_product(
        product_id="WIDGET-001",
        stock_on_hand=None,
        stock_on_order=None,
        location_code=None,
        location_name=None,
    )

    # Verify
    assert result == sample_purchase_order_response
    mock_client.inventory.set_for_product.assert_called_once()
