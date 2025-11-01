"""Inventory management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_public_api_client.client_types import UNSET

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: set_product_inventory
# ============================================================================


class SetInventoryRequest(BaseModel):
    """Request model for setting product inventory."""

    product_id: str = Field(..., description="Product ID to set inventory for")
    stock_on_hand: float | None = Field(
        None, description="Current stock on hand quantity"
    )
    stock_on_order: float | None = Field(None, description="Stock on order quantity")
    location_code: str | None = Field(None, description="Location code")
    location_name: str | None = Field(None, description="Location name")


class InventoryResult(BaseModel):
    """Result of inventory operation."""

    product_id: str
    stock_on_hand: float | None
    stock_on_order: float | None
    location_code: str | None
    location_name: str | None


async def _set_product_inventory_impl(
    request: SetInventoryRequest, context: Context
) -> InventoryResult:
    """Implementation of set_product_inventory tool.

    Args:
        request: Request containing inventory details
        context: Server context with StockTrimClient

    Returns:
        InventoryResult with operation status

    Raises:
        ValueError: If product_id is empty or invalid
        Exception: If API call fails
    """
    if not request.product_id or not request.product_id.strip():
        raise ValueError("Product ID cannot be empty")

    logger.info(f"Setting inventory for product: {request.product_id}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the set_for_product convenience method
        await client.inventory.set_for_product(
            product_id=request.product_id,
            stock_on_hand=(
                request.stock_on_hand if request.stock_on_hand is not None else UNSET
            ),
            stock_on_order=(
                request.stock_on_order if request.stock_on_order is not None else UNSET
            ),
            location_code=(
                request.location_code if request.location_code is not None else UNSET
            ),
            location_name=(
                request.location_name if request.location_name is not None else UNSET
            ),
        )

        inventory_result = InventoryResult(
            product_id=request.product_id,
            stock_on_hand=request.stock_on_hand,
            stock_on_order=request.stock_on_order,
            location_code=request.location_code,
            location_name=request.location_name,
        )

        logger.info(f"Inventory set successfully for product: {request.product_id}")
        return inventory_result

    except Exception as e:
        logger.error(f"Failed to set inventory for product {request.product_id}: {e}")
        raise


async def set_product_inventory(
    request: SetInventoryRequest, context: Context
) -> InventoryResult:
    """Set inventory levels for a product.

    This tool updates stock on hand and stock on order quantities
    for a specific product in StockTrim.

    Args:
        request: Request containing inventory details
        context: Server context with StockTrimClient

    Returns:
        InventoryResult with updated inventory details

    Example:
        Request: {
            "product_id": "123",
            "stock_on_hand": 50.0,
            "stock_on_order": 100.0,
            "location_code": "WAREHOUSE-A"
        }
        Returns: {
            "product_id": "123",
            "stock_on_hand": 50.0,
            "stock_on_order": 100.0,
            "location_code": "WAREHOUSE-A",
            "location_name": null
        }
    """
    return await _set_product_inventory_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register inventory tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(set_product_inventory)
