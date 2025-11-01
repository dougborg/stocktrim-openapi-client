"""Sales Order management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from datetime import datetime

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

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
        ValueError: If validation fails
        Exception: If API call fails
    """
    if not request.product_id or not request.product_id.strip():
        raise ValueError("Product ID cannot be empty")

    if request.quantity <= 0:
        raise ValueError("Quantity must be greater than 0")

    logger.info(
        f"Creating sales order for product {request.product_id}, "
        f"quantity {request.quantity}"
    )

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Import generated model here to avoid circular imports
        from stocktrim_public_api_client.generated.models.sales_order_request_dto import (
            SalesOrderRequestDto,
        )

        # Build request DTO from our Pydantic model
        order_dto = SalesOrderRequestDto(
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

        # Create the sales order
        result = await client.sales_orders.create(order_dto)

        # Build response model
        order_info = SalesOrderInfo(
            id=result.id if hasattr(result, "id") else None,
            product_id=result.product_id,
            order_date=result.order_date,
            quantity=result.quantity,
            external_reference_id=result.external_reference_id
            if hasattr(result, "external_reference_id")
            else None,
            unit_price=result.unit_price if hasattr(result, "unit_price") else None,
            location_code=result.location_code
            if hasattr(result, "location_code")
            else None,
            location_name=result.location_name
            if hasattr(result, "location_name")
            else None,
            customer_code=result.customer_code
            if hasattr(result, "customer_code")
            else None,
            customer_name=result.customer_name
            if hasattr(result, "customer_name")
            else None,
            location_id=result.location_id if hasattr(result, "location_id") else None,
        )

        logger.info(
            f"Sales order created successfully for product {request.product_id}"
        )
        return order_info

    except Exception as e:
        logger.error(f"Failed to create sales order: {e}")
        raise


async def create_sales_order(
    request: CreateSalesOrderRequest, context: Context
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

    product_id: str | None = Field(
        None, description="Filter by product ID (optional)"
    )


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
    logger.info(
        f"Getting sales orders"
        + (f" for product {request.product_id}" if request.product_id else "")
    )

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Get sales orders, optionally filtered by product
        if request.product_id:
            orders = await client.sales_orders.get_for_product(request.product_id)
        else:
            orders = await client.sales_orders.get_all()

        # Handle API inconsistency - could return single object or list
        if isinstance(orders, list):
            order_list = orders
        else:
            order_list = [orders] if orders else []

        # Build response
        order_infos = [
            SalesOrderInfo(
                id=order.id if hasattr(order, "id") else None,
                product_id=order.product_id,
                order_date=order.order_date,
                quantity=order.quantity,
                external_reference_id=order.external_reference_id
                if hasattr(order, "external_reference_id")
                else None,
                unit_price=order.unit_price if hasattr(order, "unit_price") else None,
                location_code=order.location_code
                if hasattr(order, "location_code")
                else None,
                location_name=order.location_name
                if hasattr(order, "location_name")
                else None,
                customer_code=order.customer_code
                if hasattr(order, "customer_code")
                else None,
                customer_name=order.customer_name
                if hasattr(order, "customer_name")
                else None,
                location_id=order.location_id if hasattr(order, "location_id") else None,
            )
            for order in order_list
        ]

        response = GetSalesOrdersResponse(
            sales_orders=order_infos,
            total_count=len(order_infos),
        )

        logger.info(f"Found {response.total_count} sales orders")
        return response

    except Exception as e:
        logger.error(f"Failed to get sales orders: {e}")
        raise


async def get_sales_orders(
    request: GetSalesOrdersRequest, context: Context
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

    product_id: str | None = Field(
        None, description="Filter by product ID (optional)"
    )


class ListSalesOrdersResponse(BaseModel):
    """Response containing sales orders (alias for get_sales_orders)."""

    sales_orders: list[SalesOrderInfo]
    total_count: int


async def list_sales_orders(
    request: ListSalesOrdersRequest, context: Context
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
    deleted_count: int | None = None


async def _delete_sales_orders_impl(
    request: DeleteSalesOrdersRequest, context: Context
) -> DeleteSalesOrdersResponse:
    """Implementation of delete_sales_orders tool.

    Args:
        request: Request with optional product_id filter
        context: Server context with StockTrimClient

    Returns:
        DeleteSalesOrdersResponse indicating success

    Raises:
        ValueError: If no filter provided (safety measure)
        Exception: If API call fails
    """
    if not request.product_id:
        # Safety measure: require a filter to avoid deleting all orders
        raise ValueError(
            "product_id is required for deletion. "
            "To delete all sales orders, use delete_all_sales_orders tool."
        )

    logger.info(f"Deleting sales orders for product: {request.product_id}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Get count before deletion for reporting
        orders_before = await client.sales_orders.get_for_product(request.product_id)
        count = len(orders_before) if isinstance(orders_before, list) else 1

        # Delete sales orders for product
        await client.sales_orders.delete_for_product(request.product_id)

        logger.info(f"Sales orders deleted for product: {request.product_id}")
        return DeleteSalesOrdersResponse(
            success=True,
            message=f"Sales orders for product {request.product_id} deleted successfully",
            deleted_count=count,
        )

    except Exception as e:
        logger.error(f"Failed to delete sales orders: {e}")
        raise


async def delete_sales_orders(
    request: DeleteSalesOrdersRequest, context: Context
) -> DeleteSalesOrdersResponse:
    """Delete sales orders for a specific product.

    This tool deletes all sales orders associated with a product.
    For safety, product_id is required (cannot delete all orders without filter).

    Args:
        request: Request with product_id filter
        context: Server context with StockTrimClient

    Returns:
        DeleteSalesOrdersResponse indicating success

    Example:
        Request: {"product_id": "WIDGET-001"}
        Returns: {
            "success": true,
            "message": "Sales orders for product WIDGET-001 deleted successfully",
            "deleted_count": 5
        }
    """
    return await _delete_sales_orders_impl(request, context)


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
