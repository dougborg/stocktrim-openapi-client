"""Tests for forecast management workflow tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.workflows.forecast_management import (
    ManageForecastGroupRequest,
    UpdateForecastSettingsRequest,
    manage_forecast_group,
    update_forecast_settings,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)


@pytest.mark.asyncio
async def test_manage_forecast_group_api_limitation(mock_context):
    """Test that manage_forecast_group returns helpful message about API limitation."""
    # Execute
    request = ManageForecastGroupRequest(
        operation="create",
        group_name="FastMoving",
        description="Fast moving products",
        product_codes=["WIDGET-001", "WIDGET-002"],
    )
    response = await manage_forecast_group(request, mock_context)

    # Verify
    assert response.operation == "create"
    assert response.group_name == "FastMoving"
    assert "cannot be completed" in response.message
    assert "category" in response.note.lower()


@pytest.mark.asyncio
async def test_update_forecast_settings_success(mock_context, sample_product):
    """Test successfully updating forecast settings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        lead_time=21,
        forecast_period=14,
        service_level=0.98,
        minimum_order_quantity=20.0,
    )
    mock_client.products.create.return_value = updated_product

    # Execute
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=21,
        safety_stock_days=14,
        service_level=98.0,
        minimum_order_quantity=20.0,
    )
    response = await update_forecast_settings(request, mock_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.lead_time == 21
    assert response.forecast_period == 14
    assert response.service_level == 98.0
    assert response.minimum_order_quantity == 20.0
    assert "Successfully updated" in response.message

    mock_client.products.find_by_code.assert_called_once_with("WIDGET-001")
    mock_client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_update_forecast_settings_partial(mock_context, sample_product):
    """Test partial update of forecast settings."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        lead_time=28,
    )
    mock_client.products.create.return_value = updated_product

    # Execute - only update lead_time
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=28,
    )
    response = await update_forecast_settings(request, mock_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.lead_time == 28


@pytest.mark.asyncio
async def test_update_forecast_settings_service_level_conversion(
    mock_context, sample_product
):
    """Test that service level is correctly converted from percentage to decimal."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product

    # We need to verify the create call was made with correct decimal value
    async def verify_create_call(update_data):
        # Service level should be converted to decimal (95% -> 0.95)
        assert update_data.service_level == 0.95
        return ProductsResponseDto(
            product_id=sample_product.product_id,
            product_code_readable=sample_product.product_code_readable,
            service_level=0.95,
        )

    mock_client.products.create = AsyncMock(side_effect=verify_create_call)

    # Execute
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        service_level=95.0,  # Input as percentage
    )
    response = await update_forecast_settings(request, mock_context)

    # Verify response converts back to percentage
    assert response.service_level == 95.0


@pytest.mark.asyncio
async def test_update_forecast_settings_product_not_found(mock_context):
    """Test error when product doesn't exist."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = None

    # Execute & Verify
    request = UpdateForecastSettingsRequest(
        product_code="NONEXISTENT",
        lead_time_days=14,
    )

    with pytest.raises(ValueError, match="Product not found"):
        await update_forecast_settings(request, mock_context)

    mock_client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_update_forecast_settings_validation():
    """Test request model validation."""
    # Negative values should fail validation
    with pytest.raises(ValueError):  # Pydantic ValidationError
        UpdateForecastSettingsRequest(
            product_code="WIDGET-001",
            lead_time_days=-5,
        )

    # Service level > 100 should fail
    with pytest.raises(ValueError):  # Pydantic ValidationError
        UpdateForecastSettingsRequest(
            product_code="WIDGET-001",
            service_level=150.0,
        )


@pytest.mark.asyncio
async def test_update_forecast_settings_api_error(mock_context, sample_product):
    """Test handling of API errors."""
    # Setup
    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.products.find_by_code.return_value = sample_product
    mock_client.products.create.side_effect = Exception("API Error")

    # Execute & Verify
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=14,
    )

    with pytest.raises(Exception, match="API Error"):
        await update_forecast_settings(request, mock_context)
