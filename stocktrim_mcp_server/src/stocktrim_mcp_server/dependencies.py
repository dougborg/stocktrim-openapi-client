"""Dependency injection helpers for MCP tools."""

from __future__ import annotations

from fastmcp import Context

from stocktrim_mcp_server.context import ServerContext


def get_services(context: Context) -> ServerContext:
    """Extract ServerContext from FastMCP context.

    This helper function provides a clean way to access the service layer
    from MCP tool functions.

    Args:
        context: FastMCP context from tool invocation

    Returns:
        ServerContext with initialized services

    Example:
        async def get_product(request: GetProductRequest, context: Context) -> ProductInfo:
            services = get_services(context)
            return await services.products.get_by_code(request.code)
    """
    return context.request_context.lifespan_context
