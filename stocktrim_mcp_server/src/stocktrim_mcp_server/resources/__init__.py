"""MCP Resources for StockTrim MCP Server.

This module provides read-only resources that AI agents can explore
without making tool calls. Resources provide context and enable discovery.

Resources are organized into:
- Foundation: Core entity resources (products, customers, suppliers, etc.)
- Reports: Aggregated data resources (inventory status, urgent orders, etc.)
"""

from fastmcp import FastMCP

from stocktrim_mcp_server.resources.foundation import register_foundation_resources
from stocktrim_mcp_server.resources.reports import register_report_resources


def register_all_resources(mcp: FastMCP) -> None:
    """Register all MCP resources with the server.

    Args:
        mcp: FastMCP server instance
    """
    register_foundation_resources(mcp)
    register_report_resources(mcp)


__all__ = ["register_all_resources"]
