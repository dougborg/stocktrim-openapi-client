# StockTrim OpenAPI Client

A production-ready Python client for the StockTrim Inventory Management API with
transport-layer resilience and multi-integration support.

## Features

- **🔄 Automatic Retries**: Built-in exponential backoff for network failures and server
  errors
- **🔐 Custom Authentication**: Automatic handling of StockTrim's `api-auth-id` and
  `api-auth-signature` headers
- **⚡ Modern Python**: Fully async/await support with comprehensive type hints
- **🛡️ Transport-Layer Resilience**: Retry logic built into HTTP transport for all API
  calls
- **🔀 Multi-Integration Support**: Handle both StockTrim native data (DTO models) and
  third-party integrations (Square, etc.)
- **📦 Generated from OpenAPI**: Always up-to-date with the latest StockTrim API
- **🎯 No Pagination Complexity**: Simplified transport layer since StockTrim doesn't use
  pagination

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
from stocktrim_public_api_client.generated.api.products import get_api_products
from stocktrim_public_api_client.generated.api.customers import (
    get_api_customers_dto,  # StockTrim native format
    get_api_customers       # Square integration format
)

async def main():
    # Set up your credentials (or use environment variables)
    async with StockTrimClient(
        api_auth_id="your_tenant_id",
        api_auth_signature="your_tenant_name"
    ) as client:
        # All API calls get automatic retries and authentication

        # Get products
        products_response = await get_api_products.asyncio_detailed(client=client)
        if products_response.status_code == 200:
            products = products_response.parsed
            print(f"Found {len(products)} products")

        # Get customers in StockTrim native format
        customers_dto_response = await get_api_customers_dto.asyncio_detailed(client=client)
        if customers_dto_response.status_code == 200:
            stocktrim_customers = customers_dto_response.parsed
            print(f"Found {len(stocktrim_customers)} StockTrim customers")

        # Get customers in Square integration format
        customers_response = await get_api_customers.asyncio_detailed(client=client)
        if customers_response.status_code == 200:
            square_customers = customers_response.parsed
            print(f"Found {len(square_customers)} Square customers")

# Run the example
asyncio.run(main())
```

## Multi-Integration Architecture

StockTrim's API uniquely supports both native data formats and third-party integrations:

### DTO Models (StockTrim Native)

Models with "Dto" suffix represent StockTrim's internal format:

- `CustomerDto` - Native customer format with fields like `code`, `name`,
  `street_address`
- `ProductDto` - Native product format optimized for inventory management
- Simple, flat structure focused on core business operations

### Integration Models (Third-Party)

Models without "Dto" suffix represent external system formats:

- `Customer` - Square POS integration with `given_name`, `family_name`, nested `Address`
- `Product` - Third-party product integration formats
- Complex, nested structures matching external API requirements

This dual approach allows seamless data synchronization between StockTrim and external
systems like Square, Shopify, or other POS/ERP platforms.

## Environment Variables

Create a `.env` file in your project:

```bash
# Copy from .env.example and fill in your credentials
STOCKTRIM_API_AUTH_ID=your_tenant_id_here
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name_here
```

## Development

This client implements the proven transport-layer resilience pattern from our Katana
client:

- ✅ **Retries**: Automatic exponential backoff for network and server errors
- ✅ **Authentication**: Custom header authentication handled transparently
- ✅ **Error Handling**: Consistent error parsing across all endpoints
- ✅ **Modern Tooling**: Pre-commit hooks, type checking, automated formatting
- ✅ **Simplified Transport**: No pagination complexity since StockTrim doesn't paginate
- ✅ **Multi-Integration**: Support for both native and third-party data formats

### Development Setup

```bash
# Install dependencies
poetry install

# Set up pre-commit hooks (required for development)
poetry run poe pre-commit-install

# Run all quality checks
poetry run poe check

# Format code
poetry run poe format

# Run tests
poetry run poe test

# Regenerate client from latest OpenAPI spec
poetry run poe regenerate-client
```

### Quality Gates

Before committing, ensure all quality checks pass:

```bash
# Full quality pipeline
poetry run poe ci

# Individual checks
poetry run poe lint          # MyPy type checking
poetry run poe format-check  # Code formatting validation
poetry run poe test          # Test suite
```

## Architecture

Built on the proven transport-layer resilience pattern:

- **Transport-Layer Resilience**: All retry logic happens at the HTTP transport level,
  not as decorators or wrappers
- **Multi-Integration Support**: Dual model system supports both StockTrim native data
  (DTO models) and third-party integrations (non-DTO models)
- **No Pagination Complexity**: Simplified compared to other clients since StockTrim
  doesn't use pagination
- **Type Safety**: Full mypy type checking on all custom code
- **Modern Python Packaging**: PEP 621 compliant with Poetry and poethepoet tasks
- **Generated from OpenAPI**: Client auto-generated from live StockTrim API
  specification

### Key Architectural Decisions

1. **Transport-Layer Pattern**: Resilience built into HTTP transport means ALL API calls
   get retries automatically
1. **Custom Authentication**: StockTrim's unique header-based auth handled transparently
1. **Model Duality**: Support both native StockTrim formats and external integration
   formats in same client
1. **No Rate Limiting**: Simplified transport since StockTrim doesn't implement rate
   limits

See `docs/STOCKTRIM_CLIENT_GUIDE.md` for detailed architecture documentation.

## License

MIT License - see LICENSE file for details.
