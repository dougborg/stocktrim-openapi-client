# Logging Architecture

## Overview

The StockTrim client provides comprehensive logging to help diagnose API interactions,
debug issues, and monitor application behavior. This document describes the logging
architecture, configuration options, and best practices.

## Design Principles

1. **Structured Logging**: All logs include structured context (method, URL, status
   code, timing)
1. **Performance-Aware**: Minimize logging overhead in production while enabling
   detailed debugging when needed
1. **Privacy-First**: Never log sensitive data (API keys, passwords, PII) in any log
   level
1. **Developer-Friendly**: Provide clear, actionable log messages with sufficient
   context
1. **Configurable**: Allow fine-grained control over log levels and output formats

## Logging Levels

The client uses standard Python logging levels with specific semantics:

### DEBUG

**Purpose**: Detailed diagnostic information for development and troubleshooting

**Logged Information**:

- All HTTP requests (method, URL, headers - excluding auth)
- All HTTP responses (status code, headers, response body excerpt)
- Response body content for successful (2xx) responses (first 200 chars by default)
- Request/response timing information
- Retry attempts and backoff delays
- JSON parsing operations and results

**Use Cases**:

- Investigating why an API call failed
- Understanding what data the API actually returned
- Debugging type errors or unexpected None values
- Analyzing performance bottlenecks

**Example**:

```
2025-10-31 19:38:57 [DEBUG] [stocktrim_client] GET /api/V2/PurchaseOrders?status=Draft -> 200 (150ms)
2025-10-31 19:38:57 [DEBUG] [stocktrim_client] Response body: null (JSON null)
```

### INFO

**Purpose**: Confirmation that things are working as expected

**Logged Information**:

- Client initialization and configuration
- Successful API operations (without response bodies)
- Rate limit information
- Retry success messages

**Use Cases**:

- Monitoring application health
- Tracking API usage patterns
- Confirming successful operations

**Example**:

```
2025-10-31 19:38:56 [INFO] [stocktrim_client] StockTrim client initialized (base_url=https://api.stocktrim.com)
2025-10-31 19:38:57 [INFO] [stocktrim_client] GET /api/V2/PurchaseOrders -> 200 (342ms)
```

### WARNING

**Purpose**: Indication that something unexpected happened, but the client recovered

**Logged Information**:

- Deprecated API usage
- Unexpected response formats that were handled gracefully
- Rate limit warnings
- Automatic retry attempts for transient failures

**Use Cases**:

- Identifying potential issues before they become errors
- Monitoring API changes or deprecations
- Alerting on unusual patterns

**Example**:

```
2025-10-31 19:38:57 [WARNING] [stocktrim_client] API returned null for list endpoint, converting to empty list
2025-10-31 19:38:58 [WARNING] [stocktrim_client] Retrying GET /api/Products (attempt 2/3) after 500 error
```

### ERROR

**Purpose**: An error occurred, but the application can continue

**Logged Information**:

- HTTP 4xx client errors (with response body)
- HTTP 5xx server errors (after retries exhausted)
- Network errors
- JSON parsing errors
- Authentication failures

**Use Cases**:

- Alerting on production issues
- Tracking error rates
- Debugging integration problems

**Example**:

```
2025-10-31 19:39:00 [ERROR] [stocktrim_client] Client error 404 for GET /api/Products/invalid-id
2025-10-31 19:39:00 [ERROR] [stocktrim_client] Response: {"type":"about:blank","title":"Not Found","status":404}
```

### CRITICAL

**Purpose**: A serious error that prevents the application from functioning

**Logged Information**:

- Client initialization failures
- Unrecoverable authentication errors
- Configuration errors

**Use Cases**:

- Emergency alerting
- Application startup validation

## Logging Components

### ErrorLoggingTransport

The `ErrorLoggingTransport` class wraps the HTTP transport layer to intercept all
requests and responses.

**Previous Implementation** (4xx errors only):

```python
class ErrorLoggingTransport(AsyncHTTPTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self._wrapped_transport.handle_async_request(request)

        if 400 <= response.status_code < 500:
            await self._log_client_error(response, request)

        return response
```

**New Implementation** (all responses at appropriate levels):

