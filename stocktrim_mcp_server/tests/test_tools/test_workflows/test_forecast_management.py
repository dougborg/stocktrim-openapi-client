"""Tests for forecast management workflow tools."""

from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_mcp_server.tools.workflows.forecast_management import (
    ForecastsGetForProductsRequest,
    ForecastsUpdateAndMonitorRequest,
    ManageForecastGroupRequest,
    UpdateForecastSettingsRequest,
    forecasts_get_for_products,
    forecasts_update_and_monitor,
    manage_forecast_group,
    update_forecast_settings,
)
from stocktrim_public_api_client.generated.models.processing_status_response_dto import (
    ProcessingStatusResponseDto,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)


@pytest.fixture
def mock_forecast_context(mock_context):
    """Extend mock_context with products service and client."""
    services = mock_context.request_context.lifespan_context
    services.products = AsyncMock()
    # Also mock the client.products since update_forecast_settings uses it directly
    services.client = AsyncMock()
    services.client.products = AsyncMock()
    return mock_context


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
    assert "categor" in response.note.lower()  # matches "category" or "categories"


@pytest.mark.asyncio
async def test_update_forecast_settings_success(mock_forecast_context, sample_product):
    """Test successfully updating forecast settings."""
    # Setup
    services = mock_forecast_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        lead_time=21,
        forecast_period=14,
        service_level=0.98,
        minimum_order_quantity=20.0,
    )
    services.client.products.create.return_value = updated_product

    # Execute
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=21,
        safety_stock_days=14,
        service_level=98.0,
        minimum_order_quantity=20.0,
    )
    response = await update_forecast_settings(request, mock_forecast_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.lead_time == 21
    assert response.forecast_period == 14
    assert response.service_level == 98.0
    assert response.minimum_order_quantity == 20.0
    assert "Successfully updated" in response.message

    services.products.get_by_code.assert_called_once_with("WIDGET-001")
    services.client.products.create.assert_called_once()


@pytest.mark.asyncio
async def test_update_forecast_settings_partial(mock_forecast_context, sample_product):
    """Test partial update of forecast settings."""
    # Setup
    services = mock_forecast_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    updated_product = ProductsResponseDto(
        product_id=sample_product.product_id,
        product_code_readable=sample_product.product_code_readable,
        lead_time=28,
    )
    services.client.products.create.return_value = updated_product

    # Execute - only update lead_time
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=28,
    )
    response = await update_forecast_settings(request, mock_forecast_context)

    # Verify
    assert response.product_code == "WIDGET-001"
    assert response.lead_time == 28


@pytest.mark.asyncio
async def test_update_forecast_settings_service_level_conversion(
    mock_forecast_context, sample_product
):
    """Test that service level is correctly converted from percentage to decimal."""
    # Setup
    services = mock_forecast_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product

    # We need to verify the create call was made with correct decimal value
    async def verify_create_call(update_data):
        # Service level should be converted to decimal (95% -> 0.95)
        assert update_data.service_level == 0.95
        return ProductsResponseDto(
            product_id=sample_product.product_id,
            product_code_readable=sample_product.product_code_readable,
            service_level=0.95,
        )

    services.client.products.create = AsyncMock(side_effect=verify_create_call)

    # Execute
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        service_level=95.0,  # Input as percentage
    )
    response = await update_forecast_settings(request, mock_forecast_context)

    # Verify response converts back to percentage
    assert response.service_level == 95.0


@pytest.mark.asyncio
async def test_update_forecast_settings_product_not_found(mock_forecast_context):
    """Test error when product doesn't exist."""
    # Setup
    services = mock_forecast_context.request_context.lifespan_context
    services.products.get_by_code.return_value = None

    # Execute & Verify
    request = UpdateForecastSettingsRequest(
        product_code="NONEXISTENT",
        lead_time_days=14,
    )

    with pytest.raises(ValueError, match="Product not found"):
        await update_forecast_settings(request, mock_forecast_context)

    services.client.products.create.assert_not_called()


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
async def test_update_forecast_settings_api_error(
    mock_forecast_context, sample_product
):
    """Test handling of API errors."""
    # Setup
    services = mock_forecast_context.request_context.lifespan_context
    services.products.get_by_code.return_value = sample_product
    services.client.products.create.side_effect = Exception("API Error")

    # Execute & Verify
    request = UpdateForecastSettingsRequest(
        product_code="WIDGET-001",
        lead_time_days=14,
    )

    with pytest.raises(Exception, match="API Error"):
        await update_forecast_settings(request, mock_forecast_context)


