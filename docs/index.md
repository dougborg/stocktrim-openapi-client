# StockTrim OpenAPI Client Documentation

Welcome to the **StockTrim OpenAPI Client** documentation. This is a modern, pythonic
client for the StockTrim Inventory Management API built with transport-layer resilience.

## Features

- **Transport-layer resilience**: Automatic retries and custom authentication at the
  HTTP transport level
- **Type-safe**: Full type hints and mypy compatibility
- **Async/await support**: Built on httpx for modern Python async patterns
- **Production-ready**: Comprehensive error handling and logging
- **Zero-wrapper philosophy**: All resilience features work transparently with the
  generated API client

## Quick Start

```python
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.api.products import get_api_products

async def main():
    async with StockTrimClient() as client:
        # This call automatically gets retries and auth headers
        response = await get_api_products.asyncio_detailed(client=client)

        if response.status_code == 200:
            products = response.parsed
            print(f"Found {len(products)} products")
```

## Architecture

The client uses a **transport-layer resilience** approach where resilience features
(retries, custom authentication) are implemented at the HTTP transport level rather than
as decorators or wrapper methods. This means:

- All generated API methods automatically get resilience features
- No code changes needed when the OpenAPI spec is updated
- Type safety is preserved throughout the entire client
- Performance is optimized by handling resilience at the lowest level

## StockTrim-Specific Features

- **Custom Header Authentication**: Automatic `api-auth-id` and `api-auth-signature`
  headers
- **No Pagination**: Simplified for StockTrim's direct response model
- **Inventory Focus**: Optimized for inventory management operations

## Documentation Structure

```{toctree}
:maxdepth: 2
:caption: User Guides

STOCKTRIM_CLIENT_GUIDE
TESTING_GUIDE
```

```{toctree}
:maxdepth: 2
:caption: API Reference

autoapi/stocktrim_public_api_client/index
```

```{toctree}
:maxdepth: 2
:caption: Development

POETRY_USAGE
```

```{toctree}
:maxdepth: 2
:caption: Project Information

CODE_OF_CONDUCT
```

## API Reference

The API reference documentation is automatically generated from the source code
docstrings and includes:

- **Main Client Classes**: `StockTrimClient`, `ResilientAsyncTransport`
- **Generated API Methods**: All endpoint methods with full type annotations
- **Data Models**: All request/response models with validation

## Installation

```bash
pip install stocktrim-openapi-client
```

## Configuration

The client can be configured through environment variables or direct initialization:

```python
# Via environment variables (.env file)
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name

# Via direct initialization
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

## Support

- **Documentation**:
  [GitHub Pages](https://dougborg.github.io/stocktrim-openapi-client/)
- **Issues**:
  [GitHub Issues](https://github.com/dougborg/stocktrim-openapi-client/issues)
- **Source**: [GitHub Repository](https://github.com/dougborg/stocktrim-openapi-client)

## License

MIT License - see
[LICENSE](https://github.com/dougborg/stocktrim-openapi-client/blob/main/LICENSE) for
details.