```python
class ErrorLoggingTransport(AsyncHTTPTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        start_time = time.time()
        response = await self._wrapped_transport.handle_async_request(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log based on status code
        if 200 <= response.status_code < 300:
            await self._log_success_response(response, request, duration_ms)
        elif 400 <= response.status_code < 500:
            await self._log_client_error(response, request, duration_ms)
        elif 500 <= response.status_code < 600:
            await self._log_server_error(response, request, duration_ms)
        else:
            await self._log_unexpected_status(response, request, duration_ms)

        return response

    async def _log_success_response(
        self, response: httpx.Response, request: httpx.Request, duration_ms: float
    ) -> None:
        """Log successful response at DEBUG or INFO level."""
        method = request.method
        url = str(request.url)
        status_code = response.status_code

        # INFO level: just status and timing
        self.logger.info(
            f"{method} {url} -> {status_code} OK ({duration_ms:.0f}ms)"
        )

        # DEBUG level: include response body excerpt
        if self.logger.isEnabledFor(logging.DEBUG):
            try:
                response_body = response.json()
                body_type = type(response_body).__name__

                if response_body is None:
                    self.logger.debug(
                        f"Response body: null (parsed as None)"
                    )
                elif isinstance(response_body, list):
                    self.logger.debug(
                        f"Response body: list[{len(response_body)}] items"
                    )
                elif isinstance(response_body, dict):
                    body_excerpt = str(response_body)[:200]
                    self.logger.debug(
                        f"Response body: {body_excerpt}..."
                    )
                else:
                    self.logger.debug(
                        f"Response body type: {body_type}, value: {str(response_body)[:200]}"
                    )
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                self.logger.debug(
                    f"Response body (non-JSON): {response.text[:200]}..."
                )
```

### Request Logging

**Desired**: Log all requests at DEBUG level with sanitized headers

```python
async def _log_request(self, request: httpx.Request) -> None:
    """Log request details at DEBUG level."""
    if not self.logger.isEnabledFor(logging.DEBUG):
        return

    # Sanitize headers (remove auth headers)
    safe_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {'authorization', 'api-auth-id', 'api-auth-signature'}
    }

    self.logger.debug(
        f"Request: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "headers": safe_headers,
        }
    )
```

### Response Body Logging

**Critical for Debugging Type Errors**:

When investigating issues like `TypeError: object of type 'NoneType' has no len()`, we
need to see:

1. What the API actually returned (the raw response body)
1. How Python parsed it (`None`, `[]`, `{}`, etc.)
1. What type the generated code expects

**Implementation**:

```python
async def _log_response_body_debug(
    self, response: httpx.Response, request: httpx.Request
) -> None:
    """Log response body details at DEBUG level for troubleshooting."""
    if not self.logger.isEnabledFor(logging.DEBUG):
        return

    method = request.method
    url = str(request.url)

    # Read response content if streaming
    if hasattr(response, "aread"):
        with contextlib.suppress(TypeError, AttributeError):
            await response.aread()

    # Log raw response text (truncated)
    raw_text = response.text[:500] if response.text else "(empty)"
    self.logger.debug(
        f"{method} {url} raw response: {raw_text}..."
    )

    # Try to parse as JSON and log type information
    try:
        parsed = response.json()
        parsed_type = type(parsed).__name__

        self.logger.debug(
            f"{method} {url} parsed as {parsed_type}: "
            f"{str(parsed)[:200] if parsed is not None else 'None'}"
        )

        # Special handling for None (this is often the source of bugs!)
        if parsed is None:
            self.logger.warning(
                f"{method} {url} returned null - this may cause TypeError "
                f"in generated code expecting a list or object"
            )
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        self.logger.debug(
            f"{method} {url} JSON parse failed: {type(e).__name__}: {e}"
        )
```

## Configuration

### Environment Variables

```bash
# Set global log level
export LOG_LEVEL=DEBUG

# Enable detailed HTTP logging
export HTTPX_LOG_LEVEL=DEBUG
export HTTPCORE_LOG_LEVEL=DEBUG
```

### Programmatic Configuration

```python
import logging
from stocktrim_public_api_client import StockTrimClient

# Enable DEBUG logging for the client
logging.getLogger("stocktrim_public_api_client").setLevel(logging.DEBUG)

# Enable DEBUG logging for HTTP layer
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)

# Create client (inherits logger configuration)
client = StockTrimClient()
```

## Common Debugging Scenarios

### Investigating "NoneType has no len()" Error

**Problem**: Getting `TypeError: object of type 'NoneType' has no len()` when calling a
list endpoint

**Solution**: Enable DEBUG logging to see what the API actually returned

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient() as client:
    # This will now log the raw response body
    orders = await client.purchase_orders_v2.get_all_paginated(status="Draft")
```

**Expected DEBUG output**:

```
DEBUG GET /api/V2/PurchaseOrders?status=Draft -> 200 (150ms)
DEBUG Response body: null (JSON null)
```

**Root Cause**: The API returned `null` instead of an empty array `[]`, and the
generated code tried to iterate over `None`:

```python
# Generated code (buggy)
_response_200 = response.json()  # Returns None
for item in _response_200:  # TypeError: 'NoneType' object is not iterable
    ...
