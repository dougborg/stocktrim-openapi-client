"""Purchase Order management tools for StockTrim MCP Server."""

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
        context: Server context with services

    Returns:
        PurchaseOrderInfo if found, None otherwise

    Raises:
        ValueError: If reference number is empty
        Exception: If API call fails
    """
    services = get_services(context)
    po = await services.purchase_orders.get_by_reference(request.reference_number)

    if not po:
        return None

    # Build PurchaseOrderInfo from response
    # Calculate total cost from line items
    total_cost = None
    if po.purchase_order_line_items:
        total_cost = sum(
            (item.unit_price or 0.0) * item.quantity
            for item in po.purchase_order_line_items
        )

    return PurchaseOrderInfo(
        reference_number=po.reference_number or "",
        supplier_code=po.supplier.supplier_code if po.supplier else None,
        supplier_name=po.supplier.supplier_name if po.supplier else None,
        status=str(po.status) if po.status else None,
        total_cost=total_cost,
        line_items_count=(
            len(po.purchase_order_line_items) if po.purchase_order_line_items else 0
        ),
    )


@unpack_pydantic_params
async def get_purchase_order(
    request: Annotated[GetPurchaseOrderRequest, Unpack()], context: Context
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
        context: Server context with services

    Returns:
        ListPurchaseOrdersResponse with purchase orders

    Raises:
        Exception: If API call fails
    """
    services = get_services(context)
    pos = await services.purchase_orders.list_all()

    # Handle case where API returns single object instead of list
    if not isinstance(pos, list):
        pos = [pos] if pos else []

    # Build response
    po_infos = []
    for po in pos:
        # Calculate total cost from line items
        total_cost = None
        if po.purchase_order_line_items:
            total_cost = sum(
                (item.unit_price or 0.0) * item.quantity
                for item in po.purchase_order_line_items
            )

        po_infos.append(
            PurchaseOrderInfo(
                reference_number=po.reference_number or "",
                supplier_code=po.supplier.supplier_code if po.supplier else None,
                supplier_name=po.supplier.supplier_name if po.supplier else None,
                status=str(po.status) if po.status else None,
                total_cost=total_cost,
                line_items_count=(
                    len(po.purchase_order_line_items)
                    if po.purchase_order_line_items
                    else 0
                ),
            )
        )

    return ListPurchaseOrdersResponse(
        purchase_orders=po_infos,
        total_count=len(po_infos),
    )


