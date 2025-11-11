"""Customer management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: get_customer
# ============================================================================


class GetCustomerRequest(BaseModel):
    """Request model for getting a customer."""

    code: str = Field(..., description="Customer code to retrieve")


class CustomerInfo(BaseModel):
    """Customer information."""

    code: str
    name: str | None
    email: str | None
    phone: str | None
    address: str | None


@unpack_pydantic_params
async def get_customer(
    request: Annotated[GetCustomerRequest, Unpack()], context: Context
) -> CustomerInfo | None:
    """Get a customer by code.

    This tool retrieves detailed information about a specific customer
    from StockTrim.

    Args:
        request: Request containing customer code
        context: Server context with StockTrimClient

    Returns:
        CustomerInfo if found, None if not found

    Example:
        Request: {"code": "CUST-001"}
        Returns: {"code": "CUST-001", "name": "Customer Name", ...}
    """
    services = get_services(context)
    customer = await services.customers.get_by_code(request.code)

    if not customer:
        return None

    # Build CustomerInfo from response
    return CustomerInfo(
        code=customer.code or "",
        name=customer.name,
        email=customer.email_address,
        phone=customer.phone,
        address=customer.street_address,
    )


# ============================================================================
# Tool 2: list_customers
# ============================================================================


class ListCustomersRequest(BaseModel):
    """Request model for listing customers."""

    limit: int = Field(default=50, description="Maximum customers to return")


class ListCustomersResponse(BaseModel):
    """Response containing customers."""

    customers: list[CustomerInfo]
    total_count: int


@unpack_pydantic_params
async def list_customers(
    request: Annotated[ListCustomersRequest, Unpack()], context: Context
) -> ListCustomersResponse:
    """List all customers.

    This tool retrieves a list of all customers from StockTrim.
    Results are limited by the limit parameter.

    Args:
        request: Request with limit
        context: Server context with StockTrimClient

    Returns:
        ListCustomersResponse with customers

    Example:
        Request: {"limit": 50}
        Returns: {"customers": [...], "total_count": 50}
    """
    services = get_services(context)
    customers = await services.customers.list_all(limit=request.limit)

    # Build response
    customer_infos = [
        CustomerInfo(
            code=c.code or "",
            name=c.name,
            email=c.email_address,
            phone=c.phone,
            address=c.street_address,
        )
        for c in customers
    ]

    return ListCustomersResponse(
        customers=customer_infos,
        total_count=len(customer_infos),
    )


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register customer tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(get_customer)
    mcp.tool()(list_customers)
