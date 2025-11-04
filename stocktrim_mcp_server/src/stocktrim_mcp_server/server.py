"""StockTrim MCP Server - FastMCP server with environment-based authentication.

This module implements the core MCP server for StockTrim Inventory Management,
providing tools for interacting with products, customers, suppliers, orders, and inventory.

Features:
- Environment-based authentication (STOCKTRIM_API_AUTH_ID, STOCKTRIM_API_AUTH_SIGNATURE)
- Automatic client initialization with error handling
- Lifespan management for StockTrimClient context
- Production-ready with transport-layer resilience
"""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from stocktrim_mcp_server import __version__
from stocktrim_mcp_server.context import ServerContext
from stocktrim_public_api_client import StockTrimClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[ServerContext]:
    """Manage server lifespan and StockTrimClient lifecycle.

    This context manager:
    1. Loads environment variables from .env file
    2. Validates required configuration (auth credentials)
    3. Initializes StockTrimClient with error handling
    4. Provides client to tools via ServerContext
    5. Ensures proper cleanup on shutdown

    Args:
        server: FastMCP server instance

    Yields:
        ServerContext: Context object containing initialized StockTrimClient

    Raises:
        ValueError: If required environment variables are not set
        Exception: If StockTrimClient initialization fails
    """
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    api_auth_id = os.getenv("STOCKTRIM_API_AUTH_ID")
    api_auth_signature = os.getenv("STOCKTRIM_API_AUTH_SIGNATURE")
    base_url = os.getenv("STOCKTRIM_BASE_URL", "https://api.stocktrim.com")

    # Validate required configuration
    if not api_auth_id:
        logger.error(
            "STOCKTRIM_API_AUTH_ID environment variable is required. "
            "Please set it in your .env file or environment."
        )
        raise ValueError(
            "STOCKTRIM_API_AUTH_ID environment variable is required for authentication"
        )

    if not api_auth_signature:
        logger.error(
            "STOCKTRIM_API_AUTH_SIGNATURE environment variable is required. "
            "Please set it in your .env file or environment."
        )
        raise ValueError(
            "STOCKTRIM_API_AUTH_SIGNATURE environment variable is required for authentication"
        )

    logger.info("Initializing StockTrim MCP Server...")
    logger.info(f"API Base URL: {base_url}")

    try:
        # Initialize StockTrimClient with automatic resilience features
        async with StockTrimClient(
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
            base_url=base_url,
            timeout=30.0,
            max_retries=5,
        ) as client:
            logger.info("StockTrimClient initialized successfully")

            # Create context with client for tools to access
            # Note: client is StockTrimClient but mypy sees it as AuthenticatedClient
            context = ServerContext(client=client)  # type: ignore[arg-type]

            # Yield context to server - tools can access via lifespan dependency
            logger.info("StockTrim MCP Server ready")
            yield context

    except ValueError as e:
        # Authentication or configuration errors
        logger.error(f"Authentication error: {e}")
        raise
    except Exception as e:
        # Unexpected errors during initialization
        logger.error(f"Failed to initialize StockTrimClient: {e}")
        raise
    finally:
        logger.info("StockTrim MCP Server shutting down...")


# Initialize FastMCP server with lifespan management
mcp = FastMCP(
    name="stocktrim-inventory",
    version=__version__,
    lifespan=lifespan,
    instructions="""
    StockTrim MCP Server provides tools for interacting with StockTrim Inventory Management.

    Available capabilities:
    - Product management (search, get, create, delete)
    - Customer management (get, list, ensure exists)
    - Supplier management (get, create, delete)
    - Order management (sales and purchase orders)
    - Inventory management (check levels, set stock)

    All tools require STOCKTRIM_API_AUTH_ID and STOCKTRIM_API_AUTH_SIGNATURE
    environment variables to be set.
    """,
)

# Register all tools, resources, and prompts with the mcp instance
# This must come after mcp initialization
from stocktrim_mcp_server.tools import register_all_tools  # noqa: E402

register_all_tools(mcp)


def main(**kwargs: Any) -> None:
    """Main entry point for the StockTrim MCP Server.

    This function is called when running the server via:
    - uvx stocktrim-mcp-server
    - python -m stocktrim_mcp_server
    - stocktrim-mcp-server (console script)

    Args:
        **kwargs: Additional arguments passed to mcp.run()
    """
    logger.info("Starting StockTrim MCP Server...")
    mcp.run(**kwargs)


if __name__ == "__main__":
    main()
