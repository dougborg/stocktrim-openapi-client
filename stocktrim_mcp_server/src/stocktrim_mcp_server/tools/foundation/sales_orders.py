"""Sales Order management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params
from stocktrim_mcp_server.utils import unset_to_none

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: create_sales_order
# ============================================================================


class CreateSalesOrderRequest(BaseModel):
    """Request model for creating a sales order."""

    product_id: str = Field(..., description="Product ID for the order")
    order_date: datetime = Field(..., description="Order date (ISO format)")
    quantity: float = Field(..., gt=0, description="Quantity ordered (must be > 0)")
    external_reference_id: str | None = Field(
        None, description="External reference ID (optional)"
    )
    unit_price: float | None = Field(None, ge=0, description="Unit price (optional)")
    location_code: str | None = Field(None, description="Location code (optional)")
    location_name: str | None = Field(None, description="Location name (optional)")
    customer_code: str | None = Field(None, description="Customer code (optional)")
    customer_name: str | None = Field(None, description="Customer name (optional)")


class SalesOrderInfo(BaseModel):
    """Sales order information."""

    id: int | None
    product_id: str
    order_date: datetime
    quantity: float
    external_reference_id: str | None
    unit_price: float | None
    location_code: str | None
    location_name: str | None
    customer_code: str | None
    customer_name: str | None
    location_id: int | None


async def _create_sales_order_impl(
    request: CreateSalesOrderRequest, context: Context
) -> SalesOrderInfo:
    """Implementation of create_sales_order tool.

    Args:
        request: Request containing sales order details
        context: Server context with StockTrimClient

    Returns:
        SalesOrderInfo with created order details

    Raises:
        Exception: If API call fails
    """
    services = get_services(context)

    # Create the sales order via service
    result = await services.sales_orders.create(
        product_id=request.product_id,
        order_date=request.order_date,
        quantity=request.quantity,
        external_reference_id=request.external_reference_id,
        unit_price=request.unit_price,
        location_code=request.location_code,
        location_name=request.location_name,
        customer_code=request.customer_code,
        customer_name=request.customer_name,
    )

    # Build response model (convert UNSET to None for Pydantic)
    return SalesOrderInfo(
        id=unset_to_none(result.id),
        product_id=result.product_id,
        order_date=result.order_date,
        quantity=result.quantity,
        external_reference_id=unset_to_none(result.external_reference_id),
        unit_price=unset_to_none(result.unit_price),
        location_code=unset_to_none(result.location_code),
        location_name=unset_to_none(result.location_name),
        customer_code=unset_to_none(result.customer_code),
        customer_name=unset_to_none(result.customer_name),
        location_id=unset_to_none(result.location_id),
    )


@unpack_pydantic_params
async def create_sales_order(
    request: Annotated[CreateSalesOrderRequest, Unpack()], context: Context
) -> SalesOrderInfo:
    """Create a new sales order.

    This tool creates a sales order in StockTrim for a specific product.
    Note: StockTrim sales orders are product-based (one product per order).

    Args:
        request: Request containing sales order details
        context: Server context with StockTrimClient

    Returns:
        SalesOrderInfo with created order details

    Example:
        Request: {
            "product_id": "WIDGET-001",
            "order_date": "2024-01-15T10:00:00Z",
            "quantity": 10.0,
            "customer_code": "CUST-001",
            "unit_price": 29.99
        }
        Returns: {
            "id": 123,
            "product_id": "WIDGET-001",
            "quantity": 10.0,
            ...
        }
    """
    return await _create_sales_order_impl(request, context)


# ============================================================================
# Tool 2: get_sales_orders
# ============================================================================


class GetSalesOrdersRequest(BaseModel):
    """Request model for getting sales orders."""

    product_id: str | None = Field(None, description="Filter by product ID (optional)")


class GetSalesOrdersResponse(BaseModel):
    """Response containing sales orders."""

    sales_orders: list[SalesOrderInfo]
    total_count: int


async def _get_sales_orders_impl(
    request: GetSalesOrdersRequest, context: Context
) -> GetSalesOrdersResponse:
    """Implementation of get_sales_orders tool.

    Args:
        request: Request with optional product_id filter
        context: Server context with StockTrimClient

    Returns:
        GetSalesOrdersResponse with sales orders

    Raises:
        Exception: If API call fails
    """
    services = get_services(context)

    # Get sales orders via service
    orders = await services.sales_orders.get_all(product_id=request.product_id)

    # Build response (convert UNSET to None for Pydantic)
    order_infos = [
        SalesOrderInfo(
            id=unset_to_none(order.id),
            product_id=order.product_id,
            order_date=order.order_date,
            quantity=order.quantity,
            external_reference_id=unset_to_none(order.external_reference_id),
            unit_price=unset_to_none(order.unit_price),
            location_code=unset_to_none(order.location_code),
            location_name=unset_to_none(order.location_name),
            customer_code=unset_to_none(order.customer_code),
            customer_name=unset_to_none(order.customer_name),
            location_id=unset_to_none(order.location_id),
        )
        for order in orders
    ]

    return GetSalesOrdersResponse(
        sales_orders=order_infos,
        total_count=len(order_infos),
    )


@unpack_pydantic_params
async def get_sales_orders(
    request: Annotated[GetSalesOrdersRequest, Unpack()], context: Context
) -> GetSalesOrdersResponse:
    """Get sales orders, optionally filtered by product.

    This tool retrieves sales orders from StockTrim. You can optionally
    filter by product ID to see orders for a specific product.

    Args:
        request: Request with optional product_id filter
        context: Server context with StockTrimClient

    Returns:
        GetSalesOrdersResponse with sales orders

    Example:
        Request: {"product_id": "WIDGET-001"}
        Returns: {"sales_orders": [...], "total_count": 5}

        Request: {}
        Returns: {"sales_orders": [...], "total_count": 50}
    """
    return await _get_sales_orders_impl(request, context)


# ============================================================================
# Tool 3: list_sales_orders (alias for backward compatibility)
# ============================================================================


class ListSalesOrdersRequest(BaseModel):
    """Request model for listing sales orders (alias for get_sales_orders)."""

    product_id: str | None = Field(None, description="Filter by product ID (optional)")


class ListSalesOrdersResponse(BaseModel):
    """Response containing sales orders (alias for get_sales_orders)."""

    sales_orders: list[SalesOrderInfo]
    total_count: int


@unpack_pydantic_params
async def list_sales_orders(
    request: Annotated[ListSalesOrdersRequest, Unpack()], context: Context
) -> ListSalesOrdersResponse:
    """List all sales orders with optional product filter.

    This is an alias for get_sales_orders for backward compatibility.

    Args:
        request: Request with optional product_id filter
        context: Server context with StockTrimClient

    Returns:
        ListSalesOrdersResponse with sales orders

    Example:
        Request: {}
        Returns: {"sales_orders": [...], "total_count": 50}
    """
    get_request = GetSalesOrdersRequest(product_id=request.product_id)
    get_response = await _get_sales_orders_impl(get_request, context)

    return ListSalesOrdersResponse(
        sales_orders=get_response.sales_orders,
        total_count=get_response.total_count,
    )


# ============================================================================
# Tool 4: delete_sales_orders
# ============================================================================


class DeleteSalesOrdersRequest(BaseModel):
    """Request model for deleting sales orders."""

    product_id: str | None = Field(
        None,
        description="Product ID to filter deletions (deletes all orders for this product)",
    )


class DeleteSalesOrdersResponse(BaseModel):
    """Response for sales order deletion."""

    success: bool
    message: str


@unpack_pydantic_params
async def delete_sales_orders(
    request: Annotated[DeleteSalesOrdersRequest, Unpack()], context: Context
) -> DeleteSalesOrdersResponse:
    """Delete sales orders for a specific product.

    🔴 HIGH-RISK OPERATION: This action permanently deletes sales order data
    and cannot be undone. User confirmation is required via elicitation.

    This tool deletes all sales orders associated with a product after obtaining
    explicit user confirmation through the MCP elicitation protocol.

    For safety, product_id is required (cannot delete all orders without filter).

    Args:
        request: Request with product_id filter
        context: Server context with StockTrimClient

    Returns:
        DeleteSalesOrdersResponse indicating success or cancellation

    Example:
        Request: {"product_id": "WIDGET-001"}
        Returns: {
            "success": true,
            "message": "Sales orders for product WIDGET-001 deleted successfully"
        }
        or {"success": false, "message": "Deletion cancelled by user"}
    """
    if not request.product_id:
        # Safety measure: require a filter to avoid deleting all orders
        return DeleteSalesOrdersResponse(
            success=False,
            message="product_id is required for deletion to prevent accidental bulk deletion.",
        )

    services = get_services(context)

    # Get sales orders for preview
    orders_response = await _get_sales_orders_impl(
        GetSalesOrdersRequest(product_id=request.product_id), context
    )

    if not orders_response.sales_orders:
        return DeleteSalesOrdersResponse(
            success=False,
            message=f"No sales orders found for product: {request.product_id}",
        )

    # Build preview information
    order_count = orders_response.total_count
    total_quantity = sum(order.quantity for order in orders_response.sales_orders)

    # Get unique customer names
    customers = {
        order.customer_name
        for order in orders_response.sales_orders
        if order.customer_name
    }
    customer_info = f"{len(customers)} customers" if customers else "No customer data"

    # Calculate total revenue if prices available
    total_revenue = sum(
        (order.unit_price or 0.0) * order.quantity
        for order in orders_response.sales_orders
        if order.unit_price
    )
    revenue_info = f"${total_revenue:,.2f}" if total_revenue > 0 else "Unknown"

    # Request user confirmation via elicitation
    result = await context.elicit(
        message=f"""⚠️ Delete {order_count} sales order{"s" if order_count != 1 else ""} for product {request.product_id}?

