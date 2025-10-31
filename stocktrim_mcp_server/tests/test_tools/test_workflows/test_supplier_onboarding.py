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


@pytest.mark.asyncio
async def test_create_supplier_with_products_success(
    mock_context, sample_product, sample_supplier
):
    """Test successfully creating a supplier with product mappings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier
    mock_client.products.find_by_code.return_value = sample_product

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
    mock_client.products.create.return_value = updated_product

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
    response = await create_supplier_with_products(request, mock_context)

    # Verify
    assert response.supplier_code == "SUP-001"
    assert response.supplier_name == "Test Supplier"
    assert response.supplier_id == "sup-456"
    assert response.mappings_attempted == 1
    assert response.mappings_successful == 1
    assert len(response.mapping_details) == 1
    assert response.mapping_details[0].success is True
    assert "created successfully" in response.message

    mock_client.suppliers.create_one.assert_called_once()
    mock_client.products.find_by_code.assert_called_once_with("WIDGET-001")
    mock_client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_supplier_with_products_multiple_mappings(
    mock_context, sample_supplier
):
    """Test creating supplier with multiple product mappings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier

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

    # Mock find_by_code to return different products
    async def mock_find_by_code(code):
        if code == "WIDGET-001":
            return product1
        elif code == "WIDGET-002":
            return product2
        return None

    mock_client.products.find_by_code = AsyncMock(side_effect=mock_find_by_code)
    mock_client.products.create.return_value = ProductsResponseDto(
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
    response = await create_supplier_with_products(request, mock_context)

    # Verify
    assert response.mappings_attempted == 2
    assert response.mappings_successful == 2
    assert len(response.mapping_details) == 2


@pytest.mark.asyncio
async def test_create_supplier_with_products_partial_failure(
    mock_context, sample_supplier
):
    """Test handling when some product mappings fail."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier

    # One product exists, one doesn't
    product1 = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[],
    )

    async def mock_find_by_code(code):
        if code == "WIDGET-001":
            return product1
        return None  # WIDGET-999 doesn't exist

    mock_client.products.find_by_code = AsyncMock(side_effect=mock_find_by_code)
    mock_client.products.create.return_value = product1

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
            SupplierProductMapping(product_code="WIDGET-999"),  # Doesn't exist
        ],
    )
    response = await create_supplier_with_products(request, mock_context)

    # Verify
    assert response.mappings_attempted == 2
    assert response.mappings_successful == 1
    assert len(response.mapping_details) == 2
    assert response.mapping_details[0].success is True
    assert response.mapping_details[1].success is False
    assert response.mapping_details[1].error is not None
    assert "not found" in response.mapping_details[1].error.lower()


@pytest.mark.asyncio
async def test_create_supplier_with_products_supplier_creation_fails(mock_context):
    """Test that product mappings are not attempted if supplier creation fails."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = None  # Supplier creation failed

    # Execute & Verify
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )

    with pytest.raises(ValueError, match="Failed to create supplier"):
        await create_supplier_with_products(request, mock_context)

    # Verify product operations were not attempted
    mock_client.products.find_by_code.assert_not_called()
    mock_client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_supplier_with_products_no_mappings(mock_context, sample_supplier):
    """Test creating supplier with no product mappings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[],
    )
    response = await create_supplier_with_products(request, mock_context)

    # Verify
    assert response.supplier_code == "SUP-001"
    assert response.mappings_attempted == 0
    assert response.mappings_successful == 0
    assert len(response.mapping_details) == 0


@pytest.mark.asyncio
async def test_create_supplier_with_products_existing_suppliers(
    mock_context, sample_supplier
):
    """Test that new supplier is added to existing suppliers list."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier

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
    mock_client.products.find_by_code.return_value = product_with_supplier

    # Verify that create is called with both suppliers
    async def verify_create_call(update_data):
        # Should have both old and new supplier
        assert len(update_data.suppliers) == 2
        assert update_data.suppliers[0] == existing_supplier
        assert update_data.suppliers[1].supplier_id == "sup-456"
        return ProductsResponseDto(
            product_id="prod-123",
            product_code_readable="WIDGET-001",
            suppliers=update_data.suppliers,
        )

    mock_client.products.create = AsyncMock(side_effect=verify_create_call)

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )
    response = await create_supplier_with_products(request, mock_context)

    # Verify
    assert response.mappings_successful == 1


@pytest.mark.asyncio
async def test_create_supplier_with_products_mapping_api_error(
    mock_context, sample_supplier
):
    """Test handling when individual mapping API call fails."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.suppliers.create_one.return_value = sample_supplier

    product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        suppliers=[],
    )
    mock_client.products.find_by_code.return_value = product
    mock_client.products.create.side_effect = Exception("API Error")

    # Execute
    request = CreateSupplierWithProductsRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        product_mappings=[
            SupplierProductMapping(product_code="WIDGET-001"),
        ],
    )
    response = await create_supplier_with_products(request, mock_context)

    # Verify - supplier created but mapping failed
    assert response.mappings_attempted == 1
    assert response.mappings_successful == 0
    assert response.mapping_details[0].success is False
    assert response.mapping_details[0].error is not None
    assert "API Error" in response.mapping_details[0].error
