"""Tests for forecast management workflow tools."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_mcp_server.tools.tool_result_utils import unwrap_tool_result
from stocktrim_mcp_server.tools.workflows.forecast_management import (
    ForecastsGetForProductsRequest,
    ForecastsGetForProductsResponse,
    ForecastsUpdateAndMonitorRequest,
    ForecastsUpdateAndMonitorResponse,
    ManageForecastGroupRequest,
    ManageForecastGroupResponse,
    UpdateForecastSettingsRequest,
    UpdateForecastSettingsResponse,
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


async def _call_manage_group(*args: Any, **kw: Any) -> ManageForecastGroupResponse:
    return unwrap_tool_result(
        await manage_forecast_group(*args, **kw), ManageForecastGroupResponse
    )


async def _call_update_settings(
    *args: Any, **kw: Any
) -> UpdateForecastSettingsResponse:
    return unwrap_tool_result(
        await update_forecast_settings(*args, **kw), UpdateForecastSettingsResponse
    )


async def _call_update_monitor(
    *args: Any, **kw: Any
) -> ForecastsUpdateAndMonitorResponse:
    return unwrap_tool_result(
        await forecasts_update_and_monitor(*args, **kw),
        ForecastsUpdateAndMonitorResponse,
    )


async def _call_get_forecasts(*args: Any, **kw: Any) -> ForecastsGetForProductsResponse:
    return unwrap_tool_result(
        await forecasts_get_for_products(*args, **kw), ForecastsGetForProductsResponse
    )


@pytest.fixture
def fast_polling_loop(monkeypatch):
    """Make ``forecasts_update_and_monitor``'s polling loop run at zero
    wall-clock cost.

    The impl loops on ``time.time() - start_time > timeout_seconds`` with an
    ``asyncio.sleep(poll_interval_seconds)`` between iterations; using real
    sleeps blocks CI for the full ``timeout_seconds`` (30+) every test run
    (Copilot review, PR #188). Patches: ``asyncio.sleep`` becomes a no-op,
    and ``time.time`` returns 0 once (for ``start_time``) then a value past
    any plausible ``timeout_seconds`` so iteration 2's elapsed check exits
    immediately.
    """
    import asyncio

    from stocktrim_mcp_server.tools.workflows import forecast_management

    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)
    times = iter([0.0] + [10_000.0] * 100)
    monkeypatch.setattr(forecast_management.time, "time", lambda: next(times))


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
    response = await _call_manage_group(request, mock_context)

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
    response = await _call_update_settings(request, mock_forecast_context)

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
    response = await _call_update_settings(request, mock_forecast_context)

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
    response = await _call_update_settings(request, mock_forecast_context)

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
        await _call_update_settings(request, mock_forecast_context)

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
        await _call_update_settings(request, mock_forecast_context)


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
    response = await _call_update_monitor(request, mock_context)

    # Verify
    assert response.triggered is True
    assert response.completed is False
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
    response = await _call_update_monitor(request, mock_context)

    # Verify
    assert response.triggered is True
    assert response.completed is True
    assert response.progress_percentage == 100
    assert response.elapsed_seconds is not None
    services.client.forecasting.run_calculations.assert_called_once()
    assert services.client.forecasting.get_processing_status.call_count == 2


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_timeout(mock_context, fast_polling_loop):
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

    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=True,
        poll_interval_seconds=1,
        timeout_seconds=30,
    )
    response = await _call_update_monitor(request, mock_context)

    # Verify
    assert response.triggered is True
    assert response.completed is False
    assert response.progress_percentage == 30
    assert "Timeout" in response.status_message


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
    response = await _call_update_monitor(request, mock_context)

    # Verify
    assert response.triggered is False
    assert response.completed is False
    assert "API Error" in response.status_message


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_keeps_triggered_when_polling_fails(
    mock_context,
):
    """``triggered`` must stay True if run_calculations() succeeded but the
    polling loop later raised — otherwise callers think nothing happened
    while a background calculation is still running (Copilot review, PR #188)."""
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock()
    services.client.forecasting.get_processing_status = AsyncMock(
        side_effect=Exception("status check exploded")
    )

    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=True,
        poll_interval_seconds=1,
        timeout_seconds=30,
    )
    response = await _call_update_monitor(request, mock_context)

    assert response.triggered is True  # was True before the polling loop blew up
    assert response.completed is False
    assert "status check exploded" in response.status_message


@pytest.mark.asyncio
async def test_forecasts_update_and_monitor_rounds_progress_percentage(
    mock_context, fast_polling_loop
):
    """``progress_percentage`` on timeout should round, not truncate
    (Copilot review, PR #188 — int(99.7) == 99 surprised callers)."""
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.forecasting = Mock()
    services.client.forecasting.run_calculations = AsyncMock()
    services.client.forecasting.get_processing_status = AsyncMock(
        return_value=ProcessingStatusResponseDto(
            is_processing=True,
            percentage_complete=99.7,
            status_message="Almost done",
        )
    )

    request = ForecastsUpdateAndMonitorRequest(
        wait_for_completion=True,
        poll_interval_seconds=1,
        timeout_seconds=30,
    )
    response = await _call_update_monitor(request, mock_context)

    assert response.completed is False  # timed out
    assert response.progress_percentage == 100  # round(99.7), not int(99.7)


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
# Tests for _to_forecast_item (DTO → ForecastItem coercion boundary)
# ============================================================================


def test_to_forecast_item_coerces_all_fields():
    """Populated DTO maps cleanly to a ForecastItem."""
    from stocktrim_mcp_server.tools.workflows.forecast_management import (
        _to_forecast_item,
    )

    dto = SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        days_until_stock_out=10,
        stock_on_hand=42.5,
        order_quantity=100.0,
        safety_stock_level=20.0,
        lead_time_days=7,
    )
    item = _to_forecast_item(dto)

    assert item.product_code == "WIDGET-001"
    assert item.priority == "MEDIUM"  # 10 days
    assert item.current_stock == 42.5
    assert item.days_until_stockout == 10.0
    assert item.recommended_order_quantity == 100.0
    assert item.safety_stock_level == 20.0
    assert item.lead_time_days == 7


