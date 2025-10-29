# Error Handling

The StockTrim client implements robust error handling with automatic retries at the transport layer.

## Automatic Retry Logic

The client automatically retries failed requests with exponential backoff for:

- Network errors (connection failures, timeouts)
- Transient server errors (500, 502, 503, 504)
- Rate limiting (429)
- Request timeouts (408)

### Retry Configuration

```python
from stocktrim_public_api_client import StockTrimClient

# Configure retry behavior
async with StockTrimClient(
    max_retries=5,  # Maximum retry attempts
    timeout=30.0    # Request timeout in seconds
) as client:
    # Requests will retry up to 5 times with exponential backoff
    pass
```

## HTTP Status Codes

### Success Codes (2xx)

```python
from stocktrim_public_api_client.generated.api.products import get_api_products

async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

    if response.status_code == 200:
        products = response.parsed
        print(f"Success: Found {len(products)} products")
    elif response.status_code == 201:
        print("Resource created successfully")
```

### Client Errors (4xx)

```python
async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

    if response.status_code == 400:
        print("Bad request: Check your input data")
    elif response.status_code == 401:
        print("Authentication failed: Check your credentials")
    elif response.status_code == 403:
        print("Forbidden: Insufficient permissions")
    elif response.status_code == 404:
        print("Resource not found (may be empty in test environments)")
```

### Server Errors (5xx)

Server errors are automatically retried by the transport layer:

```python
# These are handled automatically with exponential backoff
# - 500: Internal Server Error
# - 502: Bad Gateway
# - 503: Service Unavailable
# - 504: Gateway Timeout
```

## Exception Handling

### Network Errors

```python
import httpx

async with StockTrimClient() as client:
    try:
        response = await get_api_products.asyncio_detailed(client=client)
    except httpx.ConnectError:
        print("Connection failed: Check network and base URL")
    except httpx.TimeoutException:
        print("Request timed out: Try increasing timeout")
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
```

### Authentication Errors

```python
async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

    if response.status_code == 401:
        print("Authentication failed")
        print("Check STOCKTRIM_API_AUTH_ID and STOCKTRIM_API_AUTH_SIGNATURE")
```

### Validation Errors

```python
from pydantic import ValidationError

try:
    product = ProductsRequestDto(
        code="INVALID",
        # Missing required fields
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Best Practices

### 1. Always Check Status Codes

```python
response = await get_api_products.asyncio_detailed(client=client)

if response.status_code == 200:
    # Success
    products = response.parsed
elif response.status_code == 404:
    # Empty result (normal in test environments)
    products = []
else:
    # Unexpected status
    print(f"Unexpected status: {response.status_code}")
    print(f"Response: {response.content}")
```

### 2. Handle Empty Results

```python
response = await get_api_customers.asyncio_detailed(client=client)

if response.status_code == 200:
    customers = response.parsed or []  # Handle None
    if not customers:
        print("No customers found")
elif response.status_code == 404:
    customers = []
    print("Customer endpoint returned 404 (empty)")
```

### 3. Log Errors for Debugging

```python
import logging

logger = logging.getLogger(__name__)

try:
    response = await get_api_products.asyncio_detailed(client=client)

    if response.status_code != 200:
        logger.error(
            f"API error: status={response.status_code}, "
            f"content={response.content}"
        )
except Exception as e:
    logger.exception("Request failed")
    raise
```

### 4. Use Context Managers

```python
# ✅ Good: Automatic cleanup
async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

# ❌ Avoid: Manual cleanup
client = StockTrimClient()
try:
    response = await get_api_products.asyncio_detailed(client=client)
finally:
    await client.close()
```

## Common Error Scenarios

### Scenario 1: Empty Test Environment

```python
# 404 is normal in empty test environments
response = await get_api_products.asyncio_detailed(client=client)

if response.status_code in (200, 404):
    products = response.parsed if response.status_code == 200 else []
    print(f"Found {len(products)} products")
else:
    print(f"Unexpected error: {response.status_code}")
```

### Scenario 2: Temporary Network Issues

```python
# Transport layer handles this automatically with retries
async with StockTrimClient(max_retries=10) as client:
    # Will retry up to 10 times on network errors
    response = await get_api_products.asyncio_detailed(client=client)
```

### Scenario 3: Invalid Credentials

```python
import os

# Verify credentials are set
auth_id = os.getenv("STOCKTRIM_API_AUTH_ID")
auth_sig = os.getenv("STOCKTRIM_API_AUTH_SIGNATURE")

if not auth_id or not auth_sig:
    raise ValueError("Missing StockTrim credentials in environment")

async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

    if response.status_code == 401:
        print("Credentials are invalid or expired")
```

### Scenario 4: Rate Limiting

```python
# Automatically handled with exponential backoff
async with StockTrimClient() as client:
    response = await get_api_products.asyncio_detailed(client=client)

    # If 429 occurs, client will automatically retry with backoff
```

## Debugging Failed Requests

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("stocktrim_public_api_client")
```

### Inspect Response Details

```python
response = await get_api_products.asyncio_detailed(client=client)

print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Content: {response.content}")
print(f"Parsed: {response.parsed}")
```

### Check Request Configuration

```python
import os

print(f"Base URL: {os.getenv('STOCKTRIM_BASE_URL', 'https://api.stocktrim.com')}")
print(f"Auth ID: {os.getenv('STOCKTRIM_API_AUTH_ID', 'NOT SET')}")
print(f"Auth Sig: {os.getenv('STOCKTRIM_API_AUTH_SIGNATURE', 'NOT SET')}")
```

## Next Steps

- [Client Usage Guide](client-guide.md) - Learn more about using the client
- [Testing Guide](testing.md) - Test your error handling
- [Configuration](../getting-started/configuration.md) - Configure retry behavior
