"""StockTrim MCP Server - FastMCP server with environment-based authentication.

This module implements the core MCP server for StockTrim Inventory Management,
providing tools for interacting with products, customers, suppliers, orders, and inventory.

Features:
- Environment-based authentication (STOCKTRIM_API_AUTH_ID, STOCKTRIM_API_AUTH_SIGNATURE)
- Automatic client initialization with error handling
- Lifespan management for StockTrimClient context
- Production-ready with transport-layer resilience
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from stocktrim_mcp_server import __version__
from stocktrim_mcp_server.context import ServerContext
from stocktrim_mcp_server.logging_config import configure_logging, get_logger
from stocktrim_public_api_client import StockTrimClient

# Configure structured logging (will be called in lifespan)
logger = get_logger(__name__)


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
            "missing_configuration",
            variable="STOCKTRIM_API_AUTH_ID",
            message="Environment variable is required. Please set it in your .env file or environment.",
        )
        raise ValueError(
            "STOCKTRIM_API_AUTH_ID environment variable is required for authentication"
        )

    if not api_auth_signature:
        logger.error(
            "missing_configuration",
            variable="STOCKTRIM_API_AUTH_SIGNATURE",
            message="Environment variable is required. Please set it in your .env file or environment.",
        )
        raise ValueError(
            "STOCKTRIM_API_AUTH_SIGNATURE environment variable is required for authentication"
        )

    logger.info("server_initializing", base_url=base_url)

    try:
        # Initialize StockTrimClient with automatic resilience features
        async with StockTrimClient(
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
            base_url=base_url,
            timeout=30.0,
            max_retries=5,
        ) as client:
            logger.info(
                "client_initialized", base_url=base_url, timeout=30.0, max_retries=5
            )

            # Create context with client for tools to access
            # Note: client is StockTrimClient but mypy sees it as AuthenticatedClient
            context = ServerContext(client=client)  # type: ignore[arg-type]

            # Yield context to server - tools can access via lifespan dependency
            logger.info("server_ready")
            yield context

    except ValueError as e:
        # Authentication or configuration errors
        logger.error("authentication_error", error=str(e), error_type=type(e).__name__)
        raise
    except Exception as e:
        # Unexpected errors during initialization
        logger.error(
            "initialization_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
    finally:
        logger.info("server_shutdown")


# Initialize FastMCP server with lifespan management
mcp = FastMCP(
    name="stocktrim-inventory",
    version=__version__,
    lifespan=lifespan,
    instructions="""
StockTrim MCP Server - Inventory Management for AI Assistants

## Overview

This server provides comprehensive tools for managing StockTrim inventory, including
products, customers, suppliers, purchase orders, sales orders, and stock levels.
The server includes both foundational CRUD tools and high-level workflow tools for
common inventory management tasks.

## Authentication

All API calls require environment variables:
- STOCKTRIM_API_AUTH_ID: Your StockTrim API authentication ID
- STOCKTRIM_API_AUTH_SIGNATURE: Your StockTrim API signature

Authentication is handled automatically by the server.

## Tool Categories

### Foundation Tools (Direct API Access)
Basic CRUD operations for direct data manipulation:

**Products**: get_product, search_products, list_products, create_products, delete_products
**Customers**: get_customer, list_customers, create_customers
**Suppliers**: get_supplier, list_suppliers, create_suppliers
**Inventory**: get_inventory, set_inventory
**Orders**: create_sales_order, get_sales_orders, delete_sales_orders,
           get_purchase_order, list_purchase_orders, create_purchase_order, delete_purchase_order
**Locations**: list_locations, create_location
**Planning**: run_order_plan, run_forecast
**BOM**: list_boms, create_bom

### Workflow Tools (High-Level Operations)
Intent-based tools that combine multiple operations:

