# MCP Server Logging

## Overview

The StockTrim MCP Server uses structured logging via
[structlog](https://www.structlog.org/) to provide machine-readable logs with rich
context for debugging, monitoring, and observability.

## Features

- **Structured Logging**: All logs include structured context (event name, parameters,
  timing)
- **Dual Format Support**: Console format for development, JSON format for production
- **Tool Observability**: Automatic tracking of tool invocations with timing and status
- **Service Layer Tracing**: Debug-level logging for service operations
- **Error Context**: Detailed error information with categorization and stack traces
- **Configuration via Environment**: Easy configuration using environment variables

## Configuration

### Environment Variables

Configure logging behavior using these environment variables:

#### `LOG_LEVEL`

Controls the verbosity of logging output.

- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default**: `INFO`
- **Example**: `LOG_LEVEL=DEBUG`

#### `LOG_FORMAT`

Controls the output format of logs.

- **Values**: `console`, `json`
- **Default**: `console`
- **Example**: `LOG_FORMAT=json`

### Console Format (Development)

Human-readable colored output optimized for terminal viewing:

```bash
LOG_FORMAT=console uv run stocktrim-mcp-server
```

**Example Output**:

```
2025-11-06T19:18:09.011824Z [info     ] logging_configured             [stocktrim_mcp_server] filename=logging_config.py func_name=configure_logging lineno=86 log_format=console log_level=INFO
2025-11-06T19:18:09.012131Z [info     ] server_starting                [stocktrim_mcp_server.server] filename=server.py func_name=main lineno=158 version=0.1.0
2025-11-06T19:18:10.123456Z [info     ] tool_invoked                   [observability] filename=observability.py tool_name=get_supplier params={'code': 'SUP-001'}
2025-11-06T19:18:10.234567Z [info     ] tool_completed                 [observability] filename=observability.py tool_name=get_supplier duration_ms=111.11 success=True
```

### JSON Format (Production)

Structured JSON output for log aggregation systems (e.g., CloudWatch, Elasticsearch,
Datadog):

```bash
LOG_FORMAT=json uv run stocktrim-mcp-server
```

**Example Output**:

```json
{"log_level": "INFO", "log_format": "json", "event": "logging_configured", "level": "info", "logger": "stocktrim_mcp_server", "timestamp": "2025-11-06T19:01:30.453842Z", "lineno": 86, "filename": "logging_config.py", "func_name": "configure_logging"}
{"version": "0.1.0", "event": "server_starting", "level": "info", "logger": "stocktrim_mcp_server.server", "timestamp": "2025-11-06T19:01:30.454106Z", "lineno": 158, "filename": "server.py", "func_name": "main"}
{"tool_name": "get_supplier", "params": {"code": "SUP-001"}, "event": "tool_invoked", "level": "info", "logger": "observability", "timestamp": "2025-11-06T19:01:31.234567Z", "lineno": 45, "filename": "observability.py", "func_name": "wrapper"}
{"tool_name": "get_supplier", "duration_ms": 111.11, "success": true, "event": "tool_completed", "level": "info", "logger": "observability", "timestamp": "2025-11-06T19:01:31.345678Z", "lineno": 53, "filename": "observability.py", "func_name": "wrapper"}
```

## Log Events

### Server Lifecycle Events

#### `logging_configured`

Server logging system initialized.

**Fields**:

- `log_level`: Configured log level (DEBUG, INFO, etc.)
- `log_format`: Output format (console, json)

#### `server_starting`

Server is starting up.

**Fields**:

- `version`: MCP server version

#### `server_initializing`

Server lifespan initialization beginning.

**Fields**:

- `base_url`: StockTrim API base URL

#### `client_initialized`

StockTrim API client successfully initialized.

**Fields**:

- `base_url`: API base URL
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum retry attempts

#### `server_ready`

Server is ready to accept requests.

#### `server_shutdown`

Server is shutting down gracefully.

#### `missing_configuration`

Required environment variable not found.

**Fields**:

- `variable`: Name of missing variable
- `message`: Help message

#### `authentication_error`

Authentication failed during initialization.

**Fields**:

- `error`: Error message
- `error_type`: Exception type

#### `initialization_error`

Unexpected error during server initialization.

**Fields**:

- `error`: Error message
- `error_type`: Exception type

### Tool Invocation Events

#### `tool_invoked`

MCP tool was called.

**Fields**:

- `tool_name`: Name of the tool
- `params`: Tool parameters (excluding ctx)

#### `tool_completed`

Tool execution completed successfully.

**Fields**:

- `tool_name`: Name of the tool
- `duration_ms`: Execution time in milliseconds
- `success`: Always `true` for this event

#### `tool_failed`

Tool execution failed with an error.

**Fields**:

- `tool_name`: Name of the tool
- `duration_ms`: Execution time before failure
- `error`: Error message
- `error_type`: Exception class name
- `success`: Always `false` for this event

### Service Layer Events (DEBUG level)

#### `service_operation_started`

Service layer operation beginning.

**Fields**:

- `service`: Service class name
- `operation`: Operation name (e.g., "get_product", "create_order")
- `params`: Operation parameters

#### `service_operation_completed`

Service operation completed successfully.

**Fields**:

- `service`: Service class name
- `operation`: Operation name
- `duration_ms`: Execution time in milliseconds
- `success`: Always `true`

#### `service_operation_failed`

Service operation failed.

**Fields**:

- `service`: Service class name
- `operation`: Operation name
- `duration_ms`: Execution time before failure
- `error`: Error message
- `error_type`: Exception class name
- `success`: Always `false`

## Best Practices

### Development

Use console format with INFO or DEBUG level:

```bash
LOG_LEVEL=DEBUG LOG_FORMAT=console uv run stocktrim-mcp-server
```

### Production

Use JSON format with INFO level for structured log aggregation:

```bash
LOG_LEVEL=INFO LOG_FORMAT=json uv run stocktrim-mcp-server
```

### Claude Desktop Configuration

Add logging configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "stocktrim": {
      "command": "uvx",
      "args": ["stocktrim-mcp-server"],
      "env": {
        "STOCKTRIM_API_AUTH_ID": "your-auth-id",
        "STOCKTRIM_API_AUTH_SIGNATURE": "your-signature",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "console"
      }
    }
  }
}
```

### Monitoring Tool Performance

Filter logs by event type to track tool performance:

**Console format**:

```bash
# View only tool invocations
uv run stocktrim-mcp-server 2>&1 | grep tool_invoked

