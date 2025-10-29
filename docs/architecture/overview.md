# Architecture Overview

The StockTrim OpenAPI Client uses a transport-layer resilience pattern for robust API interactions.

## Design Philosophy

### Zero-Wrapper Approach

Unlike traditional API clients that wrap generated code with retry decorators, this client implements resilience at the HTTP transport level. This means:

- **No code changes** when regenerating the client from OpenAPI spec
- **Type safety preserved** throughout the entire stack
- **Performance optimized** by handling resilience at the lowest level
- **Transparent behavior** - all API calls automatically get resilience features

## Architecture Layers

```
┌─────────────────────────────────┐
│   Application Code              │
│   (Your async/await calls)      │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Helper Methods (Optional)     │
│   - Convenience wrappers        │
│   - Common patterns             │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Generated API Methods         │
│   - From OpenAPI spec           │
│   - Type-safe interfaces        │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   StockTrimClient               │
│   - Connection management       │
│   - Context management          │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   ResilientAsyncTransport       │
│   - Automatic retries           │
│   - Custom auth headers         │
│   - Exponential backoff         │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   HTTPX AsyncHTTPTransport      │
│   - HTTP/2 support              │
│   - Connection pooling          │
└─────────────────────────────────┘
```

## Key Components

### 1. StockTrimClient

The main client class that manages:
- Lifecycle (async context manager)
- Configuration (credentials, base URL)
- Helper method access
- Connection pooling

```python
async with StockTrimClient() as client:
    # All operations use the same connection pool
    pass
```

### 2. ResilientAsyncTransport

Custom HTTPX transport that provides:
- Automatic retry with exponential backoff
- Custom authentication headers
- Request/response logging
- Error handling

### 3. Helper Methods

Ergonomic wrappers for common operations:
- Simplified API calls
- Handle common patterns
- Reduce boilerplate
- Type-safe

### 4. Generated API

OpenAPI-generated code:
- Type-safe request/response models
- Async/await interfaces
- Full API coverage
- Automatically updated from spec

## Request Flow

1. **Application** calls API method
2. **Generated method** constructs request
3. **StockTrimClient** provides connection
4. **ResilientAsyncTransport** adds auth headers
5. **Transport** sends request
6. **On failure**: Automatic retry with backoff
7. **On success**: Parse and return response

## Error Handling Strategy

### Transport Layer (Automatic)

- Network failures → Retry with backoff
- 5xx errors → Retry with backoff
- 429 rate limit → Retry with backoff
- Timeout → Retry with backoff

### Application Layer (Manual)

- 4xx errors → Handle business logic
- 404 not found → Handle empty results
- Validation errors → Fix input data

## Benefits of This Architecture

### 1. Maintainability

- Regenerate client without losing resilience features
- Centralized retry logic
- Single point of configuration

### 2. Type Safety

- Full type checking from API call to response
- IDE autocomplete for all models
- Compile-time error detection

### 3. Performance

- Connection pooling
- HTTP/2 support
- Minimal overhead

### 4. Testability

- Mock at transport layer
- Test retry behavior independently
- Isolate business logic

## Design Decisions

### Why Transport-Layer Resilience?

**Problem**: Traditional retry decorators must be reapplied after regenerating the client.

**Solution**: Implement retries at the HTTP transport level, below the generated code.

**Result**: Resilience features survive client regeneration.

### Why Helper Methods?

**Problem**: Generated API is verbose and requires understanding HTTP details.

**Solution**: Provide ergonomic wrappers for common patterns.

**Result**: Easy-to-use high-level API without modifying generated code.

### Why Async/Await?

**Problem**: Inventory operations often require multiple API calls.

**Solution**: Use async/await for efficient concurrent operations.

**Result**: High-performance, modern Python code.

## Next Steps

- [Transport Layer](transport.md) - Deep dive into resilience implementation
- [Domain Helpers](helpers.md) - Helper method architecture
- [Client API](../api/client.md) - Complete API reference