# ============================================================================
# Tests for forecasts_update_and_monitor
# ============================================================================


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_trigger_only(mock_context):
    """Test triggering forecast without waiting for completion."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock()

    # Execute
    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=False,
        poll_interval_seconds=5,
        timeout_seconds=300,
    )
    result = await forecasts_update_and_monitor(request, mock_context)

    # Verify
    assert "# Forecast Update Status" in result
    assert "Triggered" in result
    assert "Next Steps" in result
    services.client.forecasting.run_calculations.assert_called_once()


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_wait_success(mock_context):
    """Test waiting for forecast completion successfully."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock()

    # Mock status progression: processing -> complete
    status_in_progress = ProcessingStatusResponseDto(
        is_processing=True,
        percentage_complete=50,
        status_message="Processing...",
    )
    status_complete = ProcessingStatusResponseDto(
        is_processing=False,
        percentage_complete=100,
        status_message="Complete",
    )
    services.client.forecasting.get_processing_status = AsyncMock(
        side_effect=[status_in_progress, status_complete]
    )

    # Execute
    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=True,
        poll_interval_seconds=1,
        timeout_seconds=31,
    )
    result = await forecasts_update_and_monitor(request, mock_context)

    # Verify
    assert "✅ Complete" in result
    assert "Time Elapsed" in result
    assert "forecasts_get_for_products" in result
    services.client.forecasting.run_calculations.assert_called_once()
    assert services.client.forecasting.get_processing_status.call_count == 2


@pytest.mark.asyncio
@pytest.mark.timeout(60)  # Allow 60 seconds for this test
async def test_forecasts_update_and_monitor_timeout(mock_context):
    """Test timeout when forecast takes too long."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock()

    # Mock status that never completes
    status_in_progress = ProcessingStatusResponseDto(
        is_processing=True,
        percentage_complete=30,
        status_message="Still processing...",
    )
    services.client.forecasting.get_processing_status = AsyncMock(
        return_value=status_in_progress
    )

    # Execute - use shorter timeout for faster test execution
    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=True,
        poll_interval_seconds=1,
        timeout_seconds=30,
    )
    result = await forecasts_update_and_monitor(request, mock_context)

    # Verify
    assert "⚠️ Timeout" in result
    assert "did not complete within" in result
    assert "30%" in result


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_error(mock_context):
    """Test error handling when forecast trigger fails."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock(
        side_effect=Exception("API Error")
    )

    # Execute
    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=False,
        poll_interval_seconds=5,
        timeout_seconds=300,
    )
    result = await forecasts_update_and_monitor(request, mock_context)

    # Verify
    assert "❌ Failed" in result
    assert "API Error" in result
    assert "Troubleshooting" in result


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_validation():
    """Test request parameter validation."""
    # Valid request
    valid_request = ForecastsUpdateAndMonitorRequest(
        poll_interval_seconds=30,
        timeout_seconds=600,
    )
    assert valid_request.poll_interval_seconds == 30

    # Invalid poll interval (too low)
    with pytest.raises(ValueError):
        ForecastsUpdateAndMonitorRequest(poll_interval_seconds=0)

    # Invalid poll interval (too high)
    with pytest.raises(ValueError):
        ForecastsUpdateAndMonitorRequest(poll_interval_seconds=61)

    # Invalid timeout (too low)
    with pytest.raises(ValueError):
        ForecastsUpdateAndMonitorRequest(timeout_seconds=29)

    # Invalid timeout (too high)
    with pytest.raises(ValueError):
        ForecastsUpdateAndMonitorRequest(timeout_seconds=3601)


# ============================================================================
# Tests for forecasts_get_for_products
# ============================================================================


@pytest.mark.asyncio
async def test_forecasts_get_for_products_with_filters(mock_context):
    """Test querying forecasts with filters."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    # Mock forecast data
    mock_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            # product_description removed - "Standard Widget",
            stock_on_hand=50.0,
            days_until_stock_out=5,
            order_quantity=100.0,
            safety_stock_level=20.0,
            # supplier_name removed - "Acme Corp",
            lead_time_days=7,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            # product_description removed - "Premium Widget",
            stock_on_hand=30.0,
            days_until_stock_out=10,
            order_quantity=50.0,
            safety_stock_level=15.0,
            # supplier_name removed - "Acme Corp",
            lead_time_days=7,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    # Execute
    request = ForecastsGetForProductsRequest(
        category="Widgets",
        location_code="WAREHOUSE-A",
        max_results=10,
    )
    result = await forecasts_get_for_products(request, mock_context)

    # Verify
    assert "# Forecast Data" in result
    assert "Category: Widgets" in result
    assert "Location: WAREHOUSE-A" in result
    assert "WIDGET-001" in result
    assert "WIDGET-002" in result
    assert "🔴 HIGH" in result  # 5 days is high priority
    assert "🟡 MEDIUM" in result  # 10 days is medium priority


@pytest.mark.asyncio
async def test_forecasts_get_for_products_empty_results(mock_context):
    """Test handling of empty forecast results."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()
    services.client.order_plan.query = AsyncMock(return_value=[])

    # Execute
    request = ForecastsGetForProductsRequest(
        category="NonExistent",
        max_results=10,
    )
    result = await forecasts_get_for_products(request, mock_context)

    # Verify
    assert "No forecast data found" in result
    assert "Troubleshooting" in result
    assert "forecasts_update_and_monitor" in result


