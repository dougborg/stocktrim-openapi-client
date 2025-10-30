"""Purchase Order management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: get_purchase_order
# ============================================================================


class GetPurchaseOrderRequest(BaseModel):
    """Request model for getting a purchase order."""

    reference_number: str = Field(..., description="Purchase order reference number")


class PurchaseOrderInfo(BaseModel):
    """Purchase order information."""

    reference_number: str
    supplier_code: str | None
    supplier_name: str | None
    status: str | None
    total_cost: float | None
    line_items_count: int


async def _get_purchase_order_impl(
    request: GetPurchaseOrderRequest, context: Context
) -> PurchaseOrderInfo | None:
    """Implementation of get_purchase_order tool.

    Args:
        request: Request containing reference number
        context: Server context with StockTrimClient

    Returns:
        PurchaseOrderInfo if found, None otherwise

    Raises:
        ValueError: If reference number is empty
        Exception: If API call fails
    """
    if not request.reference_number or not request.reference_number.strip():
        raise ValueError("Reference number cannot be empty")

    logger.info(f"Getting purchase order: {request.reference_number}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the find_by_reference convenience method
        po = await client.purchase_orders.find_by_reference(request.reference_number)

        if not po:
            logger.warning(f"Purchase order not found: {request.reference_number}")
            return None

        # Build PurchaseOrderInfo from response
        po_info = PurchaseOrderInfo(
            reference_number=po.reference_number or "",
            supplier_code=po.supplier.supplier_code if po.supplier else None,
            supplier_name=po.supplier.supplier_name if po.supplier else None,
            status=str(po.status.value) if po.status else None,
            total_cost=po.total_cost,
            line_items_count=len(po.line_items) if po.line_items else 0,
        )

        logger.info(f"Purchase order retrieved: {request.reference_number}")
        return po_info

    except Exception as e:
        logger.error(f"Failed to get purchase order {request.reference_number}: {e}")
        raise


async def get_purchase_order(
    request: GetPurchaseOrderRequest, context: Context
) -> PurchaseOrderInfo | None:
    """Get a purchase order by reference number.

    This tool retrieves detailed information about a specific purchase order
    from StockTrim.

    Args:
        request: Request containing reference number
        context: Server context with StockTrimClient

    Returns:
        PurchaseOrderInfo if found, None if not found

    Example:
        Request: {"reference_number": "PO-2024-001"}
        Returns: {"reference_number": "PO-2024-001", "supplier_code": "SUP-001", ...}
    """
    return await _get_purchase_order_impl(request, context)


# ============================================================================
# Tool 2: list_purchase_orders
# ============================================================================


class ListPurchaseOrdersRequest(BaseModel):
    """Request model for listing purchase orders."""

    pass  # No filters for now, V1 API doesn't support filtering


class ListPurchaseOrdersResponse(BaseModel):
    """Response containing purchase orders."""

    purchase_orders: list[PurchaseOrderInfo]
    total_count: int


async def _list_purchase_orders_impl(
    request: ListPurchaseOrdersRequest, context: Context
) -> ListPurchaseOrdersResponse:
    """Implementation of list_purchase_orders tool.

    Args:
        request: Request (no filters supported yet)
        context: Server context with StockTrimClient

    Returns:
        ListPurchaseOrdersResponse with purchase orders

    Raises:
        Exception: If API call fails
    """
    logger.info("Listing purchase orders")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Get all purchase orders
        result = await client.purchase_orders.get_all()

        # Handle API inconsistency - could return single object or list
        if isinstance(result, list):
            pos = result
        else:
            pos = [result] if result else []

        # Build response
        po_infos = [
            PurchaseOrderInfo(
                reference_number=po.reference_number or "",
                supplier_code=po.supplier.supplier_code if po.supplier else None,
                supplier_name=po.supplier.supplier_name if po.supplier else None,
                status=str(po.status.value) if po.status else None,
                total_cost=po.total_cost,
                line_items_count=len(po.line_items) if po.line_items else 0,
            )
            for po in pos
        ]

        response = ListPurchaseOrdersResponse(
            purchase_orders=po_infos,
            total_count=len(po_infos),
        )

        logger.info(f"Found {response.total_count} purchase orders")
        return response

    except Exception as e:
        logger.error(f"Failed to list purchase orders: {e}")
        raise


async def list_purchase_orders(
    request: ListPurchaseOrdersRequest, context: Context
) -> ListPurchaseOrdersResponse:
    """List all purchase orders.

    This tool retrieves all purchase orders from StockTrim (V1 API).

    Args:
        request: Request (no filters supported yet)
        context: Server context with StockTrimClient

    Returns:
        ListPurchaseOrdersResponse with purchase orders

    Example:
        Request: {}
        Returns: {"purchase_orders": [...], "total_count": 15}
    """
    return await _list_purchase_orders_impl(request, context)


# ============================================================================
# Tool 3: delete_purchase_order
# ============================================================================


class DeletePurchaseOrderRequest(BaseModel):
    """Request model for deleting a purchase order."""

    reference_number: str = Field(..., description="Reference number to delete")


class DeletePurchaseOrderResponse(BaseModel):
    """Response for purchase order deletion."""

    success: bool
    message: str


async def _delete_purchase_order_impl(
    request: DeletePurchaseOrderRequest, context: Context
) -> DeletePurchaseOrderResponse:
    """Implementation of delete_purchase_order tool.

    Args:
        request: Request containing reference number
        context: Server context with StockTrimClient

    Returns:
        DeletePurchaseOrderResponse indicating success

    Raises:
        ValueError: If reference number is empty
        Exception: If API call fails
    """
    if not request.reference_number or not request.reference_number.strip():
        raise ValueError("Reference number cannot be empty")

    logger.info(f"Deleting purchase order: {request.reference_number}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Check if PO exists first
        po = await client.purchase_orders.find_by_reference(request.reference_number)
        if not po:
            return DeletePurchaseOrderResponse(
                success=False,
                message=f"Purchase order {request.reference_number} not found",
            )

        # Delete PO
        await client.purchase_orders.delete(reference_number=request.reference_number)

        logger.info(f"Purchase order deleted: {request.reference_number}")
        return DeletePurchaseOrderResponse(
            success=True,
            message=f"Purchase order {request.reference_number} deleted successfully",
        )

    except Exception as e:
        logger.error(f"Failed to delete purchase order {request.reference_number}: {e}")
        raise


async def delete_purchase_order(
    request: DeletePurchaseOrderRequest, context: Context
) -> DeletePurchaseOrderResponse:
    """Delete a purchase order by reference number.

    This tool deletes a purchase order from StockTrim.

    Args:
        request: Request containing reference number
        context: Server context with StockTrimClient

    Returns:
        DeletePurchaseOrderResponse indicating success

    Example:
        Request: {"reference_number": "PO-2024-001"}
        Returns: {"success": true, "message": "Purchase order PO-2024-001 deleted successfully"}
    """
    return await _delete_purchase_order_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register purchase order tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(get_purchase_order)
    mcp.tool()(list_purchase_orders)
    mcp.tool()(delete_purchase_order)
