"""Product configuration management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for configuring product settings
such as discontinuing products and updating forecast configurations.
"""

from __future__ import annotations

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.observability import observe_tool
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)

logger = get_logger(__name__)

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
        # Get services from context
        services = get_services(context)

        # First, fetch the existing product to get its product_id
        existing_product = await services.products.get_by_code(request.product_code)

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

        # Update the product using the API (uses client directly for complex update)
        updated_product = await services.client.products.create(update_data)

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


@observe_tool
async def configure_product(
    request: ConfigureProductRequest, ctx: Context
) -> ConfigureProductResponse:
    """Configure product lifecycle settings (discontinue status, forecast configuration).

    This workflow tool manages product lifecycle transitions such as discontinuation
    and seasonal activation. It supports partial updates, updating only the fields
    provided in the request.

    ## How It Works

    1. Fetches the existing product to verify it exists
    2. Applies only the requested configuration changes
    3. Returns updated product settings

    ## Common Use Cases

    - **Product Discontinuation**: Mark products as discontinued and stop forecasting
    - **Seasonal Activation**: Enable products and forecasting for seasonal items
    - **Product End-of-Life**: Prepare products for phase-out
    - **SKU Rationalization**: Disable forecasting for slow-moving items

    ## Best Practices

    1. **Discontinue + Disable Forecast**: When discontinuing, also set `configure_forecast=false`
    2. **Activate + Enable Forecast**: When activating seasonal products, set `configure_forecast=true`
    3. **Update Forecast Settings After**: Use `update_forecast_settings` to adjust parameters
    4. **Re-run Forecasts**: After configuration changes, run `forecasts_update_and_monitor`

    ## Field Mappings

    - `discontinue` → `discontinued` (product lifecycle status)
    - `configure_forecast=true` → `ignore_seasonality=false` (forecasting enabled)
    - `configure_forecast=false` → `ignore_seasonality=true` (forecasting disabled)

    Args:
        request: Request with product configuration settings
        context: Server context with StockTrimClient

    Returns:
        ConfigureProductResponse with updated product info, including:
        - Product code
        - Discontinued status
        - Forecast configuration status
        - Success message

    Examples:
        **Discontinuing a Product**:
        Request: {
            "product_code": "WIDGET-OLD",
            "discontinue": true,
            "configure_forecast": false
        }
        Returns: {
            "product_code": "WIDGET-OLD",
            "discontinued": true,
            "ignore_seasonality": true,
            "message": "Successfully configured product WIDGET-OLD"
        }

        **Activating a Seasonal Product**:
        Request: {
            "product_code": "HOLIDAY-001",
            "discontinue": false,
            "configure_forecast": true
        }
        Returns: {
            "product_code": "HOLIDAY-001",
            "discontinued": false,
            "ignore_seasonality": false,
            "message": "Successfully configured product HOLIDAY-001"
        }

    See Also:
        - Complete workflow: docs/mcp-server/examples.md#workflow-4-product-lifecycle-management
        - `update_forecast_settings`: Adjust forecast parameters after configuration
        - `forecasts_update_and_monitor`: Re-calculate forecasts after changes
    """
    return await _configure_product_impl(request, ctx)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register product management workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(configure_product)
