"""Tests for foundation resources."""

import pytest
from fastmcp.exceptions import ResourceError

from stocktrim_mcp_server.resources.foundation import (
    _get_customer_resource,
    _get_inventory_resource,
    _get_location_resource,
    _get_product_resource,
    _get_products_catalog_resource,
    _get_supplier_resource,
)
from stocktrim_public_api_client.generated.models.customer_dto import CustomerDto
from stocktrim_public_api_client.generated.models.location_response_dto import (
    LocationResponseDto,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)

# ============================================================================
# Fixtures
# ============================================================================


# Note: We use mock_context directly instead of overriding with AsyncMock
# to ensure autospec catches interface mismatches


# ============================================================================
# Tests for Product Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_product_resource_success(mock_context):
    """Test successfully retrieving a product resource."""
    # Setup
    services = mock_context.request_context.lifespan_context
    product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        name="Test Widget",
        cost=15.50,
        stock_on_hand=100,
        discontinued=False,
        ignore_seasonality=False,
    )
    services.products.get_by_code.return_value = product

    # Execute
    result = await _get_product_resource("WIDGET-001", mock_context)

    # Verify
    assert result["product_code"] == "WIDGET-001"
    assert result["name"] == "Test Widget"
    assert result["cost"] == 15.50
    assert result["stock_on_hand"] == 100
    assert result["discontinued"] is False
    assert result["ignore_seasonality"] is False  # False means forecasting is enabled
    services.products.get_by_code.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_get_product_resource_not_found(mock_context):
    """Test error when product doesn't exist."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute & Verify
    with pytest.raises(ResourceError, match="Product not found"):
        await _get_product_resource("NONEXISTENT", mock_context)


# ============================================================================
# Tests for Products Catalog Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_products_catalog_success(mock_context):
    """Test successfully retrieving products catalog."""
    # Setup
    services = mock_context.request_context.lifespan_context
    products = [
        ProductsResponseDto(
            product_id=f"prod-{i}",
            product_code_readable=f"WIDGET-{i:03d}",
            name=f"Widget {i}",
        )
        for i in range(1, 6)
    ]
    services.products.list_all.return_value = products

    # Execute
    result = await _get_products_catalog_resource(mock_context)

    # Verify
    assert result["total_shown"] == 5
    assert len(result["products"]) == 5
    assert result["products"][0]["product_code"] == "WIDGET-001"
    assert result["products"][0]["name"] == "Widget 1"
    services.products.list_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_products_catalog_limits_results(mock_context):
    """Test that catalog limits results to 50 items."""
    # Setup
    services = mock_context.request_context.lifespan_context
    # Return 100 products to verify the resource limits to 50 via slicing
    products = [
        ProductsResponseDto(
            product_id=f"prod-{i}",
            product_code_readable=f"WIDGET-{i:03d}",
            name=f"Widget {i}",
        )
        for i in range(1, 101)  # 100 products
    ]
    services.products.list_all.return_value = products

    # Execute
    result = await _get_products_catalog_resource(mock_context)

    # Verify - should limit to 50 via slicing
    assert len(result["products"]) == 50
    assert result["total_shown"] == 50
    assert "Limited to 50 products" in result["note"]
    services.products.list_all.assert_called_once()


# ============================================================================
# Tests for Customer Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_customer_resource_success(mock_context):
    """Test successfully retrieving a customer resource."""
    # Setup
    services = mock_context.request_context.lifespan_context
    customer = CustomerDto(
        code="CUST-001",
        name="Test Customer Inc",
        email_address="test@example.com",
        phone="555-0100",
        street_address="123 Main St",
        city="Portland",
        state="OR",
        post_code="97201",
    )
    services.customers.get_by_code.return_value = customer

    # Execute
    result = await _get_customer_resource("CUST-001", mock_context)

    # Verify
    assert result["customer_code"] == "CUST-001"
    assert result["name"] == "Test Customer Inc"
    assert result["email"] == "test@example.com"
    assert result["phone"] == "555-0100"
    assert result["address"]["street"] == "123 Main St"
    assert result["address"]["city"] == "Portland"
    services.customers.get_by_code.assert_called_once_with("CUST-001")


@pytest.mark.asyncio
async def test_get_customer_resource_not_found(mock_context):
    """Test error when customer doesn't exist."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.customers.get_by_code.return_value = None

    # Execute & Verify
    with pytest.raises(ResourceError, match="Customer not found"):
        await _get_customer_resource("NONEXISTENT", mock_context)


