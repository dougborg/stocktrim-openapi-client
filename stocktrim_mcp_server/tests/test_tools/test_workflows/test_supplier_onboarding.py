"""Tests for supplier onboarding workflow tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.workflows.supplier_onboarding import (
    CreateSupplierWithProductsRequest,
    SupplierProductMapping,
    create_supplier_with_products,
)
from stocktrim_public_api_client.generated.models.product_supplier import (
    ProductSupplier,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)


@pytest.fixture
def mock_supplier_onboarding_context(mock_context):
    """Extend mock_context with suppliers, products services and client."""
    services = mock_context.request_context.lifespan_context
    services.suppliers = AsyncMock()
    services.products = AsyncMock()
    services.client = AsyncMock()
    services.client.products = AsyncMock()
    return mock_context


@pytest.mark.asyncio
async def test_create_supplier_with_products_success(
    mock_supplier_onboarding_context, sample_product, sample_supplier
):
    """Test successfully creating a supplier with product mappings."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        supplier_code="SUP-001",
        suppliers=[
            ProductSupplier(
                supplier_id="sup-456",
                supplier_name="Test Supplier",
                supplier_sku_code="SUP-SKU-001",
            )
        ],
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        is_active=True,
        product_mappings=[
            SupplierProductMapping(
                product_code="WIDGET-001",
                supplier_product_code="SUP-SKU-001",
                cost_price=15.50,
            )
        ],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - response is now markdown
    assert isinstance(response, str)
    assert "SUP-001" in response
    assert "Test Supplier" in response
    assert "456" in response  # sample_supplier has id=456
    assert "WIDGET-001" in response
    assert "✅" in response or "created successfully" in response.lower()

    services.suppliers.create.assert_called_once()
    services.products.get_by_code.assert_called_once_with("WIDGET-001")
    services.client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_supplier_with_products_multiple_mappings(
    mock_supplier_onboarding_context, sample_supplier
):
    """Test creating supplier with multiple product mappings."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    # Create two different products
    product1 = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[],
    )
    product2 = ProductsResponseDto(
        product_id="prod-456",
        product_code_readable="WIDGET-002",
        suppliers=[],
    )

    # Mock get_by_code to return different products
    async def mock_get_by_code(code):
        if code == "WIDGET-001":
            return product1
        elif code == "WIDGET-002":
            return product2
        return None

    services.products.get_by_code = AsyncMock(side_effect=mock_get_by_code)
    services.client.products.create.return_value = ProductsResponseDto(
        product_id="prod-123", product_code_readable="WIDGET-001"
    )

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(
                product_code="WIDGET-001",
                supplier_product_code="SUP-SKU-001",
                cost_price=15.50,
            ),
            SupplierProductMapping(
                product_code="WIDGET-002",
                supplier_product_code="SUP-SKU-002",
                cost_price=22.00,
            ),
        ],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - response is now markdown
    assert isinstance(response, str)
    assert "2/2 successful" in response.lower() or (
        "WIDGET-001" in response and "WIDGET-002" in response
    )


@pytest.mark.asyncio
async def test_create_supplier_with_products_partial_failure(
    mock_supplier_onboarding_context, sample_supplier
):
    """Test handling when some product mappings fail."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    # One product exists, one doesn't
    product1 = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[],
    )

    async def mock_get_by_code(code):
        if code == "WIDGET-001":
            return product1
        return None  # WIDGET-999 doesn't exist

    services.products.get_by_code = AsyncMock(side_effect=mock_get_by_code)
    services.client.products.create.return_value = product1

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
            SupplierProductMapping(product_code="WIDGET-999"),  # Doesn't exist
        ],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - response is now markdown
    assert isinstance(response, str)
    assert "1/2 successful" in response.lower()
    assert "WIDGET-001" in response
    assert "❌" in response or "failed" in response.lower()
    assert "not found" in response.lower() or "WIDGET-999" in response


@pytest.mark.asyncio
async def test_create_supplier_with_products_supplier_creation_fails(
    mock_supplier_onboarding_context,
):
    """Test that product mappings are not attempted if supplier creation fails."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = None  # Supplier creation failed

    # Execute & Verify
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )

    with pytest.raises(ValueError, match="Failed to create supplier"):
        await create_supplier_with_products(request, mock_supplier_onboarding_context)

    # Verify product operations were not attempted
    services.products.get_by_code.assert_not_called()
    services.client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_supplier_with_products_no_mappings(
    mock_supplier_onboarding_context, sample_supplier
):
    """Test creating supplier with no product mappings."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - response is now markdown
    assert isinstance(response, str)
    assert "SUP-001" in response
    assert "Test Supplier" in response
    # Should not have product mappings section or show 0/0
    assert "0/0" in response or "Product Mappings" not in response


@pytest.mark.asyncio
async def test_create_supplier_with_products_existing_suppliers(
    mock_supplier_onboarding_context, sample_supplier
):
    """Test that new supplier is added to existing suppliers list."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    # Product already has one supplier
    existing_supplier = ProductSupplier(
        supplier_id="existing-sup",
        supplier_name="Existing Supplier",
    )
    product_with_supplier = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[existing_supplier],
    )
    services.products.get_by_code.return_value = product_with_supplier

    # Verify that create is called with both suppliers
    async def verify_create_call(update_data):
        # Should have both old and new supplier
        assert len(update_data.suppliers) == 2
        assert update_data.suppliers[0] == existing_supplier
        assert update_data.suppliers[1].supplier_id == 456  # sample_supplier has id=456
        return ProductsResponseDto(
            product_id="prod-123",
            product_code_readable="WIDGET-001",
            suppliers=update_data.suppliers,
        )

    services.client.products.create = AsyncMock(side_effect=verify_create_call)

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - response is now markdown
    assert isinstance(response, str)
    assert "1/1 successful" in response.lower() or "WIDGET-001" in response


@pytest.mark.asyncio
async def test_create_supplier_with_products_mapping_api_error(
    mock_supplier_onboarding_context, sample_supplier
):
    """Test handling when individual mapping API call fails."""
    # Setup
    services = mock_supplier_onboarding_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[],
    )
    services.products.get_by_code.return_value = product
    services.client.products.create.side_effect = Exception("API Error")

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )
    response = await create_supplier_with_products(
        request, mock_supplier_onboarding_context
    )

    # Verify - supplier created but mapping failed, response is now markdown
    assert isinstance(response, str)
    assert "0/1 successful" in response.lower()
    assert "❌" in response or "failed" in response.lower()
    assert "API Error" in response or "error" in response.lower()