# View only failed tools
uv run stocktrim-mcp-server 2>&1 | grep tool_failed
```

**JSON format**:

```bash
# Extract tool timing metrics
LOG_FORMAT=json uv run stocktrim-mcp-server 2>&1 | \
  jq 'select(.event == "tool_completed") | {tool: .tool_name, duration: .duration_ms}'

# Find slow tools (>1000ms)
LOG_FORMAT=json uv run stocktrim-mcp-server 2>&1 | \
  jq 'select(.event == "tool_completed" and .duration_ms > 1000)'

# Count errors by tool
LOG_FORMAT=json uv run stocktrim-mcp-server 2>&1 | \
  jq 'select(.event == "tool_failed") | .tool_name' | sort | uniq -c
```

## Privacy and Security

The logging system is designed with privacy and security in mind:

- **No Credentials**: API credentials are never logged
- **No PII**: Personal identifiable information is excluded from logs
- **Sanitized Parameters**: Tool parameters are logged but sensitive fields can be
  filtered
- **Structured Data**: Consistent structure makes it easy to audit what's being logged

## Observability Decorators

The MCP server provides decorators for adding observability to custom code:

### `@observe_tool`

Automatically track tool invocations:

```python
from stocktrim_mcp_server.observability import observe_tool

@observe_tool
async def my_custom_tool(request: Request, context: Context) -> Response:
    # Your tool logic
    return response
```

### `@observe_service(operation)`

Track service layer operations:

```python
from stocktrim_mcp_server.observability import observe_service

class MyService:
    @observe_service("get_data")
    async def get_data(self, id: str) -> Data:
        # Your service logic
        return data
```

## Troubleshooting

### No Logs Appearing

1. Check that stderr is not being suppressed
1. Verify LOG_LEVEL is set appropriately
1. Ensure structlog is installed: `uv sync`

### JSON Format Not Working

1. Verify LOG_FORMAT=json is set before server starts
1. Check that jq or json parser can parse the output
1. Some FastMCP output may still use console format

### Too Much Log Output

1. Set LOG_LEVEL=WARNING to reduce verbosity
1. Filter logs by event type in your log aggregation tool
1. Consider using service-specific log levels

## Future Enhancements

Planned improvements to logging:

- Correlation IDs for request tracing across distributed systems
- Metrics integration (Prometheus, StatsD)
- Log sampling for high-volume production environments
- Dynamic log level adjustment without restart
- PII detection and automatic redaction
