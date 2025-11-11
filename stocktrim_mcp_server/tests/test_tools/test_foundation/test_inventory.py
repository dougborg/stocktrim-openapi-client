"""Tests for inventory foundation tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.foundation.inventory import (
    set_product_inventory,
)


@pytest.fixture
def mock_inventory_context(mock_context):
    """Extend mock_context with mock inventory service."""
    services = mock_context.request_context.lifespan_context
    services.inventory = AsyncMock()
    return mock_context


# ============================================================================
# Test set_product_inventory
# ============================================================================


@pytest.mark.asyncio
async def test_set_product_inventory_success(mock_inventory_context):
    """Test successfully setting product inventory."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute
    response = await set_product_inventory(
        product_id="WIDGET-001",
        stock_on_hand=50.0,
        stock_on_order=100.0,
        location_code="WH-01",
        location_name="Main Warehouse",
        context=mock_inventory_context,
    )

    # Verify
    assert response.product_id == "WIDGET-001"
    assert response.stock_on_hand == 50.0
    assert response.stock_on_order == 100.0
    assert response.location_code == "WH-01"
    assert response.location_name == "Main Warehouse"

    services.inventory.set_for_product.assert_called_once_with(
        product_id="WIDGET-001",
        stock_on_hand=50.0,
        stock_on_order=100.0,
        location_code="WH-01",
        location_name="Main Warehouse",
    )


@pytest.mark.asyncio
async def test_set_product_inventory_minimal_fields(mock_inventory_context):
    """Test setting product inventory with only required field."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute
    response = await set_product_inventory(
        product_id="WIDGET-002", stock_on_hand=25.0, context=mock_inventory_context
    )

    # Verify
    assert response.product_id == "WIDGET-002"
    assert response.stock_on_hand == 25.0
    assert response.stock_on_order is None
    assert response.location_code is None
    assert response.location_name is None

    services.inventory.set_for_product.assert_called_once_with(
        product_id="WIDGET-002",
        stock_on_hand=25.0,
        stock_on_order=None,
        location_code=None,
        location_name=None,
    )


@pytest.mark.asyncio
async def test_set_product_inventory_zero_stock(mock_inventory_context):
    """Test setting product inventory to zero."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute
    response = await set_product_inventory(
        product_id="WIDGET-003",
        stock_on_hand=0.0,
        stock_on_order=0.0,
        context=mock_inventory_context,
    )

    # Verify
    assert response.product_id == "WIDGET-003"
    assert response.stock_on_hand == 0.0
    assert response.stock_on_order == 0.0


@pytest.mark.asyncio
async def test_set_product_inventory_negative_stock(mock_inventory_context):
    """Test setting product inventory with negative values (should be allowed)."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute - negative inventory can indicate issues but should be allowed
    response = await set_product_inventory(
        product_id="WIDGET-004", stock_on_hand=-10.0, context=mock_inventory_context
    )

    # Verify
    assert response.product_id == "WIDGET-004"
    assert response.stock_on_hand == -10.0


@pytest.mark.asyncio
async def test_set_product_inventory_with_location_only(mock_inventory_context):
    """Test setting inventory with location information."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute
    response = await set_product_inventory(
        product_id="WIDGET-005",
        stock_on_hand=75.0,
        location_code="WH-02",
        location_name="Secondary Warehouse",
        context=mock_inventory_context,
    )

    # Verify
    assert response.product_id == "WIDGET-005"
    assert response.stock_on_hand == 75.0
    assert response.location_code == "WH-02"
    assert response.location_name == "Secondary Warehouse"


@pytest.mark.asyncio
async def test_set_product_inventory_service_error(mock_inventory_context):
    """Test setting inventory when service raises an error."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.side_effect = Exception("API error")

    # Execute & Verify
    with pytest.raises(Exception, match="API error"):
        await set_product_inventory(
            product_id="WIDGET-ERROR",
            stock_on_hand=50.0,
            context=mock_inventory_context,
        )


@pytest.mark.asyncio
async def test_set_product_inventory_validation_error(mock_inventory_context):
    """Test setting inventory when service raises a validation error."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.side_effect = ValueError(
        "Product ID is required"
    )

    # Execute & Verify
    with pytest.raises(ValueError, match="Product ID is required"):
        await set_product_inventory(
            product_id="", stock_on_hand=50.0, context=mock_inventory_context
        )


@pytest.mark.asyncio
async def test_set_product_inventory_decimal_quantities(mock_inventory_context):
    """Test setting inventory with decimal quantities."""
    # Setup
    services = mock_inventory_context.request_context.lifespan_context
    services.inventory.set_for_product.return_value = None

    # Execute
    response = await set_product_inventory(
        product_id="WIDGET-006",
        stock_on_hand=12.5,
        stock_on_order=47.25,
        context=mock_inventory_context,
    )

    # Verify
    assert response.product_id == "WIDGET-006"
    assert response.stock_on_hand == 12.5
    assert response.stock_on_order == 47.25
