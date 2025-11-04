"""Server context for StockTrim MCP Server."""

from __future__ import annotations

from stocktrim_mcp_server.services.products import ProductService
from stocktrim_public_api_client import StockTrimClient


class ServerContext:
    """Context object that holds the StockTrimClient and service layer for the server lifespan."""

    def __init__(self, client: StockTrimClient):
        """Initialize server context with StockTrimClient and services.

        Args:
            client: Initialized StockTrimClient instance
        """
        self.client = client

        # Service layer
        self.products = ProductService(client)
