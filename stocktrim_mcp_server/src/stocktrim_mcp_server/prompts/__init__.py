"""MCP Prompts for StockTrim MCP Server.

This module provides workflow prompts that guide AI agents through
complex multi-step inventory management tasks.
"""

from fastmcp import FastMCP

from stocktrim_mcp_server.prompts.workflows import register_workflow_prompts


def register_all_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts with the server.

    Args:
        mcp: FastMCP server instance
    """
    register_workflow_prompts(mcp)


__all__ = ["register_all_prompts"]
