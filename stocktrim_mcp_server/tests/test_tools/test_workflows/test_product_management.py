"""Tests for product management workflow tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.workflows.product_management import (
    ConfigureProductRequest,
    ProductLifecycleRequest,
    configure_product,
    products_configure_lifecycle,
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


# ============================================================================
# Tests for products_configure_lifecycle
# ============================================================================


@pytest.fixture
def mock_lifecycle_context(mock_context):
    """Extend mock_context with products service, client, and forecasting."""
    services = mock_context.request_context.lifespan_context
    services.products = AsyncMock()
    services.client = AsyncMock()
    services.client.products = AsyncMock()
    services.client.forecasting = AsyncMock()
    return mock_context


@pytest.mark.asyncio
async def test_lifecycle_activate_product(mock_lifecycle_context):
    """Test activating a product."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        name="Test Widget",
        discontinued=True,
        ignore_seasonality=True,
        stock_on_hand=50,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        ignore_seasonality=False,
    )
    services.client.products.create.return_value = updated_product
    services.client.forecasting.run_calculations.return_value = None

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="activate",
        update_forecasts=True,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify
    assert isinstance(response, str)
    assert "WIDGET-001" in response
    assert "ACTIVATE" in response
    assert "activated" in response.lower()
    assert "✅" in response
    services.products.get_by_code.assert_called_once_with("WIDGET-001")
    services.client.products.create.assert_called_once()
    services.client.forecasting.run_calculations.assert_called_once()


@pytest.mark.asyncio
async def test_lifecycle_deactivate_product(mock_lifecycle_context):
    """Test deactivating a product."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        name="Test Widget",
        discontinued=False,
        ignore_seasonality=False,
        stock_on_hand=100,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        ignore_seasonality=True,
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="deactivate",
        update_forecasts=False,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify
    assert isinstance(response, str)
    assert "deactivate" in response.lower()
    assert "WIDGET-001" in response
    services.client.forecasting.run_calculations.assert_not_called()


@pytest.mark.asyncio
async def test_lifecycle_discontinue_product(mock_lifecycle_context):
    """Test discontinuing a product."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        stock_on_hand=25,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=True,
        ignore_seasonality=True,
    )
    services.client.products.create.return_value = updated_product
    services.client.forecasting.run_calculations.return_value = None

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="discontinue",
        update_forecasts=True,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify
    assert isinstance(response, str)
    assert "discontinue" in response.lower()
    assert "25" in response  # current inventory
    assert "Previous Status" in response
    assert "New Status" in response


@pytest.mark.asyncio
async def test_lifecycle_unstock_product(mock_lifecycle_context):
    """Test unstocking a product."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        stock_on_hand=10,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=True,
        ignore_seasonality=True,
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="unstock",
        update_forecasts=False,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify
    assert isinstance(response, str)
    assert "unstock" in response.lower()


@pytest.mark.asyncio
async def test_lifecycle_invalid_action(mock_lifecycle_context):
    """Test error on invalid action."""
    # Execute & Verify
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="invalid_action",
    )

    with pytest.raises(ValueError, match="Invalid action"):
        await products_configure_lifecycle(request, mock_lifecycle_context)


@pytest.mark.asyncio
async def test_lifecycle_product_not_found(mock_lifecycle_context):
    """Test error when product doesn't exist."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute & Verify
    request = ProductLifecycleRequest(
        product_code="NONEXISTENT",
        action="activate",
    )

    with pytest.raises(ValueError, match="Product not found"):
        await products_configure_lifecycle(request, mock_lifecycle_context)

    services.client.products.create.assert_not_called()


@pytest.mark.asyncio
async def test_lifecycle_forecast_update_fails(mock_lifecycle_context):
    """Test handling when forecast update fails."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=True,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        ignore_seasonality=False,
    )
    services.client.products.create.return_value = updated_product
    services.client.forecasting.run_calculations.side_effect = Exception(
        "Forecast API Error"
    )

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="activate",
        update_forecasts=True,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify - should still succeed but report forecast failure
    assert isinstance(response, str)
    assert "⚠️" in response or "forecast" in response.lower()
    assert "failed" in response.lower() or "error" in response.lower()


@pytest.mark.asyncio
async def test_lifecycle_clear_inventory_flag(mock_lifecycle_context):
    """Test deactivate with clear_inventory flag."""
    # Setup
    services = mock_lifecycle_context.request_context.lifespan_context

    existing_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        stock_on_hand=75,
    )
    services.products.get_by_code.return_value = existing_product

    updated_product = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        discontinued=False,
        ignore_seasonality=True,
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = ProductLifecycleRequest(
        product_code="WIDGET-001",
        action="deactivate",
        clear_inventory=True,
        update_forecasts=False,
    )
    response = await products_configure_lifecycle(request, mock_lifecycle_context)

    # Verify
    assert isinstance(response, str)
    assert "75" in response  # Shows previous inventory
    # Note: Actual inventory clearing would require additional implementation
