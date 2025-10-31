"""Forecast management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for managing forecast groups
and updating forecast settings for products.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)

logger = logging.getLogger(__name__)

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
    request: ManageForecastGroupRequest, context: Context
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
    return await _manage_forecast_group_impl(request, context)


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
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # First, fetch the existing product
        existing_product = await client.products.find_by_code(request.product_code)

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

        # Update the product using the API
        updated_product = await client.products.create(update_data)

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


async def update_forecast_settings(
    request: UpdateForecastSettingsRequest, context: Context
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
    return await _update_forecast_settings_impl(request, context)


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
