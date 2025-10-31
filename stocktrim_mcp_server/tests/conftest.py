"""Test configuration and fixtures for StockTrim MCP Server tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context with StockTrimClient."""
    context = MagicMock()
    context.request_context = MagicMock()
    context.request_context.lifespan_context = MagicMock()

    # Create mock client
    mock_client = MagicMock()

    # Mock products helper
    mock_client.products = MagicMock()
    mock_client.products.find_by_code = AsyncMock()
    mock_client.products.create = AsyncMock()

    # Mock suppliers helper
    mock_client.suppliers = MagicMock()
    mock_client.suppliers.create_one = AsyncMock()

    context.request_context.lifespan_context.client = mock_client

    return context


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return ProductsResponseDto(
        product_id="prod-123",
        id=123,
        product_code_readable="WIDGET-001",
        name="Test Widget",
        category="Electronics",
        discontinued=False,
        ignore_seasonality=False,
        lead_time=14,
        forecast_period=30,
        service_level=0.95,
        minimum_order_quantity=10.0,
    )


@pytest.fixture
def sample_supplier():
    """Create a sample supplier for testing."""
    return SupplierResponseDto(
        id=456,
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
    )