**Forecast Management**:
- manage_forecast_group: Manage forecast groupings (API limitation note included)
- update_forecast_settings: Update product forecast parameters (lead time, safety stock, service level)
- forecasts_update_and_monitor: Trigger forecast recalculation with progress monitoring
- forecasts_get_for_products: Query forecast data with markdown reports

**Urgent Order Management**:
- review_urgent_order_requirements: Identify items approaching stockout, grouped by supplier
- generate_purchase_orders_from_urgent_items: Auto-generate draft POs from order plan

**Product Configuration**:
- configure_product: Update product settings (discontinue status, forecast configuration)

**Supplier Onboarding**:
- create_supplier_with_products: Onboard new supplier with product mappings in one operation

## Resources (Discovery & Context)

Resources provide read-only access to StockTrim data for AI agents to explore and gather context
without making tool calls. Resources are automatically available and can be browsed to understand
the data landscape before taking actions.

### Foundation Resources
Core entity resources for discovering and understanding StockTrim data:

- **stocktrim://products/{product_code}**: Detailed product information (pricing, inventory, suppliers)
- **stocktrim://products/catalog**: Browse product catalog (limited to 50 items)
- **stocktrim://customers/{customer_code}**: Customer details with contact information
- **stocktrim://suppliers/{supplier_code}**: Supplier information with lead times and contacts
- **stocktrim://locations/{location_code}**: Warehouse and location details
- **stocktrim://inventory/{location_code}/{product_code}**: Stock levels at specific locations

### Report Resources
Aggregated business intelligence reports:

- **stocktrim://reports/inventory-status?days_threshold=30**: Items approaching stockout
- **stocktrim://reports/urgent-orders**: Items needing immediate reorder (< 7 days)
- **stocktrim://reports/supplier-directory**: All suppliers with contact information

Resources complement tools by enabling discovery and context gathering before taking actions.
For example, browse the supplier directory resource before deciding which suppliers to include
in a purchase order workflow.

## Common Workflows

### 1. Inventory Reordering
**Goal**: Identify and reorder low-stock items

**Approach A - Automated (Recommended)**:
1. review_urgent_order_requirements(days_threshold=30) → Get items grouped by supplier
2. Review the suggested items and quantities
3. generate_purchase_orders_from_urgent_items(supplier_codes=[...]) → Create draft POs
4. Review draft POs in StockTrim UI before approving

**Approach B - Manual**:
1. list_products → Get all products
2. get_inventory → Check stock levels
3. For low-stock items: create_purchase_order with appropriate quantities

### 2. Forecast Management
**Goal**: Update forecasts and review predictions

**Steps**:
1. forecasts_update_and_monitor(wait_for_completion=True) → Trigger calculation
2. Wait for completion (tool monitors progress automatically)
3. forecasts_get_for_products(category="Widgets", max_results=20) → Review forecasts
4. For products with unexpected forecasts: update_forecast_settings to adjust parameters

### 3. New Supplier Onboarding
**Goal**: Add supplier and map their products

**Approach A - Workflow Tool**:
1. create_supplier_with_products({
     supplier_code: "SUP-NEW",
     supplier_name: "New Supplier Inc",
     product_mappings: [{product_code: "WIDGET-001", supplier_product_code: "SUP-SKU-001", cost_price: 15.50}]
   })

**Approach B - Step by Step**:
1. create_suppliers([{code: "SUP-NEW", name: "New Supplier Inc"}])
2. For each product: Update product with supplier mapping

### 4. Product Configuration
**Goal**: Discontinue product or adjust forecast settings

**Steps**:
1. configure_product({
     product_code: "WIDGET-001",
     discontinue: True,
     configure_forecast: False  # Disable forecasting for discontinued product
   })

### 5. Customer Order Fulfillment
**Goal**: Process customer order and update inventory

**Steps**:
1. get_customer("CUST-001") → Verify customer exists
2. get_product("WIDGET-001") → Verify product exists and get details
3. get_inventory → Check if sufficient stock available
4. If in stock: create_sales_order({...})
5. After order ships: set_inventory to deduct stock

