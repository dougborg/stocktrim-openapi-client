"""Supplier management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

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
    phone: str | None
    is_active: bool


async def _get_supplier_impl(
    request: GetSupplierRequest, context: Context
) -> SupplierInfo | None:
    """Implementation of get_supplier tool.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        SupplierInfo if found, None otherwise

    Raises:
        ValueError: If supplier code is empty or invalid
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Supplier code cannot be empty")

    logger.info(f"Getting supplier: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the find_by_code convenience method
        supplier = await client.suppliers.find_by_code(request.code)

        if not supplier:
            logger.warning(f"Supplier not found: {request.code}")
            return None

        # Build SupplierInfo from response
        supplier_info = SupplierInfo(
            code=supplier.code or "",
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            is_active=supplier.is_active or False,
        )

        logger.info(f"Supplier retrieved: {request.code}")
        return supplier_info

    except Exception as e:
        logger.error(f"Failed to get supplier {request.code}: {e}")
        raise


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
    return await _get_supplier_impl(request, context)


# ============================================================================
# Tool 2: list_suppliers
# ============================================================================


class ListSuppliersRequest(BaseModel):
    """Request model for listing suppliers."""

    active_only: bool = Field(
        default=True, description="Only return active suppliers (default: true)"
    )


class ListSuppliersResponse(BaseModel):
    """Response containing suppliers."""

    suppliers: list[SupplierInfo]
    total_count: int


async def _list_suppliers_impl(
    request: ListSuppliersRequest, context: Context
) -> ListSuppliersResponse:
    """Implementation of list_suppliers tool.

    Args:
        request: Request with filter options
        context: Server context with StockTrimClient

    Returns:
        ListSuppliersResponse with suppliers

    Raises:
        Exception: If API call fails
    """
    logger.info(f"Listing suppliers (active_only={request.active_only})")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Get all suppliers
        suppliers = await client.suppliers.get_all()

        # Filter by active status if requested
        if request.active_only:
            suppliers = [s for s in suppliers if s.is_active]

        # Build response
        supplier_infos = [
            SupplierInfo(
                code=s.code or "",
                name=s.name,
                email=s.email,
                phone=s.phone,
                is_active=s.is_active or False,
            )
            for s in suppliers
        ]

        response = ListSuppliersResponse(
            suppliers=supplier_infos,
            total_count=len(supplier_infos),
        )

        logger.info(f"Found {response.total_count} suppliers")
        return response

    except Exception as e:
        logger.error(f"Failed to list suppliers: {e}")
        raise


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
    return await _list_suppliers_impl(request, context)


# ============================================================================
# Tool 3: create_supplier
# ============================================================================


class CreateSupplierRequest(BaseModel):
    """Request model for creating a supplier."""

    code: str = Field(..., description="Unique supplier code")
    name: str = Field(..., description="Supplier name")
    email: str | None = Field(default=None, description="Supplier email")
    phone: str | None = Field(default=None, description="Supplier phone")
    is_active: bool = Field(default=True, description="Whether supplier is active")


async def _create_supplier_impl(
    request: CreateSupplierRequest, context: Context
) -> SupplierInfo:
    """Implementation of create_supplier tool.

    Args:
        request: Request containing supplier details
        context: Server context with StockTrimClient

    Returns:
        SupplierInfo for the created supplier

    Raises:
        ValueError: If required fields are missing
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Supplier code cannot be empty")
    if not request.name or not request.name.strip():
        raise ValueError("Supplier name cannot be empty")

    logger.info(f"Creating supplier: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Import SupplierRequestDto from generated models
        from stocktrim_public_api_client.generated.models import SupplierRequestDto

        # Create supplier DTO
        supplier_dto = SupplierRequestDto(
            supplier_code=request.code,
            supplier_name=request.name,
            email_address=request.email,
        )

        # Create supplier using create_one method
        created_supplier = await client.suppliers.create_one(supplier_dto)

        # Build SupplierInfo from response
        supplier_info = SupplierInfo(
            code=created_supplier.code or "",
            name=created_supplier.name,
            email=created_supplier.email,
            phone=created_supplier.phone,
            is_active=created_supplier.is_active or False,
        )

        logger.info(f"Supplier created: {request.code}")
        return supplier_info

    except Exception as e:
        logger.error(f"Failed to create supplier {request.code}: {e}")
        raise


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
    return await _create_supplier_impl(request, context)


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
    """Implementation of delete_supplier tool.

    Args:
        request: Request containing supplier code
        context: Server context with StockTrimClient

    Returns:
        DeleteSupplierResponse indicating success

    Raises:
        ValueError: If supplier code is empty
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Supplier code cannot be empty")

    logger.info(f"Deleting supplier: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Check if supplier exists first
        supplier = await client.suppliers.find_by_code(request.code)
        if not supplier:
            return DeleteSupplierResponse(
                success=False,
                message=f"Supplier {request.code} not found",
            )

        # Delete supplier
        await client.suppliers.delete(request.code)

        logger.info(f"Supplier deleted: {request.code}")
        return DeleteSupplierResponse(
            success=True,
            message=f"Supplier {request.code} deleted successfully",
        )

    except Exception as e:
        logger.error(f"Failed to delete supplier {request.code}: {e}")
        raise


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
    return await _delete_supplier_impl(request, context)


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
