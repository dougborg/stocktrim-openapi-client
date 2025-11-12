"""Workflow prompts for StockTrim MCP Server.

This module provides guided multi-step workflow templates for common
inventory management tasks.
"""

from fastmcp import FastMCP

from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger(__name__)


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    # Individual prompts will be added here in follow-up PRs
    pass