**Orders to Delete**: {order_count}
**Total Quantity**: {total_quantity:,.1f}
**Customers Affected**: {customer_info}
**Total Revenue**: {revenue_info}

This action will permanently delete all sales orders for this product and cannot be undone.

Proceed with deletion?""",
        response_type=None,  # Simple yes/no approval
    )

    # Handle elicitation response
    match result:
        case AcceptedElicitation():
            # User confirmed - proceed with deletion
            success, message = await services.sales_orders.delete_for_product(
                request.product_id
            )
            return DeleteSalesOrdersResponse(
                success=success,
                message=f"✅ {message}" if success else message,
            )

        case DeclinedElicitation():
            # User declined
            return DeleteSalesOrdersResponse(
                success=False,
                message=f"❌ Deletion of sales orders for product {request.product_id} declined by user",
            )

        case CancelledElicitation():
            # User cancelled
            return DeleteSalesOrdersResponse(
                success=False,
                message=f"❌ Deletion of sales orders for product {request.product_id} cancelled by user",
            )

        case _:
            # Unexpected response type
            return DeleteSalesOrdersResponse(
                success=False,
                message="Unexpected elicitation response for sales orders deletion",
            )


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register sales order tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(create_sales_order)
    mcp.tool()(get_sales_orders)
    mcp.tool()(list_sales_orders)
    mcp.tool()(delete_sales_orders)
