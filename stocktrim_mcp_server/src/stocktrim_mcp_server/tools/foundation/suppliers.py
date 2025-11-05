"""Supplier management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services

logger = logging.getLogger(__name__)

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


async def get_supplier(
    request: GetSupplierRequest, context: Context
) -> SupplierInfo | None:
    """Get a supplier by code.

    This tool retrieves detailed information about a specific supplier
    from StockTrim.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        SupplierInfo if found, None if not found

    Example:
        Request: {"code": "SUP-001"}
        Returns: {"code": "SUP-001", "name": "Acme Supplies", ...}
    """
    services = get_services(context)
    supplier = await services.suppliers.get_by_code(request.code)

    if not supplier:
        return None

    # Build SupplierInfo from response
    return SupplierInfo(
        code=supplier.supplier_code,
        name=supplier.supplier_name,
        email=supplier.email_address,
        primary_contact=supplier.primary_contact_name,
    )


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


async def list_suppliers(
    request: ListSuppliersRequest, context: Context
) -> ListSuppliersResponse:
    """List all suppliers.

    This tool retrieves all suppliers from StockTrim,
    optionally filtered by active status.

    Args:
        request: Request with filter options
        context: Server context with StockTrimClient

    Returns:
        ListSuppliersResponse with suppliers

    Example:
        Request: {"active_only": true}
        Returns: {"suppliers": [...], "total_count": 10}
    """
    services = get_services(context)
    suppliers = await services.suppliers.list_suppliers(request.active_only)

    # Build response
    supplier_infos = [
        SupplierInfo(
            code=s.supplier_code,
            name=s.supplier_name,
            email=s.email_address,
            primary_contact=s.primary_contact_name,
        )
        for s in suppliers
    ]

    return ListSuppliersResponse(
        suppliers=supplier_infos,
        total_count=len(supplier_infos),
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


async def create_supplier(
    request: CreateSupplierRequest, context: Context
) -> SupplierInfo:
    """Create a new supplier.

    This tool creates a new supplier in StockTrim.

    Args:
        request: Request containing supplier details
        context: Server context with StockTrimClient

    Returns:
        SupplierInfo for the created supplier

    Example:
        Request: {"code": "SUP-001", "name": "Acme Supplies", "email": "contact@acme.com"}
        Returns: {"code": "SUP-001", "name": "Acme Supplies", ...}
    """
    services = get_services(context)
    created_supplier = await services.suppliers.create(
        code=request.code,
        name=request.name,
        email=request.email,
        primary_contact=request.primary_contact,
    )

    # Build SupplierInfo from response
    return SupplierInfo(
        code=created_supplier.supplier_code,
        name=created_supplier.supplier_name,
        email=created_supplier.email_address,
        primary_contact=created_supplier.primary_contact_name,
    )


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


async def delete_supplier(
    request: DeleteSupplierRequest, context: Context
) -> DeleteSupplierResponse:
    """Delete a supplier by code.

    This tool deletes a supplier from StockTrim.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        DeleteSupplierResponse indicating success

    Example:
        Request: {"code": "SUP-001"}
        Returns: {"success": true, "message": "Supplier SUP-001 deleted successfully"}
    """
    services = get_services(context)
    success, message = await services.suppliers.delete(request.code)

    return DeleteSupplierResponse(
        success=success,
        message=message,
    )


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
