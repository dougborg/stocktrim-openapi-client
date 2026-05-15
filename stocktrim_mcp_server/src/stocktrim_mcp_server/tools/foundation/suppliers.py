"""Supplier management tools for StockTrim MCP Server."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

logger = get_logger(__name__)

# ============================================================================
# Tool 1: get_supplier
# ============================================================================


class GetSupplierRequest(BaseModel):
    """Request model for getting a supplier."""

    code: str = Field(..., description="Supplier code to retrieve")


class SupplierInfo(BaseModel):
    """Supplier information."""

    code: str
    name: str | None
    email: str | None
    primary_contact: str | None


class GetSupplierResponse(BaseModel):
    """Response wrapper so the typed payload round-trips through
    ``unwrap_tool_result`` regardless of whether the inner field is None."""

    supplier: SupplierInfo | None = None


class CreateSupplierResponse(BaseModel):
    """Response wrapper so the typed payload round-trips through
    ``unwrap_tool_result``."""

    supplier: SupplierInfo


@unpack_pydantic_params
async def get_supplier(
    request: Annotated[GetSupplierRequest, Unpack()], context: Context
) -> ToolResult:
    """Get a supplier by code.

    This tool retrieves detailed information about a specific supplier
    from StockTrim.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, GetSupplierResponse)`` and read
        ``response.supplier`` (``None`` if not found).
    """
    services = get_services(context)
    supplier = await services.suppliers.get_by_code(request.code)

    info = (
        SupplierInfo(
            code=supplier.supplier_code,
            name=supplier.supplier_name,
            email=supplier.email_address,
            primary_contact=supplier.primary_contact_name,
        )
        if supplier
        else None
    )
    return make_json_result(GetSupplierResponse(supplier=info))


# ============================================================================
# Tool 2: list_suppliers
# ============================================================================


class ListSuppliersRequest(BaseModel):
    """Request model for listing suppliers."""

    active_only: bool = Field(
        default=False, description="Only return active suppliers (default: false)"
    )


class ListSuppliersResponse(BaseModel):
    """Response containing suppliers."""

    suppliers: list[SupplierInfo]
    total_count: int


@unpack_pydantic_params
async def list_suppliers(
    request: Annotated[ListSuppliersRequest, Unpack()], context: Context
) -> ToolResult:
    """List all suppliers.

    This tool retrieves all suppliers from StockTrim,
    optionally filtered by active status.

    Args:
        request: Request with filter options
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ListSuppliersResponse)``.
    """
    services = get_services(context)
    suppliers = await services.suppliers.list_all(request.active_only)

    supplier_infos = [
        SupplierInfo(
            code=s.supplier_code,
            name=s.supplier_name,
            email=s.email_address,
            primary_contact=s.primary_contact_name,
        )
        for s in suppliers
    ]
    return make_json_result(
        ListSuppliersResponse(
            suppliers=supplier_infos,
            total_count=len(supplier_infos),
        )
    )


# ============================================================================
# Tool 3: create_supplier
# ============================================================================


class CreateSupplierRequest(BaseModel):
    """Request model for creating a supplier."""

    code: str = Field(..., description="Unique supplier code")
    name: str = Field(..., description="Supplier name")
    email: str | None = Field(default=None, description="Supplier email")
    primary_contact: str | None = Field(
        default=None, description="Primary contact name"
    )


@unpack_pydantic_params
async def create_supplier(
    request: Annotated[CreateSupplierRequest, Unpack()], context: Context
) -> ToolResult:
    """Create a new supplier.

    This tool creates a new supplier in StockTrim.

    Args:
        request: Request containing supplier details
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, CreateSupplierResponse)`` and read
        ``response.supplier``.
    """
    services = get_services(context)
    created_supplier = await services.suppliers.create(
        code=request.code,
        name=request.name,
        email=request.email,
        primary_contact=request.primary_contact,
    )

    info = SupplierInfo(
        code=created_supplier.supplier_code,
        name=created_supplier.supplier_name,
        email=created_supplier.email_address,
        primary_contact=created_supplier.primary_contact_name,
    )
    return make_json_result(CreateSupplierResponse(supplier=info))


# ============================================================================
# Tool 4: delete_supplier
# ============================================================================


class DeleteSupplierRequest(BaseModel):
    """Request model for deleting a supplier."""

    code: str = Field(..., description="Supplier code to delete")


class DeleteSupplierResponse(BaseModel):
    """Response for supplier deletion."""

    success: bool
    message: str


async def _delete_supplier_impl(
    request: DeleteSupplierRequest, context: Context
) -> DeleteSupplierResponse:
    """Pure-impl half of ``delete_supplier`` so the ToolResult wrapper stays one line."""
    services = get_services(context)
    supplier = await services.suppliers.get_by_code(request.code)

    if not supplier:
        return DeleteSupplierResponse(
            success=False,
            message=f"Supplier not found: {request.code}",
        )

    supplier_code = supplier.supplier_code or request.code
    supplier_name = supplier.supplier_name or "Unnamed Supplier"
    contact_info = (
        supplier.primary_contact_name or supplier.email_address or "No contact"
    )

    result = await context.elicit(
        message=f"""⚠️ Delete supplier {supplier_code}?

**{supplier_name}**
Contact: {contact_info}

This action will permanently delete the supplier and all associations (product mappings, purchase order history).
This cannot be undone.

Proceed with deletion?""",
        response_type=None,
    )

    match result:
        case AcceptedElicitation():
            success, message = await services.suppliers.delete(request.code)
            return DeleteSupplierResponse(
                success=success,
                message=f"✅ {message}" if success else message,
            )
        case DeclinedElicitation():
            return DeleteSupplierResponse(
                success=False,
                message=f"❌ Deletion of supplier {supplier_code} declined by user",
            )
        case CancelledElicitation():
            return DeleteSupplierResponse(
                success=False,
                message=f"❌ Deletion of supplier {supplier_code} cancelled by user",
            )
        case _:
            return DeleteSupplierResponse(
                success=False,
                message=f"Unexpected elicitation response for supplier {supplier_code}",
            )


@unpack_pydantic_params
async def delete_supplier(
    request: Annotated[DeleteSupplierRequest, Unpack()], context: Context
) -> ToolResult:
    """Delete a supplier by code.

    🔴 HIGH-RISK OPERATION: This action permanently deletes supplier data
    and cannot be undone. User confirmation is required via elicitation.

    This tool deletes a supplier from StockTrim after obtaining
    explicit user confirmation through the MCP elicitation protocol.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, DeleteSupplierResponse)``.
    """
    response = await _delete_supplier_impl(request, context)
    return make_json_result(response)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register supplier tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(get_supplier)
    mcp.tool()(list_suppliers)
    mcp.tool()(create_supplier)
    mcp.tool()(delete_supplier)