# ============================================================================
# Tests for Supplier Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_supplier_resource_success(mock_context):
    """Test successfully retrieving a supplier resource."""
    # Setup
    services = mock_context.request_context.lifespan_context
    supplier = SupplierResponseDto(
        supplier_code="SUP-001",
        supplier_name="Test Supplier Inc",
        email_address="orders@supplier.com",
        primary_contact_name="Jane Smith",
        default_lead_time=14,
    )
    services.suppliers.get_by_code.return_value = supplier

    # Execute
    result = await _get_supplier_resource("SUP-001", mock_context)

    # Verify
    assert result["supplier_code"] == "SUP-001"
    assert result["name"] == "Test Supplier Inc"
    assert result["email"] == "orders@supplier.com"
    assert result["primary_contact"] == "Jane Smith"
    assert result["default_lead_time"] == 14
    services.suppliers.get_by_code.assert_called_once_with("SUP-001")


@pytest.mark.asyncio
async def test_get_supplier_resource_not_found(mock_context):
    """Test error when supplier doesn't exist."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = None

    # Execute & Verify
    with pytest.raises(ResourceError, match="Supplier not found"):
        await _get_supplier_resource("NONEXISTENT", mock_context)


# ============================================================================
# Tests for Location Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_location_resource_success(mock_context):
    """Test successfully retrieving a location resource."""
    # Setup
    services = mock_context.request_context.lifespan_context
    location = LocationResponseDto(
        location_code="WH-001",
        location_name="Main Warehouse",
    )
    services.locations.list_all.return_value = [location]

    # Execute
    result = await _get_location_resource("WH-001", mock_context)

    # Verify
    assert result["location_code"] == "WH-001"
    assert result["name"] == "Main Warehouse"
    services.locations.list_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_location_resource_not_found(mock_context):
    """Test error when location doesn't exist."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.locations.list_all.return_value = []

    # Execute & Verify
    with pytest.raises(ResourceError, match="Location not found"):
        await _get_location_resource("NONEXISTENT", mock_context)


# ============================================================================
# Tests for Inventory Resource
# ============================================================================


@pytest.mark.asyncio
async def test_get_inventory_resource_success(mock_context, sample_product):
    """Test successfully retrieving inventory resource."""
    # Setup
    services = mock_context.request_context.lifespan_context
    location = LocationResponseDto(
        location_code="WH-001", location_name="Main Warehouse"
    )
    services.locations.list_all.return_value = [location]

    product_with_stock = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        stock_on_hand=150,
    )
    services.products.get_by_code.return_value = product_with_stock

    # Execute
    result = await _get_inventory_resource("WH-001", "WIDGET-001", mock_context)

    # Verify
    assert result["product_code"] == "WIDGET-001"
    assert result["location_code"] == "WH-001"
    assert result["quantity"] == 150
    assert "note" in result
    services.locations.list_all.assert_called_once()
    services.products.get_by_code.assert_called_once_with("WIDGET-001")


@pytest.mark.asyncio
async def test_get_inventory_resource_not_found(mock_context):
    """Test error when location doesn't exist."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.locations.list_all.return_value = []

    # Execute & Verify
    with pytest.raises(ResourceError, match="Location not found"):
        await _get_inventory_resource("NONEXISTENT", "WIDGET-001", mock_context)
