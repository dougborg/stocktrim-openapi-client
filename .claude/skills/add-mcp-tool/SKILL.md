---
name: add-mcp-tool
description: >-
  Add a new MCP tool to stocktrim_mcp_server, including the tool function,
  service layer, and test. Use when exposing an existing helper to AI clients
  via the Model Context Protocol.
allowed-tools: Read, Edit, Write, Bash(uv run pytest *), Bash(uv run poe check), Bash(git status), Bash(git diff *)
---

# /add-mcp-tool — Add a New MCP Tool

Add a tool function in `tools/`, a service in `services/`, and a test in `stocktrim_mcp_server/tests/`.

## PURPOSE

Surface an existing client helper as an MCP tool with proper Pydantic typing, service-layer indirection, and isolated tests.

## CRITICAL

- **Tools call services; services call helpers; helpers call `generated/`** — never bypass a layer.
- **Pydantic models for inputs/outputs** — FastMCP requires typed schemas; raw dicts are not acceptable.
- **MCP tests live in `stocktrim_mcp_server/tests/`** and run via `uv run poe test-mcp`. They're also part of `uv run poe check` (since #145), so a successful `check` covers both suites in one go.
- **Mock the StockTrim client at the service boundary** — don't hit real HTTP from MCP tests.

## ASSUMES

- The underlying helper already exists in `stocktrim_public_api_client/helpers/<domain>.py`. If not, run `/add-helper-method` first.
- The MCP server is FastMCP-based (see `stocktrim_mcp_server/src/stocktrim_mcp_server/server.py`).

## STANDARD PATH

### 1. Service layer

Edit (or create) `stocktrim_mcp_server/src/stocktrim_mcp_server/services/<domain>.py`. The service receives a `StockTrimClient` and exposes domain operations the tool will call:

```python
async def find_product_by_code(client: StockTrimClient, code: str) -> Product | None:
    return await client.products.find_by_code(code)
```

Keep services thin — they're a seam for testing and for swapping the client implementation if needed.

### 2. Tool function

Tools that return non-trivial data follow the `ToolResult` pattern: the public
wrapper renders a Jinja2 markdown template alongside the structured Pydantic
payload, so LLM clients see readable output and programmatic consumers still
get the typed data.

Edit `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/<domain>.py`:

```python
from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.tools.tool_result_utils import make_tool_result


class FindProductRequest(BaseModel):
    code: str = Field(description="Product code to look up")


class FindProductResponse(BaseModel):
    product: Product | None


async def _find_product_impl(
    request: FindProductRequest, ctx: Context
) -> FindProductResponse:
    """Pure business logic; returns the typed Pydantic model."""
    services = get_services(ctx)
    product = await services.products.find_by_code(request.code)
    return FindProductResponse(product=product)


async def find_product(request: FindProductRequest, ctx: Context) -> ToolResult:
    """Find a product by code; returns null if not found."""
    response = await _find_product_impl(request, ctx)
    return make_tool_result(
        response,
        template_path="foundation/products/find",
        # extra Jinja vars (response is auto-exposed as `response`):
        query_code=request.code,
    )
```

Then register with `mcp.tool()(find_product)` in the domain module's `register_tools` function.

### 2b. Markdown template

Templates live in a domain-grouped layout and use Jinja2 (`.md.j2`):

```
templates/foundation/products/find.md.j2
templates/workflows/urgent_orders/review.md.j2
```

Inside the template the response is exposed as `response` (don't use a shorter
alias — we picked descriptive over terse). Example:

```jinja
# Product lookup: {{ query_code }}

{% if response.product is none -%}
No product found for code `{{ query_code }}`.
{% else -%}
**{{ response.product.code }}** — {{ response.product.description or "(no description)" }}
{% endif %}
```

### 3. Test

Use `unwrap_tool_result` to recover the typed Pydantic model from the wrapper's
return — keeps assertions clean without poking at `result.structured_content`:

```python
from fastmcp.tools import ToolResult

from stocktrim_mcp_server.tools.tool_result_utils import unwrap_tool_result
from stocktrim_mcp_server.tools.<domain> import (
    FindProductRequest,
    FindProductResponse,
    find_product,
)


async def test_find_product_returns_product(mock_context):
    request = FindProductRequest(code="ABC")
    result = await find_product(request, mock_context)
    response = unwrap_tool_result(result, FindProductResponse)
    assert response.product is not None
    assert response.product.code == "ABC"


async def test_find_product_renders_markdown(mock_context):
    """Wrapper-level — verify the rendered markdown payload."""
    result = await find_product(FindProductRequest(code="ABC"), mock_context)
    assert isinstance(result, ToolResult)
    text = result.content if isinstance(result.content, str) else "\n".join(
        getattr(c, "text", str(c)) for c in result.content
    )
    assert "Product lookup: ABC" in text
```

Use the existing test fixtures from `stocktrim_mcp_server/tests/conftest.py`. If a fixture doesn't exist for what you need, add one — never duplicate setup across tests.

### 4. Run the tests

For a fast MCP-only loop while iterating:

```bash
uv run poe test-mcp                                   # all MCP tests
cd stocktrim_mcp_server && uv run pytest tests/test_tools/test_<domain>.py -x  # one file
```

When you're ready to commit, the full gate covers both client and MCP suites in one shot:

```bash
uv run poe check
```

ALL must pass. CLAUDE.md zero-tolerance applies — fix any pre-existing failures, don't ignore them.

### 5. Commit

Use scope `feat(mcp)` for MCP-side changes:

```bash
git add stocktrim_mcp_server/src/ stocktrim_mcp_server/tests/
git commit -m "feat(mcp): add <domain>.<tool> tool"
```

If the change touches both client helper and MCP tool, use two commits with scopes `feat(client)` and `feat(mcp)` so semantic-release can version each package independently.

## EDGE CASES

- [Tool needs to call multiple helpers] — Compose them in the service layer; the tool itself stays minimal.
- [Pydantic model duplicates a generated model] — Reexport the generated model in the tool's input/output rather than redefining. Avoid drift.
- [Tool is destructive (delete, mutate)] — Add a `confirm: bool = False` field on the input model and require explicit `True` to proceed. AI clients should not destroy data accidentally.

## RELATED

- `/add-helper-method` — Add the underlying helper first
- `domain-advisor` — Explains StockTrim's upsert/delete quirks
