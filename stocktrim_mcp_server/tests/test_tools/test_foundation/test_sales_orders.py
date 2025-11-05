"""Tests for sales order management foundation tools."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from stocktrim_mcp_server.tools.foundation.sales_orders import (
    CreateSalesOrderRequest,
    DeleteSalesOrdersRequest,
    GetSalesOrdersRequest,
    ListSalesOrdersRequest,
    create_sales_order,
    delete_sales_orders,
    get_sales_orders,
    list_sales_orders,
)
from stocktrim_public_api_client.generated.models.sales_order_response_dto import (
    SalesOrderResponseDto,
)


@pytest.fixture
def sample_sales_order():
    """Create a sample sales order for testing."""
    return SalesOrderResponseDto(
        id=789,
        product_id="prod-123",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=10.0,
        external_reference_id="SO-2024-001",
        unit_price=29.99,
        location_code="WAREHOUSE-A",
        location_name="Main Warehouse",
        customer_code="CUST-001",
        customer_name="Test Customer",
        location_id=1,
    )


@pytest.fixture
def extended_mock_context(mock_context):
    """Extend mock context with sales_orders service."""
    from stocktrim_mcp_server.services.sales_orders import SalesOrderService

    mock_service = AsyncMock(spec=SalesOrderService)
    mock_context.request_context.lifespan_context.sales_orders = mock_service
    return mock_context


# ============================================================================
# Test create_sales_order
# ============================================================================


@pytest.mark.asyncio
async def test_create_sales_order_success(extended_mock_context, sample_sales_order):
    """Test successfully creating a sales order."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.create.return_value = sample_sales_order

    # Execute
    request = CreateSalesOrderRequest(
        product_id="prod-123",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=10.0,
        customer_code="CUST-001",
        unit_price=29.99,
    )
    response = await create_sales_order(request, extended_mock_context)

    # Verify
    assert response.id == 789
    assert response.product_id == "prod-123"
    assert response.quantity == 10.0
    assert response.customer_code == "CUST-001"
    assert response.unit_price == 29.99
    mock_service.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_sales_order_minimal(extended_mock_context, sample_sales_order):
    """Test creating a sales order with minimal required fields."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    minimal_order = SalesOrderResponseDto(
        id=790,
        product_id="prod-456",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=5.0,
    )
    mock_service.create.return_value = minimal_order

    # Execute
    request = CreateSalesOrderRequest(
        product_id="prod-456",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=5.0,
    )
    response = await create_sales_order(request, extended_mock_context)

    # Verify
    assert response.id == 790
    assert response.product_id == "prod-456"
    assert response.quantity == 5.0
    assert response.customer_code is None
    assert response.unit_price is None


@pytest.mark.asyncio
async def test_create_sales_order_empty_product_id(extended_mock_context):
    """Test creating a sales order with empty product_id raises error."""
    # Setup - service layer validates and raises ValueError
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.create.side_effect = ValueError("Product ID cannot be empty")

    # Execute and verify
    request = CreateSalesOrderRequest(
        product_id="",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=10.0,
    )
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        await create_sales_order(request, extended_mock_context)


@pytest.mark.asyncio
async def test_create_sales_order_zero_quantity(extended_mock_context):
    """Test creating a sales order with zero quantity raises error."""
    # Pydantic validation prevents zero quantity at the request level
    with pytest.raises(ValidationError):
        CreateSalesOrderRequest(
            product_id="prod-123",
            order_date=datetime(2024, 1, 15, 10, 0, 0),
            quantity=0.0,
        )


# ============================================================================
# Test get_sales_orders
# ============================================================================


@pytest.mark.asyncio
async def test_get_sales_orders_all(extended_mock_context, sample_sales_order):
    """Test getting all sales orders."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = [
        sample_sales_order,
        SalesOrderResponseDto(
            id=790,
            product_id="prod-456",
            order_date=datetime(2024, 1, 16, 10, 0, 0),
            quantity=5.0,
        ),
    ]

    # Execute
    request = GetSalesOrdersRequest()
    response = await get_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 2
    assert len(response.sales_orders) == 2
    assert response.sales_orders[0].id == 789
    assert response.sales_orders[1].id == 790
    mock_service.get_all.assert_called_once_with(product_id=None)


@pytest.mark.asyncio
async def test_get_sales_orders_by_product(extended_mock_context, sample_sales_order):
    """Test getting sales orders filtered by product ID."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = [sample_sales_order]

    # Execute
    request = GetSalesOrdersRequest(product_id="prod-123")
    response = await get_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert len(response.sales_orders) == 1
    assert response.sales_orders[0].product_id == "prod-123"
    mock_service.get_all.assert_called_once_with(product_id="prod-123")


@pytest.mark.asyncio
async def test_get_sales_orders_empty_list(extended_mock_context):
    """Test getting sales orders when none exist."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = []

    # Execute
    request = GetSalesOrdersRequest()
    response = await get_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 0
    assert len(response.sales_orders) == 0


@pytest.mark.asyncio
async def test_get_sales_orders_single_object(
    extended_mock_context, sample_sales_order
):
    """Test getting sales orders when API returns single object instead of list."""
    # Setup - service layer already handles this, so it returns a list
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = [sample_sales_order]

    # Execute
    request = GetSalesOrdersRequest()
    response = await get_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert len(response.sales_orders) == 1
    assert response.sales_orders[0].id == 789


# ============================================================================
# Test list_sales_orders (alias)
# ============================================================================


@pytest.mark.asyncio
async def test_list_sales_orders_all(extended_mock_context, sample_sales_order):
    """Test listing all sales orders using alias."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = [sample_sales_order]

    # Execute
    request = ListSalesOrdersRequest()
    response = await list_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert len(response.sales_orders) == 1
    mock_service.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_sales_orders_by_product(extended_mock_context, sample_sales_order):
    """Test listing sales orders filtered by product using alias."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.get_all.return_value = [sample_sales_order]

    # Execute
    request = ListSalesOrdersRequest(product_id="prod-123")
    response = await list_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert response.sales_orders[0].product_id == "prod-123"


# ============================================================================
# Test delete_sales_orders
# ============================================================================


@pytest.mark.asyncio
async def test_delete_sales_orders_by_product(
    extended_mock_context, sample_sales_order
):
    """Test deleting sales orders for a specific product."""
    # Setup
    mock_service = extended_mock_context.request_context.lifespan_context.sales_orders
    mock_service.delete_for_product.return_value = (
        True,
        "Sales orders for product prod-123 deleted successfully",
    )

    # Execute
    request = DeleteSalesOrdersRequest(product_id="prod-123")
    response = await delete_sales_orders(request, extended_mock_context)

    # Verify
    assert response.success is True
    assert "prod-123" in response.message
    mock_service.delete_for_product.assert_called_once_with("prod-123")


@pytest.mark.asyncio
async def test_delete_sales_orders_no_filter_raises_error(extended_mock_context):
    """Test deleting sales orders without filter raises error for safety."""
    # Execute and verify
    request = DeleteSalesOrdersRequest()
    with pytest.raises(ValueError, match="product_id is required for deletion"):
        await delete_sales_orders(request, extended_mock_context)
