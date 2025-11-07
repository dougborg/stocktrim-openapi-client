"""Forecast management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for managing forecast groups
and updating forecast settings for products.
"""

from __future__ import annotations

import asyncio
import time
from typing import Literal

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.observability import observe_tool
from stocktrim_mcp_server.templates import format_template, load_template
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria import (
    OrderPlanFilterCriteria,
)
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
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


@observe_tool
async def manage_forecast_group(
    request: ManageForecastGroupRequest, ctx: Context
) -> ManageForecastGroupResponse:
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
    return await _manage_forecast_group_impl(request, ctx)


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
            product_code_readable=existing_product.product_code_readable
            if existing_product.product_code_readable not in (None, UNSET)
            else UNSET,
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

        response = UpdateForecastSettingsResponse(
            product_code=request.product_code,
            lead_time=updated_product.lead_time
            if updated_product.lead_time not in (None, UNSET)
            else None,
            forecast_period=updated_product.forecast_period
            if updated_product.forecast_period not in (None, UNSET)
            else None,
            service_level=(updated_product.service_level * 100.0)
            if updated_product.service_level not in (None, UNSET)
            else None,
            minimum_order_quantity=updated_product.minimum_order_quantity
            if updated_product.minimum_order_quantity not in (None, UNSET)
            else None,
            message=f"Successfully updated forecast settings for {request.product_code}",
        )

        logger.info(f"Forecast settings updated for product: {request.product_code}")
        return response

    except Exception as e:
        logger.error(
            f"Failed to update forecast settings for {request.product_code}: {e}"
        )
        raise


@observe_tool
async def update_forecast_settings(
    request: UpdateForecastSettingsRequest, ctx: Context
) -> UpdateForecastSettingsResponse:
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
    return await _update_forecast_settings_impl(request, ctx)


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


@observe_tool
async def forecasts_update_and_monitor(
    request: ForecastsUpdateAndMonitorRequest, ctx: Context
) -> str:
    """Trigger forecast recalculation and monitor progress.

    This workflow tool triggers StockTrim's forecast calculation system and
    optionally waits for completion while reporting progress. This is essential
    after data imports, product changes, or before planning operations.

    The tool provides real-time progress updates via logging and returns a
    markdown-formatted status report.

    Args:
        request: Request with monitoring parameters
        ctx: Server context with StockTrimClient

    Returns:
        Markdown-formatted status report with:
        - Trigger confirmation
        - Progress updates (if waiting)
        - Completion status
        - Time elapsed
        - Recommended next steps

    Example:
        Request: {
            "wait_for_completion": true,
            "poll_interval_seconds": 5,
            "timeout_seconds": 300
        }
        Returns markdown report:
        # Forecast Update Status

        Status: Complete
        Time Elapsed: 45.2 seconds
        Progress: 100%

        The forecast calculation completed successfully.

        ## Next Steps
        - Use forecasts_get_for_products to review updated forecasts
        - Use review_urgent_order_requirements to generate purchase orders
    """
    logger.info(
        "forecast_update_triggered",
        wait_for_completion=request.wait_for_completion,
        timeout=request.timeout_seconds,
    )

    try:
        # Get services from context
        services = get_services(ctx)
        client = services.client

        # Trigger forecast recalculation
        await client.forecasting.run_calculations()

        if not request.wait_for_completion:
            return load_template("forecast_triggered")

        # Monitor progress
        start_time = time.time()
        last_percentage = -1

        while True:
            status = await client.forecasting.get_processing_status()
            elapsed = time.time() - start_time

            # Log progress if it changed
            current_percentage = (
                status.percentage_complete
                if status.percentage_complete not in (None, UNSET)
                else 0
            )
            if current_percentage != last_percentage:
                logger.info(
                    "forecast_progress",
                    percentage=current_percentage,
                    elapsed_seconds=round(elapsed, 1),
                    status_message=status.status_message,
                )
                last_percentage = current_percentage

            # Check if done
            if not status.is_processing:
                logger.info(
                    "forecast_complete",
                    elapsed_seconds=round(elapsed, 1),
                    final_message=status.status_message,
                )
                return format_template(
                    "forecast_complete",
                    elapsed=elapsed,
                    status_message=status.status_message or "Calculation complete",
                )

            # Check timeout
            if elapsed > request.timeout_seconds:
                logger.warning(
                    "forecast_timeout",
                    elapsed_seconds=round(elapsed, 1),
                    last_percentage=current_percentage,
                )
                return format_template(
                    "forecast_timeout",
                    elapsed=elapsed,
                    current_percentage=current_percentage,
                    timeout_seconds=request.timeout_seconds,
                    status_message=status.status_message or "Processing...",
                )

            # Wait before next poll
            await asyncio.sleep(request.poll_interval_seconds)

    except Exception as e:
        logger.error(
            "forecast_update_failed", error=str(e), error_type=type(e).__name__
        )
        return format_template("forecast_failed", error=str(e))


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


