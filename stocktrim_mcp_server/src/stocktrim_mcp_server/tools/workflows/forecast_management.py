"""Forecast management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for managing forecast groups
and updating forecast settings for products.
"""

from __future__ import annotations

import asyncio
import time
from typing import Literal

from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
from stocktrim_mcp_server.utils import to_unset, unwrap_unset
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria import (
    OrderPlanFilterCriteria,
)
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)

logger = get_logger(__name__)

# Token budget and size estimation constants
MAX_RESPONSE_SIZE_BYTES = 400_000  # Maximum response size to avoid context overflow
ESTIMATED_CHARS_PER_FORECAST_ITEM = (
    500  # Rough estimate of characters per forecast item
)

# Priority threshold constants for stockout urgency
HIGH_PRIORITY_THRESHOLD_DAYS = 7  # < 7 days = HIGH priority
MEDIUM_PRIORITY_THRESHOLD_DAYS = 14  # < 14 days = MEDIUM priority

# ============================================================================
# Tool: manage_forecast_group
# ============================================================================


class ManageForecastGroupRequest(BaseModel):
    """Request for managing forecast groups."""

    operation: Literal["create", "update", "delete"] = Field(
        description="Operation to perform on the forecast group"
    )
    group_name: str = Field(description="Name of the forecast group")
    description: str | None = Field(
        default=None, description="Description of the forecast group"
    )
    product_codes: list[str] | None = Field(
        default=None, description="List of product codes in this group"
    )


class ManageForecastGroupResponse(BaseModel):
    """Response for forecast group management."""

    operation: str = Field(description="Operation performed")
    group_name: str = Field(description="Group name")
    message: str = Field(description="Result message")
    note: str = Field(
        description="Important note about StockTrim API capabilities",
        default="Note: StockTrim API does not provide dedicated forecast group endpoints. "
        "This tool provides a conceptual implementation using product categories. "
        "Consider using product categories for grouping forecast products.",
    )


async def _manage_forecast_group_impl(
    request: ManageForecastGroupRequest, context: Context
) -> ManageForecastGroupResponse:
    """Implementation of manage_forecast_group tool.

    Note: The StockTrim API does not provide explicit forecast group endpoints.
    This implementation provides a conceptual framework but is limited by API capabilities.
    Consider using product categories for grouping forecast-related products.

    Args:
        request: Request with forecast group operation details
        context: Server context with StockTrimClient

    Returns:
        ManageForecastGroupResponse with operation result

    Raises:
        NotImplementedError: As StockTrim API does not support forecast groups directly
    """
    logger.warning(
        f"Forecast group management requested but not fully supported by StockTrim API: {request.operation}"
    )

    # Since StockTrim doesn't have dedicated forecast group endpoints,
    # we return a helpful message explaining the limitation
    message = (
        f"Operation '{request.operation}' on forecast group '{request.group_name}' "
        "cannot be completed. StockTrim API does not provide dedicated forecast group "
        "management endpoints. Consider using product categories (category/sub_category "
        "fields) to organize products for forecast management purposes."
    )

    return ManageForecastGroupResponse(
        operation=request.operation,
        group_name=request.group_name,
        message=message,
    )


async def manage_forecast_group(
    request: ManageForecastGroupRequest, ctx: Context
) -> ToolResult:
    """Manage forecast groups (create, update, or delete).

    IMPORTANT: This tool is limited by StockTrim API capabilities. The StockTrim API
    does not provide dedicated forecast group endpoints. This tool returns information
    about this limitation and suggests alternatives.

    For grouping products for forecast purposes, consider using the product category
    and sub_category fields instead.

    Args:
        request: Request with forecast group operation details
        context: Server context with StockTrimClient

    Returns:
        ManageForecastGroupResponse with operation result and guidance

    Example:
        Request: {
            "operation": "create",
            "group_name": "FastMoving",
            "description": "Fast moving products",
            "product_codes": ["WIDGET-001", "WIDGET-002"]
        }
        Returns: {
            "operation": "create",
            "group_name": "FastMoving",
            "message": "...[explanation of API limitation]...",
            "note": "Consider using product categories instead"
        }
    """
    response = await _manage_forecast_group_impl(request, ctx)
    return make_json_result(response)


# ============================================================================
# Tool: update_forecast_settings
# ============================================================================


