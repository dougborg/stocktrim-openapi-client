# Transport Layer

The transport layer implements resilience features at the HTTP level.

## ResilientAsyncTransport

The `ResilientAsyncTransport` class wraps HTTPX's `AsyncHTTPTransport` to provide:

- Automatic retry with exponential backoff
- Custom authentication headers
- Request/response logging
- Configurable timeouts

## Implementation

```python
class ResilientAsyncTransport(AsyncHTTPTransport):
    def __init__(
        self,
        api_auth_id: str,
        api_auth_signature: str,
        max_retries: int = 5,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.api_auth_id = api_auth_id
        self.api_auth_signature = api_auth_signature
        self.max_retries = max_retries
```

## Retry Logic

### Retryable Conditions

The transport automatically retries for:

- **Network errors**: Connection failures, DNS errors
- **Timeout errors**: Request timeout exceeded
- **Server errors**: 500, 502, 503, 504
- **Rate limiting**: 429 Too Many Requests
- **Request timeout**: 408 Request Timeout

### Exponential Backoff

Retry delays follow exponential backoff with jitter:

```
Attempt 1: 1 second
Attempt 2: 2 seconds
Attempt 3: 4 seconds
Attempt 4: 8 seconds
Attempt 5: 16 seconds
```

Jitter (±25%) prevents thundering herd problems.

## Authentication

### Custom Headers

The transport automatically adds StockTrim's custom auth headers:

```python
def handle_request(self, request):
    # Add custom authentication headers
    request.headers["api-auth-id"] = self.api_auth_id
    request.headers["api-auth-signature"] = self.api_auth_signature

    return super().handle_request(request)
```

### No Bearer Tokens

Unlike many APIs, StockTrim uses custom headers instead of bearer tokens. The transport abstracts this detail from application code.

## Connection Pooling

The transport inherits HTTPX's connection pooling:

- Reuses TCP connections
- Supports HTTP/2
- Configurable limits
- Automatic cleanup

## Error Handling

### Recoverable Errors

These are retried automatically:

```python
try:
    response = await transport.handle_request(request)
except (ConnectError, TimeoutException):
    # Retry with exponential backoff
    ...
```

### Non-Recoverable Errors

These are raised immediately:

```python
if response.status_code in (400, 401, 403):
    # Don't retry client errors
    return response
```

## Configuration

### Timeout Configuration

```python
from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient(
    timeout=30.0  # 30 second timeout
) as client:
    pass
```

### Retry Configuration

```python
async with StockTrimClient(
    max_retries=10  # Up to 10 retry attempts
) as client:
    pass
```

## Benefits

### 1. Transparency

Application code doesn't need to know about:
- Retry logic
- Authentication details
- Connection pooling

### 2. Centralization

All resilience logic in one place:
- Easy to test
- Easy to modify
- Easy to monitor

### 3. Composability

Works with any HTTPX-based client:
- Can be reused
- Follows standards
- Minimal dependencies

## Testing

### Unit Tests

```python
async def test_retry_on_500():
    transport = ResilientAsyncTransport(
        api_auth_id="test",
        api_auth_signature="test",
        max_retries=3
    )

    # Mock request that fails twice then succeeds
    ...
```

### Integration Tests

```python
async def test_real_api_with_retries():
    async with StockTrimClient(max_retries=5) as client:
        # Test against real API
        ...
```

## Next Steps

- [Architecture Overview](overview.md) - Overall architecture
- [Domain Helpers](helpers.md) - Helper method patterns
- [Client API](../api/client.md) - API reference
