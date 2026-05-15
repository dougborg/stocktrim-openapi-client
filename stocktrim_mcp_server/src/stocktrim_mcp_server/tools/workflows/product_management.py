"""Product configuration management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for configuring product settings
such as discontinuing products and updating forecast configurations.
"""

from __future__ import annotations

from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
from stocktrim_mcp_server.utils import to_unset, unwrap_unset
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
            product_code_readable=to_unset(existing_product.product_code_readable),
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
            discontinued=unwrap_unset(updated_product.discontinued),
            ignore_seasonality=unwrap_unset(updated_product.ignore_seasonality),
            message=f"Successfully configured product {request.product_code}",
        )

        logger.info(f"Product configured: {request.product_code}")
        return response

    except Exception as e:
        logger.error(f"Failed to configure product {request.product_code}: {e}")
        raise


async def configure_product(
    request: ConfigureProductRequest, ctx: Context
) -> ToolResult:
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
    response = await _configure_product_impl(request, ctx)
    return make_json_result(response)


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


class ProductLifecycleStatus(BaseModel):
    """Lifecycle status snapshot (used for before / after)."""

    discontinued: bool = Field(description="Whether the product is discontinued")
    forecast_enabled: bool = Field(
        description="Whether forecasting is enabled (inverse of ignore_seasonality)"
    )


class ProductLifecycleResponse(BaseModel):
    """Typed response for products_configure_lifecycle.

    Replaces the previous hand-rendered markdown report. Hosts can render
    their own formatting from this structured data.
    """

    product_code: str = Field(description="Product code that was updated")
    product_name: str = Field(description="Resolved product name (or code if unknown)")
    action: str = Field(description="Lifecycle action that was applied")
    action_description: str = Field(description="Human-readable summary of the action")
    previous_status: ProductLifecycleStatus = Field(
        description="Status before the update"
    )
    new_status: ProductLifecycleStatus = Field(description="Status after the update")
    previous_inventory: float = Field(description="Inventory level before the update")
    inventory_cleared: bool = Field(
        description="Whether clear_inventory was requested in this update"
    )
    forecast_recalculation_triggered: bool = Field(
        description="True if forecast recalculation was attempted and succeeded"
    )
    forecast_recalculation_message: str | None = Field(
        default=None,
        description="Status or error message from the forecast recalculation attempt",
    )
    next_steps: list[str] = Field(
        description="Recommended follow-up actions based on the lifecycle change"
    )


async def _products_configure_lifecycle_impl(
    request: ProductLifecycleRequest, context: Context
) -> ProductLifecycleResponse:
    """Implementation of products_configure_lifecycle tool.

    Args:
        request: Request with lifecycle action details
        context: Server context with StockTrimClient

    Returns:
        ProductLifecycleResponse with before/after status and next steps.

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
        services = get_services(context)
        existing_product = await services.products.get_by_code(request.product_code)
        if not existing_product:
            raise ValueError(f"Product not found: {request.product_code}")

        product_name = unwrap_unset(existing_product.name, request.product_code)
        current_inventory = unwrap_unset(existing_product.stock_on_hand, 0)
        was_discontinued = unwrap_unset(existing_product.discontinued, False)
        previous_forecast_enabled = not unwrap_unset(
            existing_product.ignore_seasonality, True
        )

        update_data = ProductsRequestDto(
            product_id=existing_product.product_id,
            product_code_readable=to_unset(existing_product.product_code_readable),
        )

        action_description = ""
        if request.action == "activate":
            update_data.discontinued = False
            update_data.ignore_seasonality = False
            action_description = "activated (available for orders and forecasting)"
        elif request.action == "deactivate":
            update_data.discontinued = False
            update_data.ignore_seasonality = True
            action_description = "deactivated (available but forecasting disabled)"
            if request.clear_inventory:
                action_description += " - inventory will be cleared"
        elif request.action == "discontinue":
            update_data.discontinued = True
            update_data.ignore_seasonality = True
            action_description = "discontinued (no longer available for new orders)"
        elif request.action == "unstock":
            update_data.discontinued = True
            update_data.ignore_seasonality = True
            action_description = "unstocked (removed from inventory management)"

        updated_product = await services.client.products.create(update_data)

        forecast_triggered = False
        forecast_message: str | None = None
        if request.update_forecasts:
            try:
                await services.client.forecasting.run_calculations()
                forecast_triggered = True
                forecast_message = "Forecast recalculation triggered"
            except Exception as e:
                logger.warning(f"Failed to trigger forecast update: {e}")
                forecast_message = f"Forecast update failed: {e}"

        new_discontinued = unwrap_unset(updated_product.discontinued, False)
        new_forecast_enabled = not unwrap_unset(
            updated_product.ignore_seasonality, True
        )

        if request.action == "activate":
            next_steps = [
                "Verify product pricing and supplier information",
                "Use `forecasts_get_for_products` to check demand forecast",
                "Use `review_urgent_order_requirements` to check reorder needs",
            ]
        else:
            next_steps = [
                "Review and fulfill any pending customer orders",
                "Clear remaining inventory if needed",
                "Update product catalog and customer communications",
            ]

        logger.info(
            f"Product lifecycle updated: {request.product_code} -> {request.action}"
        )
        return ProductLifecycleResponse(
            product_code=request.product_code,
            product_name=product_name,
            action=request.action,
            action_description=action_description,
            previous_status=ProductLifecycleStatus(
                discontinued=was_discontinued,
                forecast_enabled=previous_forecast_enabled,
            ),
            new_status=ProductLifecycleStatus(
                discontinued=new_discontinued,
                forecast_enabled=new_forecast_enabled,
            ),
            previous_inventory=float(current_inventory),
            inventory_cleared=request.clear_inventory,
            forecast_recalculation_triggered=forecast_triggered,
            forecast_recalculation_message=forecast_message,
            next_steps=next_steps,
        )

    except Exception as e:
        # Preserve diagnostic context on failures — the pre-migration impl
        # had this logger.error wrapper and peer impls in this PR
        # (_create_supplier_with_products_impl, _update_forecast_settings_impl)
        # kept theirs. Dropping it during the markdown → typed-response refactor
        # would have silently lost operator visibility (Copilot review, PR #188).
        logger.error(f"Failed to configure lifecycle for {request.product_code}: {e}")
        raise


async def products_configure_lifecycle(
    request: ProductLifecycleRequest, ctx: Context
) -> ToolResult:
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
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ProductLifecycleResponse)``.

    See Also:
        - `configure_product`: Basic product configuration
        - `forecasts_get_for_products`: Check demand forecast
        - `review_urgent_order_requirements`: Check reorder needs
        - `list_products`: View all products
    """
    response = await _products_configure_lifecycle_impl(request, ctx)
    return make_json_result(response)


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
