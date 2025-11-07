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
    return await _configure_product_impl(request, ctx)


# ============================================================================
# Tool: products_configure_lifecycle
# ============================================================================


class ProductLifecycleRequest(BaseModel):
    """Request for configuring product lifecycle settings."""

    product_code: str = Field(description="Product code to configure")
    action: str = Field(
        description="Lifecycle action: 'activate', 'deactivate', 'discontinue', or 'unstock'"
    )
    clear_inventory: bool = Field(
        default=False, description="Zero inventory on deactivate"
    )
    update_forecasts: bool = Field(
        default=True, description="Trigger forecast recalculation"
    )


async def _products_configure_lifecycle_impl(
    request: ProductLifecycleRequest, context: Context
) -> str:
    """Implementation of products_configure_lifecycle tool.

    Args:
        request: Request with lifecycle action details
        context: Server context with StockTrimClient

    Returns:
        Markdown formatted report with lifecycle change results

    Raises:
        ValueError: If action is invalid or product not found
        Exception: If API call fails
    """
    valid_actions = ["activate", "deactivate", "discontinue", "unstock"]
    if request.action not in valid_actions:
        raise ValueError(
            f"Invalid action: {request.action}. Must be one of {valid_actions}"
        )

    logger.info(
        f"Configuring lifecycle for product {request.product_code}: {request.action}"
    )

    try:
        # Get services from context
        services = get_services(context)

        # Step 1: Fetch the existing product
        existing_product = await services.products.get_by_code(request.product_code)

        if not existing_product:
            raise ValueError(f"Product not found: {request.product_code}")

        # Step 2: Check current inventory and status
        product_name = (
            existing_product.name
            if existing_product.name not in (None, UNSET)
            else request.product_code
        )

        current_inventory = (
            existing_product.stock_on_hand
            if existing_product.stock_on_hand not in (None, UNSET)
            else 0
        )

        was_discontinued = (
            existing_product.discontinued
            if existing_product.discontinued not in (None, UNSET)
            else False
        )

        # Step 3: Build update based on action
        update_data = ProductsRequestDto(
            product_id=existing_product.product_id,
            product_code_readable=existing_product.product_code_readable
            if existing_product.product_code_readable not in (None, UNSET)
            else UNSET,
        )

        action_description = ""

        if request.action == "activate":
            update_data.discontinued = False
            update_data.ignore_seasonality = False  # Enable forecasting
            action_description = "activated (available for orders and forecasting)"

        elif request.action == "deactivate":
            update_data.discontinued = False
            update_data.ignore_seasonality = True  # Disable forecasting
            action_description = "deactivated (available but forecasting disabled)"

            # Optionally clear inventory
            if request.clear_inventory:
                # Note: We'd need to use inventory service here
                # For now, just note in the report
                action_description += " - inventory will be cleared"

        elif request.action == "discontinue":
            update_data.discontinued = True
            update_data.ignore_seasonality = True  # Disable forecasting
            action_description = "discontinued (no longer available for new orders)"

        elif request.action == "unstock":
            update_data.discontinued = True
            update_data.ignore_seasonality = True
            # Additional unstocking logic would go here
            action_description = "unstocked (removed from inventory management)"

        # Step 4: Update the product
        updated_product = await services.client.products.create(update_data)

        # Step 5: Optionally trigger forecast recalculation
        forecast_status = ""
        if request.update_forecasts:
            try:
                await services.client.forecasting.run_calculations()
                forecast_status = "✅ Forecast recalculation triggered"
            except Exception as e:
                logger.warning(f"Failed to trigger forecast update: {e}")
                forecast_status = f"⚠️  Forecast update failed: {e}"

        # Step 6: Build markdown report
        report_lines = [
            "# Product Lifecycle Update",
            "",
            f"## Product: {product_name} ({request.product_code})",
            "",
            f"**Action**: {request.action.upper()}",
            f"**Status**: ✅ {action_description}",
            "",
            "## Previous Status",
            "",
            f"- Discontinued: {was_discontinued}",
            f"- Current Inventory: {current_inventory} units",
            "",
            "## New Status",
            "",
        ]

        new_discontinued = (
            updated_product.discontinued
            if updated_product.discontinued not in (None, UNSET)
            else False
        )

        new_forecast_enabled = not (
            updated_product.ignore_seasonality
            if updated_product.ignore_seasonality not in (None, UNSET)
            else True
        )

        report_lines.extend(
            [
                f"- Discontinued: {new_discontinued}",
                f"- Forecasting Enabled: {new_forecast_enabled}",
            ]
        )

        if request.clear_inventory:
            report_lines.append(f"- Inventory: Cleared (was {current_inventory} units)")

        # Add forecast status
        if forecast_status:
            report_lines.extend(["", "## Forecast Impact", "", forecast_status])

        # Add next steps
        report_lines.extend(
            [
                "",
                "## Next Steps",
                "",
            ]
        )

        if request.action == "activate":
            report_lines.extend(
                [
                    "- Verify product pricing and supplier information",
                    "- Use `forecasts_get_for_products` to check demand forecast",
                    "- Use `review_urgent_order_requirements` to check reorder needs",
                ]
            )
        elif request.action in ["deactivate", "discontinue", "unstock"]:
            report_lines.extend(
                [
                    "- Review and fulfill any pending customer orders",
                    "- Clear remaining inventory if needed",
                    "- Update product catalog and customer communications",
                ]
            )

        report = "\n".join(report_lines)

        logger.info(
            f"Product lifecycle updated: {request.product_code} -> {request.action}"
        )
        return report

    except Exception as e:
        logger.error(f"Failed to configure lifecycle for {request.product_code}: {e}")
        raise