class UpdateForecastSettingsRequest(BaseModel):
    """Request for updating forecast settings."""

    product_code: str = Field(
        description="Product code to update forecast settings for"
    )
    lead_time_days: int | None = Field(
        default=None,
        description="Lead time in days (maps to lead_time field)",
        ge=0,
    )
    safety_stock_days: int | None = Field(
        default=None,
        description="Safety stock in days (maps to forecast_period field)",
        ge=0,
    )
    service_level: float | None = Field(
        default=None,
        description="Service level percentage (0-100)",
        ge=0,
        le=100,
    )
    minimum_order_quantity: float | None = Field(
        default=None,
        description="Minimum order quantity",
        ge=0,
    )


class UpdateForecastSettingsResponse(BaseModel):
    """Response with updated forecast settings."""

    product_code: str = Field(description="Product code")
    lead_time: int | None = Field(description="Updated lead time in days")
    forecast_period: int | None = Field(
        description="Updated forecast period (safety stock days)"
    )
    service_level: float | None = Field(description="Updated service level")
    minimum_order_quantity: float | None = Field(
        description="Updated minimum order quantity"
    )
    message: str = Field(description="Success message")


async def _update_forecast_settings_impl(
    request: UpdateForecastSettingsRequest, context: Context
) -> UpdateForecastSettingsResponse:
    """Implementation of update_forecast_settings tool.

    Args:
        request: Request with forecast settings to update
        context: Server context with StockTrimClient

    Returns:
        UpdateForecastSettingsResponse with updated settings

    Raises:
        Exception: If product not found or API call fails
    """
    logger.info(f"Updating forecast settings for product: {request.product_code}")

    try:
        # Get services from context
        services = get_services(context)

        # First, fetch the existing product
        existing_product = await services.products.get_by_code(request.product_code)

        if not existing_product:
            raise ValueError(f"Product not found: {request.product_code}")

        # Build update request with only specified forecast fields
        update_data = ProductsRequestDto(
            product_id=existing_product.product_id,
            product_code_readable=to_unset(existing_product.product_code_readable),
        )

        # Update only the fields that were provided
        if request.lead_time_days is not None:
            update_data.lead_time = request.lead_time_days

        if request.safety_stock_days is not None:
            update_data.forecast_period = request.safety_stock_days

        if request.service_level is not None:
            # Convert percentage to decimal (100% = 1.0)
            update_data.service_level = request.service_level / 100.0

        if request.minimum_order_quantity is not None:
            update_data.minimum_order_quantity = request.minimum_order_quantity

        # Update the product using the API (uses client directly for complex update)
        updated_product = await services.client.products.create(update_data)

        service_level = unwrap_unset(updated_product.service_level)
        response = UpdateForecastSettingsResponse(
            product_code=request.product_code,
            lead_time=unwrap_unset(updated_product.lead_time),
            forecast_period=unwrap_unset(updated_product.forecast_period),
            service_level=service_level * 100.0 if service_level is not None else None,
            minimum_order_quantity=unwrap_unset(updated_product.minimum_order_quantity),
            message=f"Successfully updated forecast settings for {request.product_code}",
        )

        logger.info(f"Forecast settings updated for product: {request.product_code}")
        return response

    except Exception as e:
        logger.error(
            f"Failed to update forecast settings for {request.product_code}: {e}"
        )
        raise


async def update_forecast_settings(
    request: UpdateForecastSettingsRequest, ctx: Context
) -> ToolResult:
    """Update forecast parameters for products.

    This workflow tool updates forecast-related settings for a product, including
    lead time, safety stock levels, service level, and minimum order quantities.

    The tool supports partial updates - only the fields provided in the request
    will be updated. All numeric values are validated to ensure they are non-negative.

    Args:
        request: Request with forecast settings to update
        context: Server context with StockTrimClient

    Returns:
        UpdateForecastSettingsResponse with updated settings

    Example:
        Request: {
            "product_code": "WIDGET-001",
            "lead_time_days": 14,
            "safety_stock_days": 7,
            "service_level": 95.0,
            "minimum_order_quantity": 10.0
        }
        Returns: {
            "product_code": "WIDGET-001",
            "lead_time": 14,
            "forecast_period": 7,
            "service_level": 95.0,
            "minimum_order_quantity": 10.0,
            "message": "Successfully updated forecast settings for WIDGET-001"
        }
    """
    response = await _update_forecast_settings_impl(request, ctx)
    return make_json_result(response)


# ============================================================================
# Tool: forecasts_update_and_monitor
# ============================================================================


