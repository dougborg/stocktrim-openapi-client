"""Customer management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

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


async def _get_customer_impl(
    request: GetCustomerRequest, context: Context
) -> CustomerInfo | None:
    """Implementation of get_customer tool.

    Args:
        request: Request containing customer code
        context: Server context with StockTrimClient

    Returns:
        CustomerInfo if found, None otherwise

    Raises:
        ValueError: If customer code is empty or invalid
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Customer code cannot be empty")

    logger.info(f"Getting customer: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the get method
        customer = await client.customers.get(request.code)

        if not customer:
            logger.warning(f"Customer not found: {request.code}")
            return None

        # Build CustomerInfo from response
        customer_info = CustomerInfo(
            code=customer.code or "",
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
        )

        logger.info(f"Customer retrieved: {request.code}")
        return customer_info

    except Exception as e:
        logger.error(f"Failed to get customer {request.code}: {e}")
        # Return None instead of raising for not found errors
        if "404" in str(e) or "not found" in str(e).lower():
            logger.warning(f"Customer not found: {request.code}")
            return None
        raise


async def get_customer(
    request: GetCustomerRequest, context: Context
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
    return await _get_customer_impl(request, context)


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


async def _list_customers_impl(
    request: ListCustomersRequest, context: Context
) -> ListCustomersResponse:
    """Implementation of list_customers tool.

    Args:
        request: Request with limit
        context: Server context with StockTrimClient

    Returns:
        ListCustomersResponse with customers

    Raises:
        Exception: If API call fails
    """
    logger.info(f"Listing customers (limit: {request.limit})")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use get_all method
        customers = await client.customers.get_all()

        # Build response (limit results)
        customer_infos = [
            CustomerInfo(
                code=c.code or "",
                name=c.name,
                email=c.email,
                phone=c.phone,
                address=c.address,
            )
            for c in customers[: request.limit]
        ]

        response = ListCustomersResponse(
            customers=customer_infos,
            total_count=len(customer_infos),
        )

        logger.info(f"Listed {response.total_count} customers")
        return response

    except Exception as e:
        logger.error(f"Failed to list customers: {e}")
        raise


async def list_customers(
    request: ListCustomersRequest, context: Context
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
    return await _list_customers_impl(request, context)


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
