"""Tests for product management service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.products import ProductService
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.products = MagicMock()
    return client


@pytest.fixture
def product_service(mock_client):
    """Create a ProductService instance with mock client."""
    return ProductService(mock_client)


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return ProductsResponseDto(
        product_id="WIDGET-001",
        id=123,
        product_code_readable="WIDGET-001",
        name="Test Widget",
        cost=10.0,
        price=20.0,
        discontinued=False,
    )


@pytest.fixture
def sample_products():
    """Create a list of sample products for testing."""
    return [
        ProductsResponseDto(
            product_id="WIDGET-001",
            product_code_readable="WIDGET-001",
            name="Widget One",
        ),
        ProductsResponseDto(
            product_id="WIDGET-002",
            product_code_readable="WIDGET-002",
            name="Widget Two",
        ),
        ProductsResponseDto(
            product_id="WIDGET-003",
            product_code_readable="WIDGET-003",
            name="Widget Three",
        ),
    ]


# ============================================================================
# Tests for get_by_code
# ============================================================================


@pytest.mark.asyncio
async def test_get_by_code_success(product_service, mock_client, sample_product):
    """Test successfully getting a product by code."""
    # Setup
    mock_client.products.find_by_code = AsyncMock(return_value=sample_product)

    # Execute
    result = await product_service.get_by_code("WIDGET-001")

    # Verify
    assert result == sample_product
    assert result.product_code_readable == "WIDGET-001"
    assert result.name == "Test Widget"
    mock_client.products.find_by_code.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_get_by_code_not_found(product_service, mock_client):
    """Test getting a product that doesn't exist returns None."""
    # Setup
    mock_client.products.find_by_code = AsyncMock(return_value=None)

    # Execute
    result = await product_service.get_by_code("NONEXISTENT")

    # Verify
    assert result is None
    mock_client.products.find_by_code.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_by_code_empty_code(product_service):
    """Test that empty code raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.get_by_code("")

    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.get_by_code("  ")


# ============================================================================
# Tests for find_by_exact_code
# ============================================================================


@pytest.mark.asyncio
async def test_find_by_exact_code_success(
    product_service, mock_client, sample_products
):
    """Test successfully finding products by exact code."""
    # Setup
    mock_client.products.find_by_exact_code = AsyncMock(return_value=sample_products)

    # Execute
    result = await product_service.find_by_exact_code("WIDGET-001")

    # Verify
    assert len(result) == 3
    assert result[0].product_code_readable == "WIDGET-001"
    assert result[1].product_code_readable == "WIDGET-002"
    assert result[2].product_code_readable == "WIDGET-003"
    mock_client.products.find_by_exact_code.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_find_by_exact_code_no_results(product_service, mock_client):
    """Test finding products when no products match."""
    # Setup
    mock_client.products.find_by_exact_code = AsyncMock(return_value=[])

    # Execute
    result = await product_service.find_by_exact_code("NONEXISTENT")

    # Verify
    assert len(result) == 0
    assert result == []
    mock_client.products.find_by_exact_code.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_find_by_exact_code_empty(product_service):
    """Test that empty code raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.find_by_exact_code("")

    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.find_by_exact_code("  ")


# ============================================================================
# Tests for create
# ============================================================================


@pytest.mark.asyncio
async def test_create_success(product_service, mock_client, sample_product):
    """Test successfully creating a product."""
    # Setup
    mock_client.products.create = AsyncMock(return_value=sample_product)

    # Execute
    result = await product_service.create(
        code="WIDGET-001",
        description="Test Widget",
        cost_price=10.0,
        selling_price=20.0,
    )

    # Verify
    assert result == sample_product
    assert result.product_code_readable == "WIDGET-001"
    assert result.name == "Test Widget"
    mock_client.products.create.assert_called_once()

    # Verify the DTO that was passed
    call_args = mock_client.products.create.call_args
    dto = call_args[0][0]
    assert isinstance(dto, ProductsRequestDto)
    assert dto.product_id == "WIDGET-001"
    assert dto.product_code_readable == "WIDGET-001"
    assert dto.name == "Test Widget"
    assert dto.cost == 10.0
    assert dto.price == 20.0


@pytest.mark.asyncio
async def test_create_empty_code(product_service):
    """Test that empty code raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.create(code="", description="Test")

    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.create(code="  ", description="Test")


@pytest.mark.asyncio
async def test_create_empty_description(product_service):
    """Test that empty description raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product description cannot be empty"):
        await product_service.create(code="WIDGET-001", description="")

    with pytest.raises(ValueError, match="Product description cannot be empty"):
        await product_service.create(code="WIDGET-001", description="  ")


@pytest.mark.asyncio
async def test_create_optional_prices(product_service, mock_client, sample_product):
    """Test creating a product without prices."""
    # Setup
    mock_client.products.create = AsyncMock(return_value=sample_product)

    # Execute
    result = await product_service.create(
        code="WIDGET-001",
        description="Test Widget",
    )

    # Verify
    assert result == sample_product
    mock_client.products.create.assert_called_once()

    # Verify the DTO has None for prices
    call_args = mock_client.products.create.call_args
    dto = call_args[0][0]
    assert dto.cost is None
    assert dto.price is None


@pytest.mark.asyncio
async def test_create_failure(product_service, mock_client):
    """Test handling of creation failure."""
    # Setup
    mock_client.products.create = AsyncMock(return_value=None)

    # Execute & Verify
    with pytest.raises(Exception, match="Failed to create product"):
        await product_service.create(
            code="WIDGET-001",
            description="Test Widget",
        )


# ============================================================================
# Tests for delete
# ============================================================================


@pytest.mark.asyncio
async def test_delete_success(product_service, mock_client, sample_product):
    """Test successfully deleting a product."""
    # Setup
    mock_client.products.find_by_code = AsyncMock(return_value=sample_product)
    mock_client.products.delete = AsyncMock()

    # Execute
    success, message = await product_service.delete("WIDGET-001")

    # Verify
    assert success is True
    assert "deleted successfully" in message
    assert "WIDGET-001" in message
    mock_client.products.find_by_code.assert_called_once_with("WIDGET-001")
    mock_client.products.delete.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_delete_not_found(product_service, mock_client):
    """Test deleting a product that doesn't exist."""
    # Setup
    mock_client.products.find_by_code = AsyncMock(return_value=None)

    # Execute
    success, message = await product_service.delete("NONEXISTENT")

    # Verify
    assert success is False
    assert "not found" in message
    assert "NONEXISTENT" in message
    mock_client.products.find_by_code.assert_called_once_with("NONEXISTENT")
    # delete should not be called if product doesn't exist
    mock_client.products.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_empty_code(product_service):
    """Test that empty code raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.delete("")

    with pytest.raises(ValueError, match="Product code cannot be empty"):
        await product_service.delete("  ")