class ForecastsUpdateAndMonitorRequest(BaseModel):
    """Request for triggering and monitoring forecast recalculation."""

    wait_for_completion: bool = Field(
        default=True, description="Wait and report progress"
    )
    poll_interval_seconds: int = Field(
        default=5, description="Status check interval", ge=1, le=60
    )
    timeout_seconds: int = Field(
        default=600, description="Maximum wait time", ge=30, le=3600
    )


class ForecastsUpdateAndMonitorResponse(BaseModel):
    """Response with forecast update status."""

    triggered: bool = Field(description="Whether forecast calculation was triggered")
    completed: bool = Field(description="Whether calculation completed")
    status_message: str = Field(description="Status message")
    elapsed_seconds: float | None = Field(
        description="Time elapsed during monitoring", default=None
    )
    progress_percentage: int | None = Field(
        description="Final progress percentage", default=None
    )


async def _forecasts_update_and_monitor_impl(
    request: ForecastsUpdateAndMonitorRequest, ctx: Context
) -> ForecastsUpdateAndMonitorResponse:
    """Pure-impl half of forecasts_update_and_monitor."""
    logger.info(
        "forecast_update_triggered",
        wait_for_completion=request.wait_for_completion,
        timeout=request.timeout_seconds,
    )

    triggered = False
    try:
        services = get_services(ctx)
        client = services.client
        await client.forecasting.run_calculations()
        triggered = True  # set after run_calculations() returns successfully

        if not request.wait_for_completion:
            return ForecastsUpdateAndMonitorResponse(
                triggered=True,
                completed=False,
                status_message="Forecast calculation triggered (not waiting for completion)",
            )

        start_time = time.time()
        last_percentage = -1

        while True:
            status = await client.forecasting.get_processing_status()
            elapsed = time.time() - start_time

            current_percentage = unwrap_unset(status.percentage_complete, 0)
            if current_percentage != last_percentage:
                logger.info(
                    "forecast_progress",
                    percentage=current_percentage,
                    elapsed_seconds=round(elapsed, 1),
                    status_message=status.status_message,
                )
                last_percentage = current_percentage

            if not status.is_processing:
                logger.info(
                    "forecast_complete",
                    elapsed_seconds=round(elapsed, 1),
                    final_message=status.status_message,
                )
                return ForecastsUpdateAndMonitorResponse(
                    triggered=True,
                    completed=True,
                    status_message=status.status_message or "Calculation complete",
                    elapsed_seconds=round(elapsed, 1),
                    progress_percentage=100,
                )

            if elapsed > request.timeout_seconds:
                logger.warning(
                    "forecast_timeout",
                    elapsed_seconds=round(elapsed, 1),
                    last_percentage=current_percentage,
                )
                return ForecastsUpdateAndMonitorResponse(
                    triggered=True,
                    completed=False,
                    status_message=(
                        f"Timeout reached after {request.timeout_seconds} seconds; "
                        f"forecast still processing. Last status: "
                        f"{status.status_message or 'Processing...'}"
                    ),
                    elapsed_seconds=round(elapsed, 1),
                    progress_percentage=round(current_percentage),
                )

            await asyncio.sleep(request.poll_interval_seconds)

    except Exception as e:
        # If run_calculations() succeeded but the polling loop blew up, the
        # background calculation is still running — preserve `triggered=True`
        # so callers don't think nothing happened (Copilot review on PR #188).
        logger.error(
            "forecast_update_failed", error=str(e), error_type=type(e).__name__
        )
        return ForecastsUpdateAndMonitorResponse(
            triggered=triggered,
            completed=False,
            status_message=f"Forecast update failed: {e}",
        )


async def forecasts_update_and_monitor(
    request: ForecastsUpdateAndMonitorRequest, ctx: Context
) -> ToolResult:
    """Trigger forecast recalculation and monitor progress.

    This workflow tool triggers StockTrim's forecast calculation system and
    optionally waits for completion while reporting progress.

    Args:
        request: Request with monitoring parameters
        ctx: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ForecastsUpdateAndMonitorResponse)``
        to recover the typed status payload (triggered/completed/elapsed/
        progress_percentage/status_message).
    """
    response = await _forecasts_update_and_monitor_impl(request, ctx)
    return make_json_result(response)


# ============================================================================
# Tool: forecasts_get_for_products
# ============================================================================