```

**Fix Options**:

1. **Client-side** (defensive): Check for None in generated code
1. **Server-side** (proper): Fix API to return `[]` instead of `null`
1. **Helper-side** (workaround): Convert None to `[]` in helper methods (already
   implemented)

### Investigating 404 Errors

**Problem**: Getting 404 errors but not sure why

**Solution**: ERROR level automatically logs the response body

```python
# No special configuration needed - ERROR level is always logged
async with StockTrimClient() as client:
    product = await client.products.get_by_id(999999)
```

**Expected ERROR output**:

```
ERROR Client error 404 for GET /api/Products/999999
ERROR Response: {"type":"about:blank","title":"Not Found","status":404,"detail":"Product not found"}
```

### Enhanced Parsing Error Logging

**Feature**: Intelligent error logging when TypeErrors, ValueErrors, or other parsing
errors occur

**How it works**:

- When a parsing error occurs, the client automatically inspects the response
- For TypeErrors: Identifies and lists all null fields that may have caused the issue
- For other errors: Shows response excerpts for debugging
- **Zero overhead**: Only runs when errors actually occur

**Example - Automatic TypeError debugging**:

```python
from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient() as client:
    # If this raises a TypeError due to null fields, enhanced logging activates
    orders = await client.purchase_orders_v2.get_all()
```

**Example ERROR output** (automatically generated):

```
ERROR TypeError during parsing for GET /api/V2/PurchaseOrders
ERROR TypeError: object of type 'NoneType' has no len()
ERROR Found 3 null field(s) in response:
ERROR   - orderDate
ERROR   - fullyReceivedDate
ERROR   - supplier.supplierName
ERROR
ERROR Possible fixes:
ERROR   1. Add fields to NULLABLE_FIELDS in scripts/regenerate_client.py and regenerate
ERROR      - For scalar/date fields: script adds 'nullable: true'
ERROR      - For object references: script uses 'allOf' with 'nullable: true' (OpenAPI 3.0 limitation)
ERROR   2. Handle null values defensively in helper methods
ERROR
ERROR See: docs/contributing/api-feedback.md#nullable-arrays-vs-optional-fields
```

**How to use it in helper methods**:

Helper methods can catch parsing errors and use the transport's logging:

```python
try:
    order = PurchaseOrderResponseDto.from_dict(response.json())
except (TypeError, ValueError, AttributeError) as e:
    # Log detailed error information with null field detection
    self.client.error_logging_transport.log_parsing_error(e, response, request)
    raise  # Re-raise the original error
```

This provides developers with immediate, actionable debugging information:

- Which specific fields are null
- The full error message and type
- Response excerpts for context
- No need to manually enable DEBUG logging or inspect responses

## Best Practices

### For Library Users

1. **Start with INFO level** in production
1. **Enable DEBUG only when investigating issues** (generates significant log volume)
1. **Use structured logging** to capture context in production logs
1. **Set up log rotation** to prevent disk space issues with DEBUG logging

### For Library Developers

1. **Never log sensitive data** (API keys, passwords, PII) at any level
1. **Log at appropriate levels**:
   - DEBUG: Everything needed to debug issues
   - INFO: Normal successful operations
   - WARNING: Unexpected but handled situations
   - ERROR: Failures that need attention
1. **Include context**: method, URL, status code, timing
1. **Truncate response bodies** to prevent log spam (default: 200 chars)
1. **Make logs searchable**: use consistent formats and include request IDs when
   available

## Future Enhancements

1. **Request ID tracking**: Propagate request IDs through the call chain for distributed
   tracing
1. **Metrics integration**: Export timing and error rate metrics to Prometheus/StatsD
1. **Sampling**: Log only a percentage of successful requests at DEBUG level in
   high-throughput scenarios
1. **Response body filtering**: Allow configuration of which endpoints to log response
   bodies for
1. **Structured logging**: Use structlog for machine-readable JSON logs in production

## Implementation Status

- ✅ ERROR logging for 4xx client errors with response details
- ✅ ERROR logging for 5xx server errors with response details
- ✅ INFO logging for successful 2xx responses with timing
- ✅ DEBUG logging for successful 2xx responses with body excerpts
- ✅ DEBUG logging for request details with sanitized headers
- ✅ **Enhanced ERROR logging for parsing errors** (TypeErrors, ValueErrors, etc.)
  - Automatically identifies null fields that may have caused TypeErrors
  - Shows response excerpts for other parsing errors
  - Only activates when errors actually occur (zero performance overhead in normal
    operation)
- ✅ Automatic retry logging at WARNING level (from httpx_retries)
- ✅ Request timing information included in all log messages
- ✅ Privacy-first: Auth headers excluded from DEBUG logs

## Related Documentation

- [Transport Layer Architecture](transport.md) - How the HTTP transport layer works
- [Error Handling](../user-guide/error-handling.md) - How to handle API errors
- [Contributing](../contributing/development.md) - Development setup and testing
