"""Tests for product foundation tools."""

from unittest.mock import AsyncMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from stocktrim_mcp_server.tools.foundation.products import (
    create_product,
    delete_product,
    get_product,
    search_products,
)
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return ProductsResponseDto(
        product_id="WIDGET-001",
        product_code_readable="WIDGET-001",
        name="Blue Widget",
        discontinued=False,
        cost=15.50,
        price=25.00,
    )


@pytest.fixture
def mock_product_context(mock_context):
    """Extend mock_context with mock products service."""
    services = mock_context.request_context.lifespan_context
    services.products = AsyncMock()
    return mock_context


# ============================================================================
# Test get_product
# ============================================================================


@pytest.mark.asyncio
async def test_get_product_success(mock_product_context, sample_product):
    """Test successfully getting a product."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    # Execute
    response = await get_product(code="WIDGET-001", context=mock_product_context)

    # Verify
    assert response is not None
    assert response.code == "WIDGET-001"
    assert response.description == "Blue Widget"
    assert response.is_active is True
    assert response.cost_price == 15.50
    assert response.selling_price == 25.00

    services.products.get_by_code.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_get_product_not_found(mock_product_context):
    """Test getting a product that doesn't exist."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute
    response = await get_product(code="MISSING", context=mock_product_context)

    # Verify
    assert response is None
    services.products.get_by_code.assert_called_once_with("MISSING")


@pytest.mark.asyncio
async def test_get_product_discontinued(mock_product_context):
    """Test getting a discontinued product."""
    # Setup
    product = ProductsResponseDto(
        product_id="OLD-001",
        product_code_readable="OLD-001",
        name="Discontinued Item",
        discontinued=True,
        cost=UNSET,
        price=UNSET,
    )
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = product

    # Execute
    response = await get_product(code="OLD-001", context=mock_product_context)

    # Verify
    assert response is not None
    assert response.code == "OLD-001"
    assert response.is_active is False
    assert response.cost_price is None
    assert response.selling_price is None


# ============================================================================
# Test search_products
# ============================================================================


@pytest.mark.asyncio
async def test_search_products_success(mock_product_context):
    """Test successfully searching products with keyword search."""
    # Setup - create order plan results (SkuOptimizedResultsDto)
    order_plan_item1 = SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        name="Blue Widget",
        is_discontinued=False,
        sku_cost=15.50,
        sku_price=25.00,
    )
    order_plan_item2 = SkuOptimizedResultsDto(
        product_code="WIDGET-002",
        name="Red Widget",
        is_discontinued=False,
        sku_cost=16.00,
        sku_price=26.00,
    )
    services = mock_product_context.request_context.lifespan_context
    services.client.order_plan.query.return_value = [order_plan_item1, order_plan_item2]

    # Execute - using flattened parameters
    response = await search_products(
        search_query="widget", context=mock_product_context
    )

    # Verify
    assert response.total_count == 2
    assert len(response.products) == 2
    assert response.products[0].code == "WIDGET-001"
    assert response.products[0].description == "Blue Widget"
    assert response.products[1].code == "WIDGET-002"
    assert response.products[1].description == "Red Widget"

    # Verify order plan query was called with searchString
    services.client.order_plan.query.assert_called_once()
    # Get the filter criteria passed to query()
    call_args = services.client.order_plan.query.call_args
    filter_criteria = (
        call_args[0][0] if call_args[0] else call_args[1].get("filter_criteria")
    )
    assert filter_criteria.search_string == "widget"


@pytest.mark.asyncio
async def test_search_products_empty(mock_product_context):
    """Test searching products with no matches."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.client.order_plan.query.return_value = []

    # Execute - using flattened parameters
    response = await search_products(
        search_query="NONEXISTENT", context=mock_product_context
    )

    # Verify
    assert response.total_count == 0
    assert len(response.products) == 0


# ============================================================================
# Test create_product
# ============================================================================


@pytest.mark.asyncio
async def test_create_product_success(mock_product_context, sample_product):
    """Test successfully creating a product."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.create.return_value = sample_product

    # Execute
    response = await create_product(
        code="WIDGET-001",
        description="Blue Widget",
        cost_price=15.50,
        selling_price=25.00,
        context=mock_product_context,
    )

    # Verify
    assert response.code == "WIDGET-001"
    assert response.description == "Blue Widget"
    assert response.cost_price == 15.50
    assert response.selling_price == 25.00

    services.products.create.assert_called_once_with(
        code="WIDGET-001",
        description="Blue Widget",
        cost_price=15.50,
        selling_price=25.00,
    )