def test_to_forecast_item_substitutes_defaults_for_unset_fields():
    """Missing UNSET fields collapse to type-appropriate defaults / None."""
    from stocktrim_mcp_server.tools.workflows.forecast_management import (
        _to_forecast_item,
    )

    # All optional fields omitted (UNSET).
    dto = SkuOptimizedResultsDto()
    item = _to_forecast_item(dto)

    assert item.product_code == "Unknown"
    assert item.priority == "UNKNOWN"  # missing days_until_stockout
    assert item.current_stock == 0.0
    assert (
        item.days_until_stockout is None
    )  # NOT 0.0 — that would falsely classify HIGH
    assert item.recommended_order_quantity == 0.0
    assert item.safety_stock_level == 0.0
    assert item.lead_time_days is None


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify
    assert response.filters["category"] == "Widgets"
    assert response.filters["location_code"] == "WAREHOUSE-A"
    codes = [item.product_code for item in response.items]
    assert "WIDGET-001" in codes
    assert "WIDGET-002" in codes
    by_code = {item.product_code: item for item in response.items}
    assert by_code["WIDGET-001"].priority == "HIGH"  # 5 days
    assert by_code["WIDGET-002"].priority == "MEDIUM"  # 10 days


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify
    assert response.items == []
    assert response.total_available == 0
    assert response.average_days_until_stockout is None
    assert response.error is None


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify - WIDGET-001 (5 days) should appear before WIDGET-002 (20 days)
    codes = [item.product_code for item in response.items]
    assert codes.index("WIDGET-001") < codes.index("WIDGET-002")


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify
    by_code = {item.product_code: item for item in response.items}
    assert by_code["HIGH-PRIORITY"].priority == "HIGH"
    assert by_code["MEDIUM-PRIORITY"].priority == "MEDIUM"
    assert by_code["LOW-PRIORITY"].priority == "LOW"


@pytest.mark.asyncio
async def test_forecasts_get_for_products_truncated_for_size_only_when_dropped(
    mock_context,
):
    """``truncated_for_size`` must only be True when the trim slice actually
    drops items. The pre-fix impl set the flag whenever the byte estimate
    exceeded the budget, but the trim was a no-op when len <= 50 — leaving
    consumers who use the flag as a 'results were trimmed' indicator with a
    false positive (Copilot review, PR #188)."""
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    # Build 30 items, each with the default per-item byte estimate. With
    # ESTIMATED_CHARS_PER_FORECAST_ITEM=500 and MAX_RESPONSE_SIZE_BYTES=400_000,
    # 30 items ~= 15_000 bytes — nowhere near the budget. So the trim block
    # should NOT be entered and truncated_for_size must stay False.
    small_batch = [
        SkuOptimizedResultsDto(
            product_code=f"WIDGET-{i:03d}",
            days_until_stock_out=10,
            stock_on_hand=50.0,
            order_quantity=100.0,
            safety_stock_level=20.0,
        )
        for i in range(30)
    ]
    services.client.order_plan.query = AsyncMock(return_value=small_batch)

    response = await _call_get_forecasts(
        ForecastsGetForProductsRequest(max_results=500),
        mock_context,
    )

    assert len(response.items) == 30
    assert response.truncated_for_size is False


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify - should only include WIDGET-001 and WIDGET-003
    codes = {item.product_code for item in response.items}
    assert codes == {"WIDGET-001", "WIDGET-003"}


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify
    assert response.error is not None
    assert "API Error" in response.error
    assert response.items == []


@pytest.mark.asyncio
async def test_forecasts_get_for_products_missing_days_is_unknown_priority(
    mock_context,
):
    """Items with no days_until_stock_out from the API must surface as
    ``UNKNOWN`` priority rather than being silently classified ``HIGH``
    via a 0.0 substitution (Copilot review, PR #188 — operators were at
    risk of acting on phantom urgency for items missing forecast data)."""
    services = mock_context.request_context.lifespan_context
    services.client = Mock()
    services.client.order_plan = Mock()

    mock_items = [
        SkuOptimizedResultsDto(
            product_code="HAS-DATA",
            days_until_stock_out=4,
            stock_on_hand=10.0,
            order_quantity=50.0,
            safety_stock_level=20.0,
        ),
        SkuOptimizedResultsDto(
            product_code="MISSING-DATA",
            # days_until_stock_out intentionally omitted (UNSET)
            stock_on_hand=10.0,
            order_quantity=50.0,
            safety_stock_level=20.0,
        ),
    ]
    services.client.order_plan.query = AsyncMock(return_value=mock_items)

    request = ForecastsGetForProductsRequest(max_results=10)
    response = await _call_get_forecasts(request, mock_context)

    by_code = {item.product_code: item for item in response.items}
    assert by_code["HAS-DATA"].priority == "HIGH"  # 4 days < 7
    assert by_code["MISSING-DATA"].priority == "UNKNOWN"
    assert by_code["MISSING-DATA"].days_until_stockout is None
    # Average should skip the UNKNOWN row, not treat it as 0.
    assert response.average_days_until_stockout == 4.0


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
    response = await _call_get_forecasts(request, mock_context)

    # Verify
    assert response.total_recommended_quantity == 300.0  # 100 + 200
    assert response.average_days_until_stockout == 10.0  # (5 + 15) / 2
