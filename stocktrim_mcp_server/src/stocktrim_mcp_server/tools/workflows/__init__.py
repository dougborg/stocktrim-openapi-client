"""Workflow tools for StockTrim MCP Server.

Workflow tools provide high-level, intent-based operations that combine multiple
foundation operations into cohesive workflows. These tools are designed to handle
common business scenarios efficiently.

Tool Registration Pattern:
--------------------------
Each tool module exports a register_tools(mcp) function that registers its tools
with the FastMCP instance.
"""

from fastmcp import FastMCP

from .forecast_management import register_tools as register_forecast_management_tools
from .product_management import register_tools as register_product_management_tools
from .supplier_onboarding import register_tools as register_supplier_onboarding_tools
from .urgent_orders import register_tools as register_urgent_order_tools


def register_all_workflow_tools(mcp: FastMCP) -> None:
    """Register all workflow tools from all modules.

    Args:
        mcp: FastMCP server instance to register tools with
    """
    register_urgent_order_tools(mcp)
    register_product_management_tools(mcp)
    register_forecast_management_tools(mcp)
    register_supplier_onboarding_tools(mcp)


__all__ = [
    "register_all_workflow_tools",
]
