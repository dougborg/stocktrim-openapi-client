"""Tests for SalesOrderService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.sales_orders import SalesOrderService
from stocktrim_public_api_client.generated.models import SalesOrderResponseDto


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.sales_orders = MagicMock()
    client.sales_orders.create = AsyncMock()
    client.sales_orders.get_for_product = AsyncMock()
    client.sales_orders.get_all = AsyncMock()
    client.sales_orders.delete_for_product = AsyncMock()
    return client


@pytest.fixture
def sales_order_service(mock_client):
    """Create a SalesOrderService with mock client."""
    return SalesOrderService(mock_client)


@pytest.fixture
def sample_sales_order():
    """Create a sample sales order for testing."""
    return SalesOrderResponseDto(
        id=123,
        product_id="WIDGET-001",
        order_date=datetime(2025, 1, 15),
        quantity=10.0,
        external_reference_id="SO-001",
    )


# ============================================================================
# Test create
# ============================================================================


@pytest.mark.asyncio
async def test_create_success(sales_order_service, mock_client, sample_sales_order):
    """Test successfully creating a sales order."""
    mock_client.sales_orders.create.return_value = sample_sales_order

    result = await sales_order_service.create(
        product_id="WIDGET-001",
        order_date=datetime(2025, 1, 15),
        quantity=10.0,
    )

    assert result == sample_sales_order
    assert result.product_id == "WIDGET-001"
    assert result.quantity == 10.0
    mock_client.sales_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_with_all_params(sales_order_service, mock_client):
    """Test creating a sales order with all optional parameters."""
    created_order = SalesOrderResponseDto(
        id=123,
        product_id="WIDGET-001",
        order_date=datetime(2025, 1, 15),
        quantity=10.0,
        external_reference_id="SO-001",
        unit_price=20.0,
    )
    mock_client.sales_orders.create.return_value = created_order

    result = await sales_order_service.create(
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

    assert result.product_id == "WIDGET-001"
    assert result.quantity == 10.0
    assert result.unit_price == 20.0
    assert result.external_reference_id == "SO-001"
    mock_client.sales_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_empty_product_id(sales_order_service):
    """Test error when product_id is empty."""
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.create(
            product_id="",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        )

    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.create(
            product_id="   ",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        )


@pytest.mark.asyncio
async def test_create_invalid_quantity_zero(sales_order_service):
    """Test error when quantity is zero."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        await sales_order_service.create(
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=0,
        )


@pytest.mark.asyncio
async def test_create_invalid_quantity_negative(sales_order_service):
    """Test error when quantity is negative."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        await sales_order_service.create(
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=-5.0,
        )


@pytest.mark.asyncio
async def test_create_invalid_quantity_none(sales_order_service):
    """Test error when quantity is None."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        await sales_order_service.create(
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=None,
        )


@pytest.mark.asyncio
async def test_create_api_error(sales_order_service, mock_client):
    """Test handling of API errors during creation."""
    mock_client.sales_orders.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await sales_order_service.create(
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        )


# ============================================================================
# Test get_for_product
# ============================================================================


@pytest.mark.asyncio
async def test_get_for_product_success(sales_order_service, mock_client):
    """Test successfully getting sales orders for a product."""
    orders = [
        SalesOrderResponseDto(
            id=1,
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        ),
        SalesOrderResponseDto(
            id=2,
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 16),
            quantity=20.0,
        ),
    ]
    mock_client.sales_orders.get_for_product.return_value = orders

    result = await sales_order_service.get_for_product("WIDGET-001")

    assert len(result) == 2
    assert result[0].product_id == "WIDGET-001"
    assert result[1].product_id == "WIDGET-001"
    mock_client.sales_orders.get_for_product.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_get_for_product_not_found(sales_order_service, mock_client):
    """Test getting sales orders for a product with no results."""
    mock_client.sales_orders.get_for_product.return_value = []

    result = await sales_order_service.get_for_product("NONEXISTENT")

    assert len(result) == 0
    mock_client.sales_orders.get_for_product.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_for_product_empty_product_id(sales_order_service):
    """Test error when product_id is empty."""
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.get_for_product("")

    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.get_for_product("   ")


@pytest.mark.asyncio
async def test_get_for_product_api_error(sales_order_service, mock_client):
    """Test handling of API errors."""
    mock_client.sales_orders.get_for_product.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await sales_order_service.get_for_product("WIDGET-001")


# ============================================================================
# Test get_all
# ============================================================================


@pytest.mark.asyncio
async def test_get_all_success(sales_order_service, mock_client):
    """Test successfully getting all sales orders."""
    orders = [
        SalesOrderResponseDto(
            id=1,
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        ),
        SalesOrderResponseDto(
            id=2,
            product_id="WIDGET-002",
            order_date=datetime(2025, 1, 16),
            quantity=20.0,
        ),
    ]
    mock_client.sales_orders.get_all.return_value = orders

    result = await sales_order_service.get_all()

    assert len(result) == 2
    assert result[0].product_id == "WIDGET-001"
    assert result[1].product_id == "WIDGET-002"
    mock_client.sales_orders.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_empty(sales_order_service, mock_client):
    """Test getting all sales orders when none exist."""
    mock_client.sales_orders.get_all.return_value = []

    result = await sales_order_service.get_all()

    assert len(result) == 0
    mock_client.sales_orders.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_filtered_by_product(sales_order_service, mock_client):
    """Test getting sales orders filtered by product."""
    orders = [
        SalesOrderResponseDto(
            id=1,
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 15),
            quantity=10.0,
        ),
        SalesOrderResponseDto(
            id=2,
            product_id="WIDGET-001",
            order_date=datetime(2025, 1, 16),
            quantity=20.0,
        ),
    ]
    mock_client.sales_orders.get_for_product.return_value = orders

    result = await sales_order_service.get_all(product_id="WIDGET-001")

    assert len(result) == 2
    assert result[0].product_id == "WIDGET-001"
    assert result[1].product_id == "WIDGET-001"
    # Should call get_for_product when product_id is provided
    mock_client.sales_orders.get_for_product.assert_called_once_with("WIDGET-001")
    mock_client.sales_orders.get_all.assert_not_called()


@pytest.mark.asyncio
async def test_get_all_api_error(sales_order_service, mock_client):
    """Test handling of API errors."""
    mock_client.sales_orders.get_all.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await sales_order_service.get_all()


# ============================================================================
# Test delete_for_product
# ============================================================================


@pytest.mark.asyncio
async def test_delete_for_product_success(sales_order_service, mock_client):
    """Test successfully deleting sales orders for a product."""
    success, message = await sales_order_service.delete_for_product("WIDGET-001")

    assert success is True
    assert "deleted successfully" in message
    assert "WIDGET-001" in message
    mock_client.sales_orders.delete_for_product.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_delete_for_product_empty_product_id(sales_order_service):
    """Test error when product_id is empty."""
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.delete_for_product("")

    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await sales_order_service.delete_for_product("   ")


@pytest.mark.asyncio
async def test_delete_for_product_api_error(sales_order_service, mock_client):
    """Test handling of API errors during deletion."""
    mock_client.sales_orders.delete_for_product.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await sales_order_service.delete_for_product("WIDGET-001")
