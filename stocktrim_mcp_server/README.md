# StockTrim MCP Server

Model Context Protocol (MCP) server for
[StockTrim Inventory Management](https://www.stocktrim.com/).

This server provides AI assistants like Claude with tools to interact with your
StockTrim inventory system, enabling natural language queries and operations for product
management, customer data, and inventory control.

## Features

- **Product Management**: Create, retrieve, update, and delete products with full
  lifecycle support
- **Customer Operations**: Access and manage customer data
- **Supplier Management**: Manage supplier information and relationships
- **Inventory Control**: Set and update inventory levels across locations
- **Purchase Orders**: Create and manage purchase orders with line items
- **Sales Orders**: Track and manage sales orders
- **Workflow Tools**: High-level business operations (forecast management, urgent
  orders)
- **Safety Features**: User confirmation for destructive operations via MCP elicitation
  ([ADR 001](../docs/architecture/decisions/001-user-confirmation-pattern.md))
- **Service Layer Architecture**: Clean separation of business logic with dependency
  injection
- **Type-Safe**: Full type hints with Pydantic validation for all operations
  ([ADR 002](../docs/architecture/decisions/002-tool-interface-pattern.md))
- **Production-Ready**: Built-in error handling, logging, and resilience
- **FastMCP**: Leverages FastMCP 2.11.0 for high-performance MCP implementation

## Installation

### Using UV (Recommended)

```bash
# Install from workspace
cd stocktrim-openapi-client
uv sync --all-extras

# Run server
uvx --from . stocktrim-mcp-server
```

### Using Pip

```bash
pip install stocktrim-mcp-server
stocktrim-mcp-server
```

## Configuration

The server requires StockTrim API credentials via environment variables:

### Environment Variables

Create a `.env` file in your project root or set these in your environment:

```bash
# Required
STOCKTRIM_API_AUTH_ID=your_tenant_id_here
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name_here

# Optional
STOCKTRIM_BASE_URL=https://api.stocktrim.com  # Default
```

### Getting Your Credentials

1. Log in to your StockTrim account
1. Navigate to Settings → API Settings
1. Copy your **Tenant ID** (use as `STOCKTRIM_API_AUTH_ID`)
1. Copy your **Tenant Name** (use as `STOCKTRIM_API_AUTH_SIGNATURE`)

## Claude Desktop Integration

To use this MCP server with Claude Desktop, add it to your Claude configuration:

### On macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stocktrim": {
      "command": "uvx",
      "args": ["stocktrim-mcp-server"],
      "env": {
        "STOCKTRIM_API_AUTH_ID": "your_tenant_id_here",
        "STOCKTRIM_API_AUTH_SIGNATURE": "your_tenant_name_here"
      }
    }
  }
}
```

### On Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json` with the same configuration.

### Using Python Environment

If you have the server installed in a specific Python environment:

```json
{
  "mcpServers": {
    "stocktrim": {
      "command": "python",
      "args": ["-m", "stocktrim_mcp_server"],
      "env": {
        "STOCKTRIM_API_AUTH_ID": "your_tenant_id_here",
        "STOCKTRIM_API_AUTH_SIGNATURE": "your_tenant_name_here"
      }
    }
  }
}
```

After configuring, restart Claude Desktop for changes to take effect.

## Available Tools

### Product Tools

#### `get_product`

Get detailed information about a specific product by code.

**Parameters:**

- `code` (string, required): Product code to retrieve

**Returns:** ProductInfo object with code, description, pricing, and status

**Example Claude prompt:**

```
Get product information for code "WIDGET-001"
```

#### `search_products`

Search for products by code prefix.

**Parameters:**

- `prefix` (string, required): Product code prefix to search for

**Returns:** List of matching products

**Example Claude prompt:**

```
Find all products starting with "WIDGET"
```

### Customer Tools

#### `get_customer`

Get detailed information about a specific customer by code.

**Parameters:**

- `code` (string, required): Customer code to retrieve

**Returns:** CustomerInfo object with code, name, contact information

**Example Claude prompt:**

```
Show me customer CUST-001
```

#### `list_customers`

List all customers in the system.

**Parameters:**

- `limit` (integer, optional): Maximum number of customers to return (default: 50)

**Returns:** List of customers

**Example Claude prompt:**

```
List the first 20 customers
```

### Inventory Tools

#### `set_product_inventory`

Update inventory levels for a product.

**Parameters:**

- `product_id` (string, required): Product ID to update
- `stock_on_hand` (number, optional): Current stock quantity
- `stock_on_order` (number, optional): Quantity on order
- `location_code` (string, optional): Location code
- `location_name` (string, optional): Location name

**Returns:** Operation result with success status

**Example Claude prompt:**

```
Set inventory for product 123 to 50 units on hand and 100 on order at location WAREHOUSE-A
```

## Example Conversations

### Product Discovery

```
You: What products do we have starting with "WID"?
Claude: Using search_products("WID")...
Found 3 products:
- WIDGET-001: Standard Widget ($10.00)
- WIDGET-002: Premium Widget ($15.00)
- WIDGET-SPECIAL: Custom Widget ($25.00)
```

### Inventory Management

```
You: Update inventory for product 123 - we have 75 units in the main warehouse
Claude: Using set_product_inventory(product_id="123", stock_on_hand=75, location_code="MAIN")...
Successfully updated inventory for product 123. Stock on hand is now 75 units.
```