class ForecastsGetForProductsRequest(BaseModel):
    """Request for querying forecast data."""

    product_codes: list[str] | None = Field(
        default=None, description="Specific products to query"
    )
    category: str | None = Field(default=None, description="Product category filter")
    supplier_code: str | None = Field(default=None, description="Supplier filter")
    location_code: str | None = Field(default=None, description="Location filter")
    sort_by: Literal["days_until_stockout", "recommended_quantity", "product_code"] = (
        Field(default="days_until_stockout", description="Sort order")
    )
    max_results: int = Field(default=50, description="Limit results", ge=1, le=500)


class ForecastItem(BaseModel):
    """One product's forecast snapshot."""

    product_code: str = Field(description="Product code")
    priority: Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"] = Field(
        description=(
            "Urgency tier derived from days_until_stockout. ``UNKNOWN`` when the "
            "underlying API returned no days_until_stockout — operators should "
            "investigate before treating the item as urgent (would otherwise be "
            "indistinguishable from genuine 0-day-stockout items)."
        )
    )
    current_stock: float = Field(description="Stock on hand (units)")
    days_until_stockout: float | None = Field(
        default=None,
        description="Projected days until stock runs out; ``None`` if forecast data was missing",
    )
    recommended_order_quantity: float = Field(
        description="Recommended order quantity (units)"
    )
    safety_stock_level: float = Field(description="Safety stock level (units)")
    lead_time_days: int | None = Field(
        default=None, description="Lead time in days, if known"
    )


class ForecastsGetForProductsResponse(BaseModel):
    """Typed response for forecasts_get_for_products.

    Hosts that want a markdown report can render one from this structured
    payload (see priority + summary fields).
    """

    items: list[ForecastItem] = Field(
        description="Forecast items, sorted per request.sort_by, capped at max_results"
    )
    total_available: int = Field(
        description="Total matching items before max_results truncation"
    )
    truncated_for_size: bool = Field(
        description="True if results were further trimmed to fit MAX_RESPONSE_SIZE_BYTES"
    )
    sort_by: str = Field(description="Sort order applied")
    filters: dict[str, str | list[str]] = Field(
        description="Filters that were applied (category/supplier/location/product_codes)"
    )
    total_recommended_quantity: float = Field(
        description="Sum of recommended order quantities across returned items"
    )
    average_days_until_stockout: float | None = Field(
        default=None,
        description="Mean days_until_stockout across returned items (None if empty)",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the query failed; non-None signals an error response",
    )


def _priority_for(
    days_until_stockout: float | None,
) -> Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
    """Map a days-until-stockout value to a priority tier.

    Returns ``"UNKNOWN"`` for ``None`` (missing forecast data) so callers
    don't conflate "no data" with "0 days remaining" — the previous
    implementation substituted ``0.0`` which silently classified missing
    data as ``HIGH`` priority (Copilot review on PR #188).
    """
    if days_until_stockout is None:
        return "UNKNOWN"
    if days_until_stockout < HIGH_PRIORITY_THRESHOLD_DAYS:
        return "HIGH"
    if days_until_stockout < MEDIUM_PRIORITY_THRESHOLD_DAYS:
        return "MEDIUM"
    return "LOW"


def _to_forecast_item(item: SkuOptimizedResultsDto) -> ForecastItem:
    """Map an order-plan DTO row to a typed ForecastItem.

    Centralises the UNSET → None / default coercion that was inlined six
    times in ``_forecasts_get_for_products_impl``; tests can now exercise
    the boundary directly without spinning up the full query path.

    ``days_until_stockout`` stays ``None`` when the API returned no value
    so ``_priority_for`` can map it to ``"UNKNOWN"`` — substituting ``0.0``
    would silently bucket missing-data items as ``HIGH``.
    """
    days_until_stockout_raw = unwrap_unset(item.days_until_stock_out)
    days_until_stockout = (
        float(days_until_stockout_raw) if days_until_stockout_raw is not None else None
    )
    lead_time_days_raw = unwrap_unset(item.lead_time_days)
    return ForecastItem(
        product_code=str(unwrap_unset(item.product_code, "Unknown")),
        priority=_priority_for(days_until_stockout),
        current_stock=float(unwrap_unset(item.stock_on_hand, 0.0)),
        days_until_stockout=days_until_stockout,
        recommended_order_quantity=float(unwrap_unset(item.order_quantity, 0.0)),
        safety_stock_level=float(unwrap_unset(item.safety_stock_level, 0.0)),
        lead_time_days=int(lead_time_days_raw)
        if lead_time_days_raw is not None
        else None,
    )