## Best Practices

### When to Use Workflow Tools vs Foundation Tools

**Use Workflow Tools When**:
- You need to accomplish a business goal (reorder stock, onboard supplier, configure forecasts)
- You want to combine multiple operations atomically
- You need formatted reports or progress monitoring
- You're working with forecast data or urgent reordering

**Use Foundation Tools When**:
- You need direct CRUD access to specific entities
- You're building custom workflows not covered by workflow tools
- You need maximum flexibility and control
- You're integrating with external systems

### Error Handling Patterns

**None Returns**:
- get_product, get_customer, get_supplier return None when not found
- This is NOT an error - check for None before proceeding
- Example: `if product is None: # handle not found`

**Exceptions**:
- ValueError: Invalid input (empty codes, negative quantities)
- Exception: API failures, authentication errors, network issues
- Always wrap operations in try/catch for production use

**Validation**:
- Pydantic validates all inputs automatically
- Required fields will fail with clear error messages
- Type coercion happens automatically where safe

### Data Flow Patterns

**1. Verify Before Operate**:
```
product = get_product("WIDGET-001")
if product:
    set_inventory({product_id: product.id, quantity: 100})
else:
    # create product first
```

**2. Search Before Get**:
```
# When unsure of exact code
results = search_products("WIDG")
# Then get specific product
product = get_product(results[0].code)
```

**3. Workflow Tool Composition**:
```
# Update forecasts, then review urgent items
forecasts_update_and_monitor(wait_for_completion=True)
urgent_items = review_urgent_order_requirements(days_threshold=14)
# Review and generate POs for specific suppliers
generate_purchase_orders_from_urgent_items(supplier_codes=["SUP-001"])
```

## Observability

All tools are automatically instrumented with structured logging:
- Tool invocations logged with parameters
- Execution time tracked (duration_ms)
- Success/failure status recorded
- Errors logged with full context

Set `LOG_FORMAT=json` for machine-readable logs in production.
Set `LOG_LEVEL=DEBUG` to see service-layer operations.

## Rate Limiting & Performance

- List operations return limited results - check total_count in responses
- Batch operations (create_products, create_customers) are more efficient than loops
- Forecast calculations can take minutes - use forecasts_update_and_monitor for progress
- Order plan queries are cached - re-run forecasts if data seems stale

## Data Validation

All request models use Pydantic validation:
- Type safety enforced
- Required fields validated
- Ranges checked (e.g., quantity > 0)
- Date formats validated (ISO 8601)

See individual tool documentation for specific field requirements.

## Need Help?

- Tool Documentation: See docs/mcp-server/tools.md for detailed tool reference
- Logging Guide: See docs/mcp-server/logging.md for observability features
- Examples: See docs/mcp-server/examples.md for complete workflow examples
- Issues: Report bugs at https://github.com/dougborg/stocktrim-openapi-client/issues
    """,
)

# Register all tools, resources, and prompts with the mcp instance
# This must come after mcp initialization
from stocktrim_mcp_server.prompts import register_all_prompts  # noqa: E402
from stocktrim_mcp_server.resources import register_all_resources  # noqa: E402
from stocktrim_mcp_server.tools import register_all_tools  # noqa: E402

register_all_tools(mcp)
register_all_resources(mcp)
register_all_prompts(mcp)
logger.info("prompts_registered")


def main(**kwargs: Any) -> None:
    """Main entry point for the StockTrim MCP Server.

    This function is called when running the server via:
    - uvx stocktrim-mcp-server
    - python -m stocktrim_mcp_server
    - stocktrim-mcp-server (console script)

    Args:
        **kwargs: Additional arguments passed to mcp.run()
    """
    # Configure structured logging before anything else
    configure_logging()

    logger.info("server_starting", version=__version__)
    mcp.run(**kwargs)


if __name__ == "__main__":
    main()