@pytest.mark.asyncio
async def test_create_product_minimal(mock_product_context):
    """Test creating a product with minimal fields."""
    # Setup
    product = ProductsResponseDto(
        product_id="MIN-001",
        product_code_readable="MIN-001",
        name="Minimal Product",
        discontinued=False,
        cost=UNSET,
        price=UNSET,
    )
    services = mock_product_context.request_context.lifespan_context
    services.products.create.return_value = product

    # Execute
    response = await create_product(
        code="MIN-001", description="Minimal Product", context=mock_product_context
    )

    # Verify
    assert response.code == "MIN-001"
    assert response.description == "Minimal Product"
    assert response.cost_price is None
    assert response.selling_price is None


@pytest.mark.asyncio
async def test_create_product_validation_error(mock_product_context):
    """Test creating a product when service raises validation error."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.create.side_effect = ValueError("Product code cannot be empty")

    # Execute & Verify
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await create_product(code="", description="Test", context=mock_product_context)


# ============================================================================
# Test delete_product (with elicitation)
# ============================================================================


@pytest.mark.asyncio
async def test_delete_product_not_found(mock_product_context):
    """Test deleting a product that doesn't exist."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute
    response = await delete_product(code="MISSING", context=mock_product_context)

    # Verify
    assert response.success is False
    assert "not found" in response.message
    assert "MISSING" in response.message


@pytest.mark.asyncio
async def test_delete_product_accepted(mock_product_context, sample_product):
    """Test deleting a product when user accepts confirmation."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product
    services.products.delete.return_value = (
        True,
        "Product WIDGET-001 deleted successfully",
    )
    mock_product_context.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))

    # Execute
    response = await delete_product(code="WIDGET-001", context=mock_product_context)

    # Verify
    assert response.success is True
    assert "✅" in response.message
    assert "deleted successfully" in response.message

    # Verify elicitation was called with preview
    mock_product_context.elicit.assert_called_once()
    elicit_args = mock_product_context.elicit.call_args
    assert "⚠️ Delete product" in elicit_args[1]["message"]
    assert "Blue Widget" in elicit_args[1]["message"]
    assert "Active" in elicit_args[1]["message"]

    # Verify deletion was called
    services.products.delete.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_delete_product_declined(mock_product_context, sample_product):
    """Test deleting a product when user declines confirmation."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product
    mock_product_context.elicit = AsyncMock(return_value=DeclinedElicitation(data=None))

    # Execute
    response = await delete_product(code="WIDGET-001", context=mock_product_context)

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "declined" in response.message
    assert "WIDGET-001" in response.message

    # Verify deletion was NOT called
    services.products.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_product_cancelled(mock_product_context, sample_product):
    """Test deleting a product when user cancels confirmation."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product
    mock_product_context.elicit = AsyncMock(
        return_value=CancelledElicitation(data=None)
    )

    # Execute
    response = await delete_product(code="WIDGET-001", context=mock_product_context)

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "cancelled" in response.message
    assert "WIDGET-001" in response.message

    # Verify deletion was NOT called
    services.products.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_product_discontinued_preview(mock_product_context):
    """Test that discontinued products show correct status in preview."""
    # Setup
    discontinued_product = ProductsResponseDto(
        product_id="OLD-001",
        product_code_readable="OLD-001",
        name="Discontinued Item",
        discontinued=True,
        cost=UNSET,
        price=UNSET,
    )
    services = mock_product_context.request_context.lifespan_context
    services.products.get_by_code.return_value = discontinued_product
    mock_product_context.elicit = AsyncMock(return_value=DeclinedElicitation(data=None))

    # Execute
    await delete_product(code="OLD-001", context=mock_product_context)

    # Verify elicitation preview shows discontinued status
    elicit_args = mock_product_context.elicit.call_args
    assert "🔴" in elicit_args[1]["message"]  # Red emoji for discontinued
    assert "Discontinued" in elicit_args[1]["message"]
