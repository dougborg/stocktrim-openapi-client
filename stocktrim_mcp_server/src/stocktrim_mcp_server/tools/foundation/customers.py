"""Customer management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
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


class GetCustomerResponse(BaseModel):
    """Response wrapper for ``get_customer`` so the ``None`` case still
    serializes through ``make_json_result``."""

    customer: CustomerInfo | None = None


@unpack_pydantic_params
async def get_customer(
    request: Annotated[GetCustomerRequest, Unpack()], context: Context
) -> ToolResult:
    """Get a customer by code.

    This tool retrieves detailed information about a specific customer
    from StockTrim.

    Args:
        request: Request containing customer code
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, GetCustomerResponse)`` and read
        ``response.customer`` (``None`` if not found).
    """
    services = get_services(context)
    customer = await services.customers.get_by_code(request.code)

    customer_info = (
        CustomerInfo(
            code=customer.code or "",
            name=customer.name,
            email=customer.email_address,
            phone=customer.phone,
            address=customer.street_address,
        )
        if customer
        else None
    )
    return make_json_result(GetCustomerResponse(customer=customer_info))


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
) -> ToolResult:
    """List all customers.

    This tool retrieves a list of all customers from StockTrim.
    Results are limited by the limit parameter.

    Args:
        request: Request with limit
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ListCustomersResponse)`` to recover
        the typed payload.
    """
    services = get_services(context)
    customers = await services.customers.list_all(limit=request.limit)

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

    return make_json_result(
        ListCustomersResponse(
            customers=customer_infos,
            total_count=len(customer_infos),
        )
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
