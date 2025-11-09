"""Test configuration and fixtures for StockTrim MCP Server tests."""

from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from stocktrim_mcp_server.services.customers import CustomerService
from stocktrim_mcp_server.services.inventory import InventoryService
from stocktrim_mcp_server.services.locations import LocationService
from stocktrim_mcp_server.services.products import ProductService
from stocktrim_mcp_server.services.purchase_orders import PurchaseOrderService
from stocktrim_mcp_server.services.sales_orders import SalesOrderService
from stocktrim_mcp_server.services.suppliers import SupplierService
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context with autospec'd service mocks.

    This fixture uses create_autospec to ensure tests can only mock
    methods that actually exist on the service classes, preventing
    bugs where tests pass but production code fails.
    """
    context = MagicMock()
    context.request_context = MagicMock()

    # Create a mock ServerContext with autospec'd services
    lifespan_context = MagicMock()

    # Create mock client (keep as MagicMock since it's from external library)
    mock_client = MagicMock()

    # Mock client helpers (these are from the generated client)
    mock_client.products = MagicMock()
    mock_client.products.find_by_code = AsyncMock()
    mock_client.products.create = AsyncMock()

    mock_client.suppliers = MagicMock()
    mock_client.suppliers.create_one = AsyncMock()

    mock_client.order_plan = MagicMock()
    mock_client.order_plan.query = AsyncMock()

    # Create autospec'd service instances
    # These will enforce interface compliance and fail if tests try to mock non-existent methods
    lifespan_context.client = mock_client
    lifespan_context.products = create_autospec(ProductService, instance=True)
    lifespan_context.customers = create_autospec(CustomerService, instance=True)
    lifespan_context.suppliers = create_autospec(SupplierService, instance=True)
    lifespan_context.locations = create_autospec(LocationService, instance=True)
    lifespan_context.inventory = create_autospec(InventoryService, instance=True)
    lifespan_context.purchase_orders = create_autospec(
        PurchaseOrderService, instance=True
    )
    lifespan_context.sales_orders = create_autospec(SalesOrderService, instance=True)

    context.request_context.lifespan_context = lifespan_context

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