@pytest.mark.asyncio
async def test_forecasts_get_for_products_sorting(mock_context):
    """Test sorting by days until stockout."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    # Mock unsorted data
    mock_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            # product_description removed - "Widget 2",
            days_until_stock_out=20,
            stock_on_hand=100.0,
            order_quantity=50.0,
            safety_stock_level=10.0,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            # product_description removed - "Widget 1",
            days_until_stock_out=5,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    # Execute
    request = ForecastsGetForProductsRequest(
        sort_by="days_until_stockout",
        max_results=10,
    )
    result = await forecasts_get_for_products(request, mock_context)

    # Verify - WIDGET-001 (5 days) should appear before WIDGET-002 (20 days)
    widget_001_pos = result.find("WIDGET-001")
    widget_002_pos = result.find("WIDGET-002")
    assert widget_001_pos < widget_002_pos


@pytest.mark.asyncio
async def test_forecasts_get_for_products_priority_indicators(mock_context):
    """Test priority indicators based on days until stockout."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    # Mock items with different urgency levels
    mock_items = [
        SkuOptimizedResultsDto(
            product_code="HIGH-PRIORITY",
            # product_description removed - "High Priority Item",
            days_until_stock_out=3,  # < 7 days = HIGH
            stock_on_hand=10.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
        SkuOptimizedResultsDto(
            product_code="MEDIUM-PRIORITY",
            # product_description removed - "Medium Priority Item",
            days_until_stock_out=10,  # 7-14 days = MEDIUM
            stock_on_hand=50.0,
            order_quantity=50.0,
            safety_stock_level=15.0,
        ),
        SkuOptimizedResultsDto(
            product_code="LOW-PRIORITY",
            # product_description removed - "Low Priority Item",
            days_until_stock_out=20,  # > 14 days = LOW
            stock_on_hand=100.0,
            order_quantity=25.0,
            safety_stock_level=10.0,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    # Execute
    request = ForecastsGetForProductsRequest(max_results=10)
    result = await forecasts_get_for_products(request, mock_context)

    # Verify
    assert "🔴 HIGH" in result
    assert "🟡 MEDIUM" in result
    assert "🟢 LOW" in result


@pytest.mark.asyncio
async def test_forecasts_get_for_products_filter_by_codes(mock_context):
    """Test filtering by specific product codes."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    # Mock data with various products
    mock_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            # product_description removed - "Widget 1",
            days_until_stock_out=10,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            # product_description removed - "Widget 2",
            days_until_stock_out=10,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-003",
            # product_description removed - "Widget 3",
            days_until_stock_out=10,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    # Execute
    request = ForecastsGetForProductsRequest(
        product_codes=["WIDGET-001", "WIDGET-003"],
        max_results=10,
    )
    result = await forecasts_get_for_products(request, mock_context)

    # Verify - should only include WIDGET-001 and WIDGET-003
    assert "WIDGET-001" in result
    assert "WIDGET-003" in result
    assert "WIDGET-002" not in result


@pytest.mark.asyncio
async def test_forecasts_get_for_products_error(mock_context):
    """Test error handling when query fails."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()
    services.client.order_plan.query = AsyncMock(side_effect=Exception("API Error"))

    # Execute
    request = ForecastsGetForProductsRequest(max_results=10)
    result = await forecasts_get_for_products(request, mock_context)

    # Verify
    assert "Query Failed" in result
    assert "API Error" in result
    assert "Troubleshooting" in result


@pytest.mark.asyncio
async def test_forecasts_get_for_products_validation():
    """Test request parameter validation."""
    # Valid request
    valid_request = ForecastsGetForProductsRequest(max_results=50)
    assert valid_request.max_results == 50

    # Invalid max_results (too low)
    with pytest.raises(ValueError):
        ForecastsGetForProductsRequest(max_results=0)

    # Invalid max_results (too high)
    with pytest.raises(ValueError):
        ForecastsGetForProductsRequest(max_results=501)


@pytest.mark.asyncio
async def test_forecasts_get_for_products_summary_stats(mock_context):
    """Test that summary statistics are calculated correctly."""
    # Setup
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    mock_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            # product_description removed - "Widget 1",
            days_until_stock_out=5,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            days_until_stock_out=15,
            stock_on_hand=50.0,
            order_quantity=200.0,
            safety_stock_level=20.0,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    # Execute
    request = ForecastsGetForProductsRequest(max_results=10)
    result = await forecasts_get_for_products(request, mock_context)

    # Verify
    assert "## Summary" in result
    assert "Total Recommended Order Quantity" in result
    assert "300" in result  # 100 + 200
    assert "Average Days Until Stockout" in result
    assert "10.0" in result  # (5 + 15) / 2
