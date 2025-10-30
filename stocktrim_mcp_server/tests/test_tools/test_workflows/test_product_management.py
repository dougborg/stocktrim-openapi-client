"""Tests for product management workflow tools."""

import pytest

from stocktrim_mcp_server.tools.workflows.product_management import (
    ConfigureProductRequest,
    configure_product,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)


@pytest.mark.asyncio
async def test_configure_product_discontinue_success(mock_context, sample_product):
    """Test successfully discontinuing a product."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        discontinued=True,
    )
    mock_client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
    )
    response = await configure_product(request, mock_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.discontinued is True
    assert "Successfully configured" in response.message
    mock_client.products.find_by_code.assert_called_once_with("WIDGET-001")
    mock_client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_configure_product_forecast_settings(mock_context, sample_product):
    """Test updating forecast configuration."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        ignore_seasonality=True,  # Forecast disabled
    )
    mock_client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        configure_forecast=False,  # Disable forecast
    )
    response = await configure_product(request, mock_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.ignore_seasonality is True
    mock_client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_configure_product_both_settings(mock_context, sample_product):
    """Test updating both discontinue and forecast settings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        discontinued=True,
        ignore_seasonality=False,  # Forecast enabled
    )
    mock_client.products.create.return_value = updated_product

    # Execute
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
        configure_forecast=True,  # Enable forecast
    )
    response = await configure_product(request, mock_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.discontinued is True
    assert response.ignore_seasonality is False


@pytest.mark.asyncio
async def test_configure_product_not_found(mock_context):
    """Test error when product doesn't exist."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = None

    # Execute & Verify
    request = ConfigureProductRequest(
        product_code="NONEXISTENT",
        discontinue=True,
    )

    with pytest.raises(ValueError, match="Product not found"):
        await configure_product(request, mock_context)

    mock_client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_configure_product_api_error(mock_context, sample_product):
    """Test handling of API errors."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product
    mock_client.products.create.side_effect = Exception("API Error")

    # Execute & Verify
    request = ConfigureProductRequest(
        product_code="WIDGET-001",
        discontinue=True,
    )

    with pytest.raises(Exception, match="API Error"):
        await configure_product(request, mock_context)
