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
- **MCP tests live in `stocktrim_mcp_server/tests/`** and are NOT covered by `uv run poe check` (which only runs root `tests/`). You must run them separately.
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

Edit `stocktrim_mcp_server/src/stocktrim_mcp_server/tools/<domain>.py`:

```python
from pydantic import BaseModel, Field


class FindProductInput(BaseModel):
    code: str = Field(description="Product code to look up")


class FindProductOutput(BaseModel):
    product: Product | None


@mcp.tool()
async def find_product(input: FindProductInput, ctx: Context) -> FindProductOutput:
    """Find a product by code; returns null if not found."""
    client = await get_client(ctx)
    product = await find_product_by_code(client, input.code)
    return FindProductOutput(product=product)
```

Match the existing tool registration pattern in `tools/__init__.py`.

### 3. Test

Edit `stocktrim_mcp_server/tests/test_tools/test_<domain>.py`:

```python
async def test_find_product_returns_product(mock_client_factory):
    mock_client = mock_client_factory(products_find_by_code=AsyncMock(return_value=fake_product))
    result = await find_product(FindProductInput(code="ABC"), ctx=fake_ctx(mock_client))
    assert result.product == fake_product
```

Use the existing test fixtures from `stocktrim_mcp_server/tests/conftest.py`. If a fixture doesn't exist for what you need, add one — never duplicate setup across tests.

### 4. Run the tests

```bash
cd stocktrim_mcp_server && uv run pytest tests/test_tools/test_<domain>.py -x
```

Then run the root suite to make sure nothing client-side regressed:

```bash
cd .. && uv run poe check
```

ALL must pass on both. CLAUDE.md zero-tolerance applies — fix any pre-existing failures, don't ignore them.

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