@observe_tool
async def forecasts_get_for_products(
    request: ForecastsGetForProductsRequest, ctx: Context
) -> str:
    """Get forecast data for specific products or categories.

    This workflow tool queries StockTrim's order plan (forecast results) and formats
    the data into an actionable markdown report. Use this to review demand predictions,
    safety stock levels, and reorder recommendations.

    The tool provides comprehensive forecast analysis including:
    - Current inventory levels
    - Demand forecasts
    - Days until stockout
    - Recommended reorder quantities
    - Safety stock levels
    - Forecast confidence metrics

    Args:
        request: Request with query filters
        ctx: Server context with StockTrimClient

    Returns:
        Markdown-formatted forecast report with:
        - Product-by-product forecast details
        - Current vs recommended stock levels
        - Days until stockout
        - Reorder recommendations
        - Summary statistics

    Example:
        Request: {
            "category": "Widgets",
            "location_code": "WAREHOUSE-A",
            "max_results": 20
        }
        Returns markdown report with forecast data for top 20 widgets at WAREHOUSE-A
    """
    logger.info(
        "forecast_query_started",
        category=request.category,
        supplier=request.supplier_code,
        location=request.location_code,
        max_results=request.max_results,
    )

    try:
        # Get services from context
        services = get_services(ctx)
        client = services.client

        # Build filter criteria
        criteria = OrderPlanFilterCriteria(
            category=request.category or UNSET,
            supplier=request.supplier_code or UNSET,
            location=request.location_code or UNSET,
        )

        # Query order plan
        all_items = await client.order_plan.query(criteria)

        # Filter by specific product codes if provided
        if request.product_codes:
            all_items = [
                item for item in all_items if item.product_code in request.product_codes
            ]

        # Sort based on request
        if request.sort_by == "days_until_stockout":
            all_items.sort(
                key=lambda x: float(x.days_until_stock_out)
                if x.days_until_stock_out not in (None, UNSET)
                else float("inf")
            )
        elif request.sort_by == "recommended_quantity":
            all_items.sort(
                key=lambda x: float(x.recommended_order_quantity)
                if x.recommended_order_quantity not in (None, UNSET)
                else 0,
                reverse=True,
            )
        else:  # product_code
            all_items.sort(
                key=lambda x: str(x.product_code)
                if x.product_code not in (None, UNSET)
                else ""
            )

        # Limit results
        limited_items = all_items[: request.max_results]

        # Check token budget
        estimated_size = len(limited_items) * ESTIMATED_CHARS_PER_FORECAST_ITEM
        if estimated_size > MAX_RESPONSE_SIZE_BYTES:
            logger.warning(
                "forecast_result_too_large",
                item_count=len(limited_items),
                estimated_bytes=estimated_size,
            )
            # Reduce to fit budget
            limited_items = limited_items[: min(50, len(limited_items))]

        # Build markdown report
        report_lines = ["# Forecast Data\n"]

        # Add filters
        filter_parts = []
        if request.category:
            filter_parts.append(f"Category: {request.category}")
        if request.supplier_code:
            filter_parts.append(f"Supplier: {request.supplier_code}")
        if request.location_code:
            filter_parts.append(f"Location: {request.location_code}")
        if filter_parts:
            report_lines.append(f"**Filters**: {', '.join(filter_parts)}\n")

        report_lines.append(
            f"**Results**: Showing {len(limited_items)} of {len(all_items)} total items\n"
        )
        report_lines.append(f"**Sorted by**: {request.sort_by}\n")

        if not limited_items:
            report_lines.append(load_template("forecast_query_empty"))
            return "\n".join(report_lines)

        # Add summary statistics
        total_recommended = sum(
            float(item.order_quantity)
            if item.order_quantity not in (None, UNSET)
            else 0
            for item in limited_items
        )
        avg_days_until_stockout = sum(
            float(item.days_until_stock_out)
            if item.days_until_stock_out not in (None, UNSET)
            else 0
            for item in limited_items
        ) / len(limited_items)

        report_lines.append("\n## Summary\n")
        report_lines.append(
            f"- **Total Recommended Order Quantity**: {total_recommended:,.0f} units\n"
        )
        report_lines.append(
            f"- **Average Days Until Stockout**: {avg_days_until_stockout:.1f} days\n"
        )

        # Add detailed product data
        report_lines.append("\n## Product Forecasts\n")

        for item in limited_items:
            product_code = (
                item.product_code
                if item.product_code not in (None, UNSET)
                else "Unknown"
            )
            # Note: Using product_code as name since DTO doesn't have product_description
            product_name = product_code
            current_stock = (
                float(item.stock_on_hand)
                if item.stock_on_hand not in (None, UNSET)
                else 0
            )
            days_until_stockout = (
                float(item.days_until_stock_out)
                if item.days_until_stock_out not in (None, UNSET)
                else 0
            )
            recommended_qty = (
                float(item.order_quantity)
                if item.order_quantity not in (None, UNSET)
                else 0
            )
            safety_stock = (
                float(item.safety_stock_level)
                if item.safety_stock_level not in (None, UNSET)
                else 0
            )

            # Priority indicator based on days until stockout
            if days_until_stockout < HIGH_PRIORITY_THRESHOLD_DAYS:
                priority = "🔴 HIGH"
            elif days_until_stockout < MEDIUM_PRIORITY_THRESHOLD_DAYS:
                priority = "🟡 MEDIUM"
            else:
                priority = "🟢 LOW"

            report_lines.append(f"\n### {product_code} - {product_name}\n")
            report_lines.append(f"**Priority**: {priority}\n")
            report_lines.append(f"- **Current Stock**: {current_stock:,.0f} units\n")
            report_lines.append(
                f"- **Days Until Stockout**: {days_until_stockout:.1f} days\n"
            )
            report_lines.append(
                f"- **Recommended Order**: {recommended_qty:,.0f} units\n"
            )
            report_lines.append(f"- **Safety Stock**: {safety_stock:,.0f} units\n")

            # Add lead time if available
            if item.lead_time_days not in (None, UNSET):
                report_lines.append(f"- **Lead Time**: {item.lead_time_days} days\n")

        # Add next steps
        report_lines.append("\n## Next Steps\n")
        report_lines.append("- Review high priority items (< 7 days until stockout)\n")
        report_lines.append(
            "- Use `review_urgent_order_requirements` to plan purchase orders\n"
        )
        report_lines.append(
            "- Use `generate_purchase_orders_from_urgent_items` to create draft POs\n"
        )
        report_lines.append(
            "- Update forecast settings for products with unexpected recommendations\n"
        )

        logger.info(
            "forecast_query_complete",
            items_returned=len(limited_items),
            total_items=len(all_items),
        )

        return "\n".join(report_lines)

    except Exception as e:
        logger.error("forecast_query_failed", error=str(e), error_type=type(e).__name__)
        return format_template("forecast_query_failed", error=str(e))


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
