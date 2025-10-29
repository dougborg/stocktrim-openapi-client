"""MCP tools for StockTrim Inventory Management.

This module contains tool implementations that provide actions with side effects
for interacting with the StockTrim API.

Tool Registration Pattern:
--------------------------
Each tool module exports a register_tools(mcp) function that registers its tools
with the FastMCP instance. This avoids circular imports.

When adding new tool modules:
1. Create the new module (e.g., products.py)
2. Define tools as regular async functions (no decorators)
3. Add a register_tools(mcp: FastMCP) function that calls mcp.tool() on each function
4. Import and call the registration function from this file
"""

from fastmcp import FastMCP

from .customers import register_tools as register_customer_tools
from .inventory import register_tools as register_inventory_tools
from .products import register_tools as register_product_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register all tools from all modules.

    Args:
        mcp: FastMCP server instance to register tools with
    """
    register_product_tools(mcp)
    register_customer_tools(mcp)
    register_inventory_tools(mcp)


__all__ = [
    "register_all_tools",
]
