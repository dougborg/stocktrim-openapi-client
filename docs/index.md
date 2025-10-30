# StockTrim OpenAPI Client

Welcome to the **StockTrim OpenAPI Client** documentation. This library provides a
modern, Pythonic client for the StockTrim Inventory Management API, along with a Model
Context Protocol (MCP) server for AI agent integration.

## Features

### Client Library

- **Transport-layer resilience**: Automatic retries and custom authentication at the
  HTTP transport level
- **Type-safe**: Full type hints and mypy compatibility
- **Async/await support**: Built on httpx for modern Python async patterns
- **Production-ready**: Comprehensive error handling and logging
- **Zero-wrapper philosophy**: All resilience features work transparently with the
  generated API client
- **Helper methods**: Ergonomic convenience methods for common operations

### MCP Server

- **AI Agent Integration**: Connect Claude Desktop and other AI tools to StockTrim
- **20+ Tools**: Comprehensive coverage of StockTrim API operations
- **Type-safe**: Full type checking and validation
- **Easy Setup**: Simple installation and configuration

## Quick Start

### Installation

```bash
pip install stocktrim-openapi-client
```

### Basic Usage

```python
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products

async def main():
    async with StockTrimClient() as client:
        # Automatically includes retries and auth headers
        response = await get_api_products.asyncio_detailed(client=client)

        if response.status_code == 200:
            products = response.parsed
            print(f"Found {len(products)} products")
```

### Using Helper Methods

```python
from stocktrim_public_api_client import StockTrimClient

async def main():
    async with StockTrimClient() as client:
        # Find a specific product
        product = await client.products.find_by_code("WIDGET-001")

        # Search for products
        widgets = await client.products.search("WIDGET")

        # Get all customers
        customers = await client.customers.get_all()
```

## Configuration

Configure via environment variables:

```bash
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
STOCKTRIM_BASE_URL=https://api.stocktrim.com  # optional
```

Or via direct initialization:

```python
from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient(
    api_auth_id="your_tenant_id",
    api_auth_signature="your_tenant_name",
    base_url="https://api.stocktrim.com",
    max_retries=5
) as client:
    # Use the client
    pass
```

## Architecture

The client uses a **transport-layer resilience** approach where resilience features
(retries, custom authentication) are implemented at the HTTP transport level rather than
as decorators or wrapper methods. This means:

- All generated API methods automatically get resilience features
- No code changes needed when the OpenAPI spec is updated
- Type safety is preserved throughout the entire client
- Performance is optimized by handling resilience at the lowest level

## Project Structure

This is a monorepo containing two packages:

- **`stocktrim-openapi-client`**: The Python client library
- **`stocktrim-mcp-server`**: Model Context Protocol server for AI integration

## Links

- [PyPI (Client)](https://pypi.org/project/stocktrim-openapi-client/)
- [PyPI (MCP Server)](https://pypi.org/project/stocktrim-mcp-server/)
- [GitHub Repository](https://github.com/dougborg/stocktrim-openapi-client)
- [Issue Tracker](https://github.com/dougborg/stocktrim-openapi-client/issues)
- [Changelog](https://github.com/dougborg/stocktrim-openapi-client/blob/main/docs/CHANGELOG.md)

## License

MIT License - see
[LICENSE](https://github.com/dougborg/stocktrim-openapi-client/blob/main/LICENSE) for
details.
