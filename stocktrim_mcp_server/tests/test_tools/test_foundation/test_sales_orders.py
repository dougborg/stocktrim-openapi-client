"""Tests for sales order management foundation tools."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

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
    """Extend mock context with sales_orders helper."""
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.sales_orders = AsyncMock()
    mock_client.sales_orders.create = AsyncMock()
    mock_client.sales_orders.get_all = AsyncMock()
    mock_client.sales_orders.get_for_product = AsyncMock()
    mock_client.sales_orders.delete_for_product = AsyncMock()
    return mock_context


# ============================================================================
# Test create_sales_order
# ============================================================================


@pytest.mark.asyncio
async def test_create_sales_order_success(extended_mock_context, sample_sales_order):
    """Test successfully creating a sales order."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.create.return_value = sample_sales_order

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
    mock_client.sales_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_sales_order_minimal(extended_mock_context, sample_sales_order):
    """Test creating a sales order with minimal required fields."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    minimal_order = SalesOrderResponseDto(
        id=790,
        product_id="prod-456",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=5.0,
    )
    mock_client.sales_orders.create.return_value = minimal_order

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
    # Execute and verify
    request = CreateSalesOrderRequest(
        product_id="prod-123",
        order_date=datetime(2024, 1, 15, 10, 0, 0),
        quantity=0.0,
    )
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        await create_sales_order(request, extended_mock_context)


# ============================================================================
# Test get_sales_orders
# ============================================================================


@pytest.mark.asyncio
async def test_get_sales_orders_all(extended_mock_context, sample_sales_order):
    """Test getting all sales orders."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_all.return_value = [
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
    mock_client.sales_orders.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_sales_orders_by_product(extended_mock_context, sample_sales_order):
    """Test getting sales orders filtered by product ID."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_for_product.return_value = [sample_sales_order]

    # Execute
    request = GetSalesOrdersRequest(product_id="prod-123")
    response = await get_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert len(response.sales_orders) == 1
    assert response.sales_orders[0].product_id == "prod-123"
    mock_client.sales_orders.get_for_product.assert_called_once_with("prod-123")


@pytest.mark.asyncio
async def test_get_sales_orders_empty_list(extended_mock_context):
    """Test getting sales orders when none exist."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_all.return_value = []

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
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    # API inconsistency: sometimes returns single object
    mock_client.sales_orders.get_all.return_value = sample_sales_order

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
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_all.return_value = [sample_sales_order]

    # Execute
    request = ListSalesOrdersRequest()
    response = await list_sales_orders(request, extended_mock_context)

    # Verify
    assert response.total_count == 1
    assert len(response.sales_orders) == 1
    mock_client.sales_orders.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_sales_orders_by_product(extended_mock_context, sample_sales_order):
    """Test listing sales orders filtered by product using alias."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_for_product.return_value = [sample_sales_order]

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
    mock_client = extended_mock_context.request_context.lifespan_context.client
    mock_client.sales_orders.get_for_product.return_value = [
        sample_sales_order,
        sample_sales_order,
    ]
    mock_client.sales_orders.delete_for_product.return_value = None

    # Execute
    request = DeleteSalesOrdersRequest(product_id="prod-123")
    response = await delete_sales_orders(request, extended_mock_context)

    # Verify
    assert response.success is True
    assert "prod-123" in response.message
    assert response.deleted_count == 2
    mock_client.sales_orders.get_for_product.assert_called_once_with("prod-123")
    mock_client.sales_orders.delete_for_product.assert_called_once_with("prod-123")


@pytest.mark.asyncio
async def test_delete_sales_orders_no_filter_raises_error(extended_mock_context):
    """Test deleting sales orders without filter raises error for safety."""
    # Execute and verify
    request = DeleteSalesOrdersRequest()
    with pytest.raises(ValueError, match="product_id is required for deletion"):
        await delete_sales_orders(request, extended_mock_context)


@pytest.mark.asyncio
async def test_delete_sales_orders_single_object_count(
    extended_mock_context, sample_sales_order
):
    """Test deleting sales orders when get returns single object."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    # API returns single object instead of list
    mock_client.sales_orders.get_for_product.return_value = sample_sales_order
    mock_client.sales_orders.delete_for_product.return_value = None

    # Execute
    request = DeleteSalesOrdersRequest(product_id="prod-123")
    response = await delete_sales_orders(request, extended_mock_context)

    # Verify
    assert response.success is True
    assert response.deleted_count == 1


@pytest.mark.asyncio
async def test_delete_sales_orders_empty_result_count(extended_mock_context):
    """Test deleting sales orders when get returns None/empty."""
    # Setup
    mock_client = extended_mock_context.request_context.lifespan_context.client
    # API returns None
    mock_client.sales_orders.get_for_product.return_value = None
    mock_client.sales_orders.delete_for_product.return_value = None

    # Execute
    request = DeleteSalesOrdersRequest(product_id="prod-123")
    response = await delete_sales_orders(request, extended_mock_context)

    # Verify
    assert response.success is True
    assert response.deleted_count == 0
