"""MCP tools for StockTrim Inventory Management.

This module contains tool implementations that provide actions with side effects
for interacting with the StockTrim API.

Tool Organization:
------------------
- foundation/: Low-level, granular operations that map closely to API endpoints
- workflows/: High-level, intent-based tools that combine multiple operations (future)

Tool Registration Pattern:
--------------------------
Each tool module exports a register_tools(mcp) function that registers its tools
with the FastMCP instance. This avoids circular imports.

When adding new tool modules:
1. Create the new module in the appropriate directory
2. Define tools as regular async functions (no decorators)
3. Add a register_tools(mcp: FastMCP) function that calls mcp.tool() on each function
4. Import and call the registration function from this file
"""

from fastmcp import FastMCP

from .foundation import register_all_foundation_tools
from .workflows import register_all_workflow_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register all tools from all modules.

    Args:
        mcp: FastMCP server instance to register tools with
    """
    # Register foundation tools (low-level API operations)
    register_all_foundation_tools(mcp)

    # Register workflow tools (high-level intent-based operations)
    register_all_workflow_tools(mcp)


__all__ = [
    "register_all_tools",
]
