# MCP Server Observability

The StockTrim MCP Server is **observability-agnostic**. We don't ship a built-in
tracing layer or prescribe a logging format — operators choose their own stack
and plug it in via standard hooks.

This page documents what the server does emit, what it doesn't, and how to wire
in OpenTelemetry, structured logs, and HTTP-level tracing.

## What the server ships

- **Structured app logs** via [structlog](https://www.structlog.org/) for
  lifecycle events (startup, shutdown, auth errors, lifespan failures). Tunable
  via `LOG_LEVEL` and `LOG_FORMAT` env vars.
- **Native OpenTelemetry instrumentation** via FastMCP 3.x. The server emits
  per-tool spans with MCP semantic conventions (`mcp.tool.name`,
  `mcp.tool.duration`, `mcp.tool.success`) automatically — no decorator,
  no config in the codebase.
- **`ErrorLoggingTransport`** (in `stocktrim_public_api_client`, the underlying
  client library) logs API parse errors to capture real-API-vs-spec
  divergences. This is library-author concern, not operator concern, and is
  separate from the observability story below.
- **Response caching** via FastMCP's `ResponseCachingMiddleware` is wired in
  `server.py` with an in-memory store. Read tools cache for 5 minutes; resources
  cache for 60 seconds; mutating tools (every `create_*`/`delete_*`/`set_*`/
  `configure_*`/etc. surface) are excluded so cached entries are never returned
  for state changes. Operators can swap the in-memory backend for Redis/disk
  by overriding the middleware (see Caching below).

## What the server does NOT ship

- No bespoke tracing decorators (`@observe_tool`, `@observe_service` were
  removed in #147 — see the [v3 modernization tracking issue](https://github.com/dougborg/stocktrim-openapi-client/issues/154)).
- No prescribed log format for tool invocations.
- No prescribed metrics backend.

The intent: keep the package thin and let each operator wire in their preferred
stack — Datadog, Honeycomb, Grafana, plain logs, or nothing.

## Operator setup

### App-level structured logs

Set environment variables before starting the server:

| Variable     | Values                                          | Default  |
| ------------ | ----------------------------------------------- | -------- |
| `LOG_LEVEL`  | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO`   |
| `LOG_FORMAT` | `console` (human-readable), `json` (machine)    | `console` |

Example:

```bash
LOG_FORMAT=json LOG_LEVEL=INFO uvx stocktrim-mcp-server
```

Use `json` in production for log aggregators (Datadog, Splunk, Loki, etc.).

### Tool-boundary tracing (OpenTelemetry)

FastMCP 3.x emits OTel spans natively. Operators provide an exporter via
standard env vars — no code changes.

Install the OTel SDK with an OTLP exporter:

```bash
pip install 'fastmcp[telemetry]'
# or, equivalently:
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

Set the standard OTel env vars before starting the server:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otel-collector.your-org.com:4317"
export OTEL_SERVICE_NAME="stocktrim-mcp-server"
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production"
uvx stocktrim-mcp-server
```

Each tool call is a span with attributes for the tool name, duration, success
flag, and any FastMCP-attached context. Errors are recorded as span events.

For richer attributes (parameter values, custom tags), add a FastMCP
middleware — see below.

### Tool-boundary logging (FastMCP middleware)

Operators who want structured tool-call logs (rather than OTel traces) drop in
a middleware at server construction time. FastMCP ships
[`LoggingMiddleware`](https://gofastmcp.com/servers/middleware) and operators
can write their own:

```python
from fastmcp.server.middleware import LoggingMiddleware
from stocktrim_mcp_server.server import mcp

mcp.add_middleware(LoggingMiddleware(
    log_args=True,
    log_results=False,
    log_errors=True,
))
```

For Datadog/Sentry/etc., write a small middleware that calls the SDK directly
in `before_call` / `after_call` hooks.

### HTTP-level tracing (outbound StockTrim API calls)

The MCP server's tool calls eventually translate into HTTP requests against
StockTrim. To trace those at the wire level, instrument `httpx`:

```bash
pip install opentelemetry-instrumentation-httpx
```

Then enable instrumentation before starting the server (e.g., in a wrapper
script or via `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS`/auto-instrumentation):

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
HTTPXClientInstrumentor().instrument()
```

You'll get spans for every API call, attached to the parent tool span.

## Caching

The server ships with FastMCP's `ResponseCachingMiddleware` enabled by default,
backed by an in-memory store:

| Surface           | TTL     | Notes                                              |
| ----------------- | ------- | -------------------------------------------------- |
| `call_tool`       | 5 min   | Mutating tools (`create_*`, `delete_*`, etc.) excluded |
| `read_resource`   | 60 sec  | Resources are for discovery — favor freshness      |
| `list_tools/etc.` | 5 min   | FastMCP defaults                                   |

**Staleness window**: a successful mutation invalidates downstream reads only
when the next read miss exceeds the TTL. For most workflows the 5-minute window
is acceptable — pair-programmer agents typically don't mutate and re-read the
same entity within seconds. If your workload does, see "Tightening cache
freshness" below.

### Swapping the cache backend

To use Redis (multi-process or persistent across restarts):

```python
from key_value.aio.stores.redis import RedisStore
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from stocktrim_mcp_server.server import mcp

# Replace the default in-memory middleware before mcp.run()
mcp.middleware = [m for m in mcp.middleware if not isinstance(m, ResponseCachingMiddleware)]
mcp.add_middleware(ResponseCachingMiddleware(
    cache_storage=RedisStore(host="redis.internal", port=6379),
    # …existing call_tool_settings / read_resource_settings…
))
```

### Tightening cache freshness

Three options, ordered cheapest to most invasive:

1. **Lower TTLs** — pass smaller `ttl` values via `CallToolSettings(ttl=60)` etc.
2. **Add tools to `excluded_tools`** — any tool you list there is never cached.
3. **Disable response caching entirely** — remove the middleware after
   constructing `mcp` (see snippet above; just don't re-add it).

## Why this design

The MCP server is distributed via PyPI as `stocktrim-mcp-server`. Different
operators run it in different environments — solo dev workstations, hosted
infrastructure, CI agents. Prescribing a tracing backend or a structured-logging
format would force everyone to live with one team's choices.

By relying on:

- FastMCP's native OTel (an open standard, swappable backend),
- FastMCP's middleware system (composable, operator-owned),
- httpx's instrumentation surface (already covered by the OTel ecosystem),

…the server stays small, consumers stay flexible, and the open standards do
the heavy lifting.

## Reference

- [FastMCP telemetry docs](https://gofastmcp.com/servers/telemetry)
- [FastMCP middleware docs](https://gofastmcp.com/servers/middleware)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [opentelemetry-instrumentation-httpx](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/httpx/httpx.html)