async def _forecasts_get_for_products_impl(
    request: ForecastsGetForProductsRequest, ctx: Context
) -> ForecastsGetForProductsResponse:
    """Pure-impl half of forecasts_get_for_products."""
    logger.info(
        "forecast_query_started",
        category=request.category,
        supplier=request.supplier_code,
        location=request.location_code,
        max_results=request.max_results,
    )

    filters: dict[str, str | list[str]] = {}
    if request.category:
        filters["category"] = request.category
    if request.supplier_code:
        filters["supplier_code"] = request.supplier_code
    if request.location_code:
        filters["location_code"] = request.location_code
    if request.product_codes:
        filters["product_codes"] = request.product_codes

    try:
        services = get_services(ctx)
        client = services.client

        criteria = OrderPlanFilterCriteria(
            category=request.category or UNSET,
            supplier=request.supplier_code or UNSET,
            location=request.location_code or UNSET,
        )
        all_items = await client.order_plan.query(criteria)

        if request.product_codes:
            all_items = [
                item for item in all_items if item.product_code in request.product_codes
            ]

        if request.sort_by == "days_until_stockout":
            all_items.sort(
                key=lambda x: float(unwrap_unset(x.days_until_stock_out, float("inf")))
            )
        elif request.sort_by == "recommended_quantity":
            all_items.sort(
                key=lambda x: float(unwrap_unset(x.recommended_order_quantity, 0)),
                reverse=True,
            )
        else:
            all_items.sort(key=lambda x: str(unwrap_unset(x.product_code, "")))

        limited_items = all_items[: request.max_results]

        truncated_for_size = False
        estimated_size = len(limited_items) * ESTIMATED_CHARS_PER_FORECAST_ITEM
        if estimated_size > MAX_RESPONSE_SIZE_BYTES:
            logger.warning(
                "forecast_result_too_large",
                item_count=len(limited_items),
                estimated_bytes=estimated_size,
            )
            # Only flag truncation when the slice actually drops items —
            # `[: min(50, len(items))]` is a no-op when len <= 50, and
            # falsely setting the flag misleads consumers that use it as
            # a "results were trimmed" indicator (Copilot review, PR #188).
            before_trim = len(limited_items)
            limited_items = limited_items[: min(50, before_trim)]
            truncated_for_size = len(limited_items) < before_trim

        items = [_to_forecast_item(item) for item in limited_items]
        total_recommended = sum(item.recommended_order_quantity for item in items)
        days_values = [
            item.days_until_stockout
            for item in items
            if item.days_until_stockout is not None
        ]
        avg_days = (sum(days_values) / len(days_values)) if days_values else None

        logger.info(
            "forecast_query_complete",
            items_returned=len(items),
            total_items=len(all_items),
        )
        return ForecastsGetForProductsResponse(
            items=items,
            total_available=len(all_items),
            truncated_for_size=truncated_for_size,
            sort_by=request.sort_by,
            filters=filters,
            total_recommended_quantity=total_recommended,
            average_days_until_stockout=avg_days,
        )

    except Exception as e:
        logger.error("forecast_query_failed", error=str(e), error_type=type(e).__name__)
        return ForecastsGetForProductsResponse(
            items=[],
            total_available=0,
            truncated_for_size=False,
            sort_by=request.sort_by,
            filters=filters,
            total_recommended_quantity=0.0,
            average_days_until_stockout=None,
            error=f"Forecast query failed: {e}",
        )


async def forecasts_get_for_products(
    request: ForecastsGetForProductsRequest, ctx: Context
) -> ToolResult:
    """Get forecast data for specific products or categories.

    This workflow tool queries StockTrim's order plan (forecast results) and
    returns structured forecast data. Use this to review demand predictions,
    safety stock levels, and reorder recommendations.

    Args:
        request: Request with query filters
        ctx: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ForecastsGetForProductsResponse)``.

    Example:
        Request: {
            "category": "Widgets",
            "location_code": "WAREHOUSE-A",
            "max_results": 20
        }
        Returns up to 20 forecast items at WAREHOUSE-A in the Widgets category,
        sorted by urgency.
    """
    response = await _forecasts_get_for_products_impl(request, ctx)
    return make_json_result(response)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register forecast management workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(manage_forecast_group)
    mcp.tool()(update_forecast_settings)
    mcp.tool()(forecasts_update_and_monitor)
    mcp.tool()(forecasts_get_for_products)
