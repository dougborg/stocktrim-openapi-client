"""Product configuration management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for configuring product settings
such as discontinuing products and updating forecast configurations.
"""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Tool: configure_product
# ============================================================================


class ConfigureProductRequest(BaseModel):
    """Request for configuring product settings."""

    product_code: str = Field(description="Product code to configure")
    discontinue: bool | None = Field(
        default=None, description="Mark product as discontinued"
    )
    configure_forecast: bool | None = Field(
        default=None,
        description="Enable/disable forecast calculation for this product (maps to ignore_seasonality)",
    )


class ConfigureProductResponse(BaseModel):
    """Response with updated product configuration."""

    product_code: str = Field(description="Product code")
    discontinued: bool | None = Field(description="Product discontinued status")
    ignore_seasonality: bool | None = Field(
        description="Forecast calculation status (True = forecast disabled)"
    )
    message: str = Field(description="Success message")


async def _configure_product_impl(
    request: ConfigureProductRequest, context: Context
) -> ConfigureProductResponse:
    """Implementation of configure_product tool.

    Args:
        request: Request with product configuration settings
        context: Server context with StockTrimClient

    Returns:
        ConfigureProductResponse with updated product info

    Raises:
        Exception: If product not found or API call fails
    """
    logger.info(f"Configuring product: {request.product_code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # First, fetch the existing product to get its product_id
        existing_product = await client.products.find_by_code(request.product_code)

        if not existing_product:
            raise ValueError(f"Product not found: {request.product_code}")

        # Build update request with only specified fields
        # Note: StockTrim API requires product_id for updates via POST
        update_data = ProductsRequestDto(
            product_id=existing_product.product_id,
            product_code_readable=existing_product.product_code_readable
            if existing_product.product_code_readable not in (None, UNSET)
            else UNSET,
        )

        # Only set fields that were provided in the request
        if request.discontinue is not None:
            update_data.discontinued = request.discontinue

        if request.configure_forecast is not None:
            # configure_forecast=True means enable forecasting (ignore_seasonality=False)
            # configure_forecast=False means disable forecasting (ignore_seasonality=True)
            update_data.ignore_seasonality = not request.configure_forecast

        # Update the product using the API
        updated_product = await client.products.create(update_data)

        response = ConfigureProductResponse(
            product_code=request.product_code,
            discontinued=updated_product.discontinued
            if updated_product.discontinued not in (None, UNSET)
            else None,
            ignore_seasonality=updated_product.ignore_seasonality
            if updated_product.ignore_seasonality not in (None, UNSET)
            else None,
            message=f"Successfully configured product {request.product_code}",
        )

        logger.info(f"Product configured: {request.product_code}")
        return response

    except Exception as e:
        logger.error(f"Failed to configure product {request.product_code}: {e}")
        raise


async def configure_product(
    request: ConfigureProductRequest, context: Context
) -> ConfigureProductResponse:
    """Configure product settings such as discontinue status and forecast configuration.

    This workflow tool updates product configuration settings. It supports partial
    updates, meaning only the fields provided in the request will be updated.

    The tool first fetches the existing product to ensure it exists and to get its
    product_id, then applies the requested configuration changes.

    Args:
        request: Request with product configuration settings
        context: Server context with StockTrimClient

    Returns:
        ConfigureProductResponse with updated product info

    Example:
        Request: {
            "product_code": "WIDGET-001",
            "discontinue": true,
            "configure_forecast": false
        }
        Returns: {
            "product_code": "WIDGET-001",
            "discontinued": true,
            "ignore_seasonality": true,
            "message": "Successfully configured product WIDGET-001"
        }
    """
    return await _configure_product_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register product management workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(configure_product)
