"""Foundation tools for StockTrim MCP Server.

Foundation tools provide low-level, granular operations that map closely to the
StockTrim API. These are the building blocks used by higher-level workflow tools.

Tool Registration Pattern:
--------------------------
Each tool module exports a register_tools(mcp) function that registers its tools
with the FastMCP instance.
"""

from fastmcp import FastMCP

from .customers import register_tools as register_customer_tools
from .inventory import register_tools as register_inventory_tools
from .locations import register_tools as register_location_tools
from .products import register_tools as register_product_tools
from .purchase_orders import register_tools as register_purchase_order_tools
from .sales_orders import register_tools as register_sales_order_tools
from .suppliers import register_tools as register_supplier_tools


def register_all_foundation_tools(mcp: FastMCP) -> None:
    """Register all foundation tools from all modules.

    Args:
        mcp: FastMCP server instance to register tools with
    """
    register_product_tools(mcp)
    register_customer_tools(mcp)
    register_inventory_tools(mcp)
    register_supplier_tools(mcp)
    register_location_tools(mcp)
    register_purchase_order_tools(mcp)
    register_sales_order_tools(mcp)


__all__ = [
    "register_all_foundation_tools",
]
