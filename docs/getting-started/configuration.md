# Configuration

The StockTrim OpenAPI Client can be configured through environment variables or direct initialization parameters.

## Environment Variables

The recommended way to configure the client is through environment variables:

```bash
# Required
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name

# Optional
STOCKTRIM_BASE_URL=https://api.stocktrim.com
STOCKTRIM_MAX_RETRIES=5
STOCKTRIM_TIMEOUT=30.0
```

### Using a `.env` File

Create a `.env` file in your project root:

```bash
STOCKTRIM_API_AUTH_ID=tenant123
STOCKTRIM_API_AUTH_SIGNATURE=MyCompany
STOCKTRIM_BASE_URL=https://api.stocktrim.com
```

The client automatically loads these variables using `python-dotenv`.

## Direct Initialization

You can also configure the client directly when creating it:

```python
from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient(
    api_auth_id="tenant123",
    api_auth_signature="MyCompany",
    base_url="https://api.stocktrim.com",
    max_retries=5,
    timeout=30.0
) as client:
    # Use the client
    pass
```

## Configuration Options

### Required Settings

#### `api_auth_id`
- **Environment Variable**: `STOCKTRIM_API_AUTH_ID`
- **Description**: Your StockTrim tenant ID
- **Required**: Yes

#### `api_auth_signature`
- **Environment Variable**: `STOCKTRIM_API_AUTH_SIGNATURE`
- **Description**: Your StockTrim tenant name/signature
- **Required**: Yes

### Optional Settings

#### `base_url`
- **Environment Variable**: `STOCKTRIM_BASE_URL`
- **Description**: The base URL for the StockTrim API
- **Default**: `https://api.stocktrim.com`

#### `max_retries`
- **Environment Variable**: `STOCKTRIM_MAX_RETRIES`
- **Description**: Maximum number of retry attempts for failed requests
- **Default**: `5`
- **Note**: Uses exponential backoff

#### `timeout`
- **Environment Variable**: `STOCKTRIM_TIMEOUT`
- **Description**: Request timeout in seconds
- **Default**: `30.0`

## Authentication

The client uses custom header authentication with two required headers:

- `api-auth-id`: Your tenant ID
- `api-auth-signature`: Your tenant signature

These are automatically added to all requests by the `ResilientAsyncTransport` layer.

## Retry Behavior

The client implements automatic retry logic with exponential backoff for transient failures:

- **Retryable Status Codes**: 408, 429, 500, 502, 503, 504
- **Retry Strategy**: Exponential backoff with jitter
- **Maximum Retries**: Configurable (default: 5)

Example retry configuration:

```python
from stocktrim_public_api_client import StockTrimClient

# More aggressive retries
async with StockTrimClient(max_retries=10) as client:
    # Client will retry up to 10 times
    pass

# No retries
async with StockTrimClient(max_retries=0) as client:
    # Client will not retry failed requests
    pass
```

## Multiple Environments

You can manage multiple environments using different `.env` files:

### Production (`.env.production`)
```bash
STOCKTRIM_API_AUTH_ID=prod_tenant
STOCKTRIM_API_AUTH_SIGNATURE=ProdCompany
STOCKTRIM_BASE_URL=https://api.stocktrim.com
```

### Development (`.env.development`)
```bash
STOCKTRIM_API_AUTH_ID=dev_tenant
STOCKTRIM_API_AUTH_SIGNATURE=DevCompany
STOCKTRIM_BASE_URL=https://dev-api.stocktrim.com
```

Load the appropriate environment:

```python
from dotenv import load_dotenv
import os

# Load production config
load_dotenv(".env.production")

# Or load based on environment variable
env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")
```

## Advanced Configuration

### Custom HTTP Client

The client uses `httpx` under the hood. You can provide custom configuration:

```python
import httpx
from stocktrim_public_api_client import StockTrimClient

# Create client with custom limits
async with StockTrimClient(
    max_retries=5,
    timeout=60.0
) as client:
    # The transport layer handles connection pooling
    pass
```

### Logging

Enable debug logging to see retry behavior:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("stocktrim_public_api_client")
```

## Best Practices

1. **Use Environment Variables**: Keep credentials out of code
2. **Set Appropriate Timeouts**: Balance responsiveness with reliability
3. **Configure Retries**: Higher retries for production, lower for development
4. **Monitor Failed Requests**: Log and monitor retry exhaustion
5. **Use `.env` Files**: Never commit `.env` files to version control

## Next Steps

- [Client Usage Guide](../user-guide/client-guide.md) - Learn how to use the client
- [Error Handling](../user-guide/error-handling.md) - Handle errors gracefully
- [API Reference](../api/client.md) - Complete API documentation
