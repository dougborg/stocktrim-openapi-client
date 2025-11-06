"""Tests for product foundation tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.foundation.products import (
    CreateProductRequest,
    DeleteProductRequest,
    GetProductRequest,
    SearchProductsRequest,
    create_product,
    delete_product,
    get_product,
    search_products,
)
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
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
    request = GetProductRequest(code="WIDGET-001")
    response = await get_product(request, mock_product_context)

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
    request = GetProductRequest(code="MISSING")
    response = await get_product(request, mock_product_context)

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
    request = GetProductRequest(code="OLD-001")
    response = await get_product(request, mock_product_context)

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
async def test_search_products_success(mock_product_context, sample_product):
    """Test successfully searching products."""
    # Setup
    product2 = ProductsResponseDto(
        product_id="WIDGET-002",
        product_code_readable="WIDGET-002",
        name="Red Widget",
        discontinued=False,
        cost=16.00,
        price=26.00,
    )
    services = mock_product_context.request_context.lifespan_context
    services.products.search.return_value = [sample_product, product2]

    # Execute
    request = SearchProductsRequest(prefix="WIDGET")
    response = await search_products(request, mock_product_context)

    # Verify
    assert response.total_count == 2
    assert len(response.products) == 2
    assert response.products[0].code == "WIDGET-001"
    assert response.products[1].code == "WIDGET-002"

    services.products.search.assert_called_once_with("WIDGET")


@pytest.mark.asyncio
async def test_search_products_empty(mock_product_context):
    """Test searching products with no matches."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.search.return_value = []

    # Execute
    request = SearchProductsRequest(prefix="NONEXISTENT")
    response = await search_products(request, mock_product_context)

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
    request = CreateProductRequest(
        code="WIDGET-001",
        description="Blue Widget",
        cost_price=15.50,
        selling_price=25.00,
    )
    response = await create_product(request, mock_product_context)

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
    request = CreateProductRequest(
        code="MIN-001",
        description="Minimal Product",
    )
    response = await create_product(request, mock_product_context)

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
    request = CreateProductRequest(
        code="",
        description="Test",
    )
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await create_product(request, mock_product_context)


# ============================================================================
# Test delete_product
# ============================================================================


@pytest.mark.asyncio
async def test_delete_product_success(mock_product_context):
    """Test successfully deleting a product."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.delete.return_value = (
        True,
        "Product WIDGET-001 deleted successfully",
    )

    # Execute
    request = DeleteProductRequest(code="WIDGET-001")
    response = await delete_product(request, mock_product_context)

    # Verify
    assert response.success is True
    assert "deleted successfully" in response.message
    assert "WIDGET-001" in response.message

    services.products.delete.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_delete_product_not_found(mock_product_context):
    """Test deleting a product that doesn't exist."""
    # Setup
    services = mock_product_context.request_context.lifespan_context
    services.products.delete.return_value = (False, "Product MISSING not found")

    # Execute
    request = DeleteProductRequest(code="MISSING")
    response = await delete_product(request, mock_product_context)

    # Verify
    assert response.success is False
    assert "not found" in response.message

    services.products.delete.assert_called_once_with("MISSING")