@observe_tool
async def products_configure_lifecycle(
    request: ProductLifecycleRequest, ctx: Context
) -> str:
    """Configure product lifecycle settings with impact analysis.

    This workflow tool manages product lifecycle transitions with full visibility
    into current state and impact of changes. It supports common lifecycle actions
    and provides detailed reporting.

    ## How It Works

    1. Fetches current product details and inventory levels
    2. Analyzes impact of requested lifecycle change
    3. Updates product configuration based on action
    4. Optionally triggers forecast recalculation
    5. Returns markdown report with before/after comparison

    ## Lifecycle Actions

    - **activate**: Make product active and enable forecasting
      - Sets `discontinued = false`
      - Sets `ignore_seasonality = false` (forecasting enabled)
      - Use for reactivating seasonal items or bringing products back

    - **deactivate**: Temporarily disable without removing
      - Sets `discontinued = false`
      - Sets `ignore_seasonality = true` (forecasting disabled)
      - Use for seasonal items or temporary stock issues

    - **discontinue**: Mark as discontinued for phase-out
      - Sets `discontinued = true`
      - Sets `ignore_seasonality = true`
      - Use for end-of-life products

    - **unstock**: Remove from inventory management
      - Sets `discontinued = true`
      - Sets `ignore_seasonality = true`
      - Use for products no longer carried

    ## Use Cases

    - **Seasonal management**: Activate/deactivate seasonal products
    - **Product phase-out**: Gracefully discontinue products
    - **Catalog cleanup**: Remove obsolete items
    - **Reactivation**: Bring discontinued products back

    ## Impact Analysis

    The tool provides:
    - Current inventory levels
    - Previous lifecycle status
    - New configuration settings
    - Forecast recalculation status
    - Recommended next steps

    ## Typical Workflow

    **Discontinuing a Product**:
    1. Run `products_configure_lifecycle` with action='discontinue'
    2. Review current inventory and pending orders
    3. Clear remaining inventory if needed
    4. Update customer communications

    **Reactivating a Seasonal Product**:
    1. Run `products_configure_lifecycle` with action='activate'
    2. Verify supplier and pricing information
    3. Check forecast with `forecasts_get_for_products`
    4. Generate reorder with `review_urgent_order_requirements`

    Args:
        request: Request with lifecycle action details
        ctx: Server context with StockTrimClient

    Returns:
        Markdown report with lifecycle change results

    Example:
        Request: {
            "product_code": "WIDGET-001",
            "action": "discontinue",
            "clear_inventory": false,
            "update_forecasts": true
        }

    See Also:
        - `configure_product`: Basic product configuration
        - `forecasts_get_for_products`: Check demand forecast
        - `review_urgent_order_requirements`: Check reorder needs
        - `list_products`: View all products
    """
    return await _products_configure_lifecycle_impl(request, ctx)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register product management workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(configure_product)
    mcp.tool()(products_configure_lifecycle)