### Customer Lookup

```
You: Get contact information for customer ACME-001
Claude: Using get_customer("ACME-001")...
Customer: ACME Corporation
Email: contact@acme.com
Phone: +1-555-0123
Address: 123 Main St, City, ST 12345
```

## Development

### Running Locally

```bash
# Clone repository
git clone https://github.com/dougborg/stocktrim-openapi-client.git
cd stocktrim-openapi-client

# Install dependencies
uv sync --all-extras

# Set environment variables
export STOCKTRIM_API_AUTH_ID=your_tenant_id
export STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name

# Run server
uv run stocktrim-mcp-server
```

### Project Structure

```
stocktrim_mcp_server/
├── src/stocktrim_mcp_server/
│   ├── __init__.py          # Package metadata
│   ├── server.py            # FastMCP server setup
│   └── tools/               # Tool implementations
│       ├── __init__.py      # Tool registration
│       ├── products.py      # Product management tools
│       ├── customers.py     # Customer management tools
│       └── inventory.py     # Inventory management tools
├── pyproject.toml           # Package configuration
└── README.md               # This file
```

### Adding New Tools

1. Create a new file in `src/stocktrim_mcp_server/tools/`
1. Define your tool functions with type hints
1. Use the `@unpack_pydantic_params` decorator for parameter flattening
1. Create a `register_tools(mcp: FastMCP)` function
1. Import and call in `tools/__init__.py`

See existing tools for examples.

#### Parameter Flattening Pattern

All tools use a parameter flattening decorator to expose Pydantic model fields as
individual tool parameters. This provides better MCP client compatibility while
maintaining type safety.

**Example Tool Implementation:**

```python
from typing import Annotated
from fastmcp import Context
from pydantic import BaseModel, Field
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

class SearchProductsRequest(BaseModel):
    """Request model for searching products."""
    search_query: str = Field(..., description="Search query for product name or code")
    limit: int = Field(10, description="Maximum number of results")

class SearchProductsResponse(BaseModel):
    """Response containing matching products."""
    products: list[ProductInfo]
    total_count: int

@unpack_pydantic_params
async def search_products(
    request: Annotated[SearchProductsRequest, Unpack()],
    context: Context
) -> SearchProductsResponse:
    """Search for products by name or code.

    This tool searches across product fields using keyword matching.
    """
    # Inside the function, 'request' is a validated SearchProductsRequest instance
    services = get_services(context)
    results = await services.products.search(request.search_query, request.limit)
    return SearchProductsResponse(products=results, total_count=len(results))
```

**What FastMCP Sees:**

```python
# Tool signature exposed to MCP clients:
search_products(
    search_query: str,      # From SearchProductsRequest.search_query
    limit: int = 10,        # From SearchProductsRequest.limit
    context: Context
) -> SearchProductsResponse
```

**Benefits:**

- ✅ **MCP Compatibility**: Flat parameters work reliably with Claude Code and other
  clients
- ✅ **Type Safety**: Pydantic validation ensures parameter correctness
- ✅ **Clean Code**: Tool implementations work with typed model instances
- ✅ **Auto Documentation**: Field descriptions become parameter documentation

**See Also:**
[ADR 0001: Parameter Flattening](docs/adr/0001-parameter-flattening-for-mcp-tools.md)

## Logging

The server logs to standard output with INFO level by default. Logs include:

- Server lifecycle events (startup, shutdown)
- Tool invocations
- API call results
- Error details

To adjust log level:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG
uv run stocktrim-mcp-server
```

## Troubleshooting

### Authentication Errors

```
ValueError: STOCKTRIM_API_AUTH_ID environment variable is required
```

**Solution:** Ensure both `STOCKTRIM_API_AUTH_ID` and `STOCKTRIM_API_AUTH_SIGNATURE` are
set in your environment or `.env` file.

### Connection Failures

```
Failed to initialize StockTrimClient: Connection refused
```

**Solution:**

- Check that `STOCKTRIM_BASE_URL` is correct (default: https://api.stocktrim.com)
- Verify your network connection
- Ensure StockTrim API is accessible

### Tool Not Found

```
Tool 'xyz' not found
```

**Solution:** Restart Claude Desktop after updating configuration.

## Security Notes

- **Never commit** `.env` files or expose API credentials in code
- **Use environment variables** for credential management
- **Consider** using a secrets manager in production environments
- **Credentials are passed** to StockTrim API via secure HTTPS headers
- **Client includes** automatic retry logic with exponential backoff

## Support

- **Issues**:
  [GitHub Issues](https://github.com/dougborg/stocktrim-openapi-client/issues)
- **Documentation**:
  [Client Documentation](https://dougborg.github.io/stocktrim-openapi-client/)
- **StockTrim API**: [API Documentation](https://www.stocktrim.com/api-docs)

## License

MIT License - see LICENSE file for details

## Related Projects

- [stocktrim-openapi-client](../README.md): Python client library for StockTrim API
- [FastMCP](https://github.com/jlowin/fastmcp): High-performance MCP server framework

## Changelog

### v0.1.0 (2025-10-29)

- Initial release
- Product management tools (get, search)
- Customer management tools (get, list)
- Inventory management tools (set levels)
- Claude Desktop integration
- FastMCP-based implementation