@unpack_pydantic_params
async def list_purchase_orders(
    request: Annotated[ListPurchaseOrdersRequest, Unpack()], context: Context
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
# Tool 3: create_purchase_order
# ============================================================================


class LineItemRequest(BaseModel):
    """Line item for purchase order."""

    product_code: str = Field(..., description="Product code")
    quantity: float = Field(..., description="Quantity to order", gt=0)
    unit_price: float | None = Field(default=None, description="Unit price")


class CreatePurchaseOrderRequest(BaseModel):
    """Request model for creating a purchase order."""

    supplier_code: str = Field(..., description="Supplier code")
    supplier_name: str | None = Field(default=None, description="Supplier name")
    line_items: list[LineItemRequest] = Field(
        ..., description="Line items for the purchase order", min_length=1
    )
    order_date: datetime | None = Field(
        default=None,
        description="Order date (ISO format). Defaults to current date if not provided.",
    )
    location_code: str | None = Field(default=None, description="Location code")
    location_name: str | None = Field(default=None, description="Location name")
    reference_number: str | None = Field(
        default=None, description="Custom reference number"
    )
    client_reference_number: str | None = Field(
        default=None, description="Client reference number"
    )
    status: str | None = Field(
        default="Draft",
        description="Purchase order status (Draft, Approved, Sent, Received)",
    )


class CreatePurchaseOrderResponse(BaseModel):
    """Response for purchase order creation."""

    reference_number: str
    supplier_code: str | None
    supplier_name: str | None
    status: str | None
    total_cost: float | None
    line_items_count: int


async def _create_purchase_order_impl(
    request: CreatePurchaseOrderRequest, context: Context
) -> CreatePurchaseOrderResponse:
    """Implementation of create_purchase_order tool.

    Args:
        request: Request containing purchase order details
        context: Server context with services

    Returns:
        CreatePurchaseOrderResponse with created PO details

    Raises:
        Exception: If API call fails
    """
    services = get_services(context)

    # Convert line items from pydantic models to dicts for service layer
    line_items = [
        {
            "product_code": item.product_code,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        for item in request.line_items
    ]

    # Create purchase order via service
    created_po = await services.purchase_orders.create(
        supplier_code=request.supplier_code,
        line_items=line_items,
        supplier_name=request.supplier_name,
        order_date=request.order_date,
        location_code=request.location_code,
        location_name=request.location_name,
        reference_number=request.reference_number,
        client_reference_number=request.client_reference_number,
        status=request.status,
    )

    # Build response
    # Calculate total cost from line items
    total_cost = None
    if created_po.purchase_order_line_items:
        total_cost = sum(
            (item.unit_price or 0.0) * item.quantity
            for item in created_po.purchase_order_line_items
        )

    return CreatePurchaseOrderResponse(
        reference_number=created_po.reference_number or "",
        supplier_code=(
            created_po.supplier.supplier_code if created_po.supplier else None
        ),
        supplier_name=(
            created_po.supplier.supplier_name if created_po.supplier else None
        ),
        status=str(created_po.status) if created_po.status else None,
        total_cost=total_cost,
        line_items_count=(
            len(created_po.purchase_order_line_items)
            if created_po.purchase_order_line_items
            else 0
        ),
    )


@unpack_pydantic_params
async def create_purchase_order(
    request: Annotated[CreatePurchaseOrderRequest, Unpack()], context: Context
) -> CreatePurchaseOrderResponse:
    """Create a new purchase order.

    This tool creates a new purchase order in StockTrim.

    Args:
        request: Request containing purchase order details
        context: Server context with StockTrimClient

    Returns:
        CreatePurchaseOrderResponse with created PO details

    Example:
        Request: {
            "supplier_code": "SUP-001",
            "supplier_name": "Acme Supplies",
            "line_items": [
                {"product_code": "WIDGET-001", "quantity": 100, "unit_price": 15.50}
            ],
            "status": "Draft"
        }
        Returns: {
            "reference_number": "PO-2024-001",
            "supplier_code": "SUP-001",
            "status": "Draft",
            "total_cost": 1550.0,
            "line_items_count": 1,
            "message": "Purchase order PO-2024-001 created successfully"
        }
    """
    return await _create_purchase_order_impl(request, context)


# ============================================================================
# Tool 4: delete_purchase_order
# ============================================================================


class DeletePurchaseOrderRequest(BaseModel):
    """Request model for deleting a purchase order."""

    reference_number: str = Field(..., description="Reference number to delete")


class DeletePurchaseOrderResponse(BaseModel):
    """Response for purchase order deletion."""

    success: bool
    message: str


@unpack_pydantic_params
async def delete_purchase_order(
    request: Annotated[DeletePurchaseOrderRequest, Unpack()], context: Context
) -> DeletePurchaseOrderResponse:
    """Delete a purchase order by reference number.

    🔴 HIGH-RISK OPERATION: This action permanently deletes purchase order data
    and cannot be undone. User confirmation is required via elicitation.

    This tool deletes a purchase order from StockTrim after obtaining
    explicit user confirmation through the MCP elicitation protocol.

    Args:
        request: Request containing reference number
        context: Server context with StockTrimClient

    Returns:
        DeletePurchaseOrderResponse indicating success or cancellation

    Example:
        Request: {"reference_number": "PO-2024-001"}
        Returns: {"success": true, "message": "Purchase order PO-2024-001 deleted successfully"}
                 or {"success": false, "message": "Deletion cancelled by user"}
    """
    services = get_services(context)

    # Get PO details for preview
    po_info = await _get_purchase_order_impl(
        GetPurchaseOrderRequest(reference_number=request.reference_number), context
    )

    if not po_info:
        return DeletePurchaseOrderResponse(
            success=False,
            message=f"Purchase order not found: {request.reference_number}",
        )

    # Build preview information
    supplier_info = (
        f"{po_info.supplier_name} ({po_info.supplier_code})"
        if po_info.supplier_name and po_info.supplier_code
        else po_info.supplier_code or "Unknown Supplier"
    )
    cost_info = f"${po_info.total_cost:,.2f}" if po_info.total_cost else "Unknown"
    items_info = (
        f"{po_info.line_items_count} items" if po_info.line_items_count else "0 items"
    )
    status_info = po_info.status or "Unknown"

    # Request user confirmation via elicitation
    result = await context.elicit(
        message=f"""⚠️ Delete purchase order {po_info.reference_number}?

**Supplier**: {supplier_info}
**Status**: {status_info}
**Total Cost**: {cost_info}
**Line Items**: {items_info}

This action will permanently delete the purchase order and cannot be undone.

Proceed with deletion?""",
        response_type=None,  # Simple yes/no approval
    )

    # Handle elicitation response
    match result:
        case AcceptedElicitation():
            # User confirmed - proceed with deletion
            success, message = await services.purchase_orders.delete(
                request.reference_number
            )
            return DeletePurchaseOrderResponse(
                success=success,
                message=f"✅ {message}" if success else message,
            )

        case DeclinedElicitation():
            # User declined
            return DeletePurchaseOrderResponse(
                success=False,
                message=f"❌ Deletion of purchase order {po_info.reference_number} declined by user",
            )

        case CancelledElicitation():
            # User cancelled
            return DeletePurchaseOrderResponse(
                success=False,
                message=f"❌ Deletion of purchase order {po_info.reference_number} cancelled by user",
            )

        case _:
            # Unexpected response type
            return DeletePurchaseOrderResponse(
                success=False,
                message=f"Unexpected elicitation response for purchase order {po_info.reference_number}",
            )


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
    mcp.tool()(create_purchase_order)
    mcp.tool()(delete_purchase_order)
