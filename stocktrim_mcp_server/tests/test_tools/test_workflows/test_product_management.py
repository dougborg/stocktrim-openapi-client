"""Tests for product management workflow tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.workflows.product_management import (
    ConfigureProductRequest,
    configure_product,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)


@pytest.fixture
def mock_product_mgmt_context(mock_context):
    """Extend mock_context with products service and client."""
    services = mock_context.request_context.lifespan_context
    services.products = AsyncMock()
    services.client = AsyncMock()
    services.client.products = AsyncMock()
    return mock_context


@pytest.mark.asyncio
async def test_configure_product_discontinue_success(
    mock_product_mgmt_context, sample_product
):
    """Test successfully discontinuing a product."""
    # Setup
    services = mock_product_mgmt_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        discontinued=True,
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
    )
    response = await configure_product(request, mock_product_mgmt_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.discontinued is True
    assert "Successfully configured" in response.message
    services.products.get_by_code.assert_called_once_with("WIDGET-001")
    services.client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_configure_product_forecast_settings(
    mock_product_mgmt_context, sample_product
):
    """Test updating forecast configuration."""
    # Setup
    services = mock_product_mgmt_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        ignore_seasonality=True,  # Forecast disabled
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        configure_forecast=False,  # Disable forecast
    )
    response = await configure_product(request, mock_product_mgmt_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.ignore_seasonality is True
    services.client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_configure_product_both_settings(
    mock_product_mgmt_context, sample_product
):
    """Test updating both discontinue and forecast settings."""
    # Setup
    services = mock_product_mgmt_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        discontinued=True,
        ignore_seasonality=False,  # Forecast enabled
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
        configure_forecast=True,  # Enable forecast
    )
    response = await configure_product(request, mock_product_mgmt_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.discontinued is True
    assert response.ignore_seasonality is False


@pytest.mark.asyncio
async def test_configure_product_not_found(mock_product_mgmt_context):
    """Test error when product doesn't exist."""
    # Setup
    services = mock_product_mgmt_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute & Verify
    request = ConfigureProductRequest(
        product_code="NONEXISTENT",
        discontinue=True,
    )

    with pytest.raises(ValueError, match="Product not found"):
        await configure_product(request, mock_product_mgmt_context)

    services.client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_configure_product_api_error(mock_product_mgmt_context, sample_product):
    """Test handling of API errors."""
    # Setup
    services = mock_product_mgmt_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product
    services.client.products.create.side_effect = Exception("API Error")

    # Execute & Verify
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
    )

    with pytest.raises(Exception, match="API Error"):
        await configure_product(request, mock_product_mgmt_context)
