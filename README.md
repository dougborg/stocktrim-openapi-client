# StockTrim OpenAPI Client

A modern, pythonic StockTrim Inventory Management API client with automatic retries and custom authentication.

## Features

- **🔄 Automatic Retries**: Built-in exponential backoff for network failures and server errors
- **🔐 Custom Authentication**: Automatic handling of StockTrim's `api-auth-id` and `api-auth-signature` headers
- **⚡ Modern Python**: Fully async/await support with type hints
- **🛡️ Transport-Layer Resilience**: Retry logic built into HTTP transport for all API calls
- **📦 Generated from OpenAPI**: Always up-to-date with the latest StockTrim API

## Installation

```bash
# Install with Poetry (recommended)
poetry add stocktrim-openapi-client

# Or with pip
pip install stocktrim-openapi-client
```

## Quick Start

```python
import asyncio
from stocktrim_public_api_client import StockTrimClient

async def main():
    # Set up your credentials (or use environment variables)
    async with StockTrimClient(
        api_auth_id="your_tenant_id",
        api_auth_signature="your_tenant_name"
    ) as client:
        # All API calls get automatic retries and authentication
        # Example: Get all products
        # response = await some_products_api.asyncio_detailed(client=client)
        pass

# Run the example
asyncio.run(main())
```

## Environment Variables

Create a `.env` file in your project:

```bash
# Copy from .env.example and fill in your credentials
STOCKTRIM_API_AUTH_ID=your_tenant_id_here
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name_here
```

## Development

This client uses your proven transport-layer resilience pattern:

- ✅ **Retries**: Automatic exponential backoff for network and server errors
- ✅ **Authentication**: Custom header authentication handled transparently
- ✅ **Error Handling**: Consistent error parsing across all endpoints
- ✅ **Modern Tooling**: Pre-commit hooks, type checking, automated formatting

### Development Setup

```bash
# Install dependencies
poetry install

# Set up pre-commit hooks
poetry run poe pre-commit-install

# Run tests
poetry run poe test

# Format code
poetry run poe format

# Check everything
poetry run poe check
```

## Architecture

Built on the same proven patterns as the Katana client:

- **Transport-Layer Resilience**: All retry logic happens at the HTTP transport level
- **No Decorators**: Generated API methods work transparently with resilience features
- **Type Safety**: Full mypy type checking on custom code
- **Modern Python Packaging**: PEP 621 compliant with Poetry

## License

MIT License - see LICENSE file for details.
