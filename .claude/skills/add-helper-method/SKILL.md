---
name: add-helper-method
description: >-
  Add a new ergonomic helper method to stocktrim_public_api_client/helpers/
  that wraps a generated API call. Includes test scaffolding and quality gate.
  Use when adding a domain operation (e.g., bulk upsert, find-by-code) that
  callers should reach for instead of the raw generated client.
allowed-tools: Read, Edit, Write, Bash(uv run pytest *), Bash(uv run poe check), Bash(uv run poe lint*), Bash(uv run poe format*), Bash(git status), Bash(git diff *)
---

# /add-helper-method — Add a Domain Helper

Add a new method to the appropriate `helpers/<domain>.py` module with a test that mocks the transport layer.

## PURPOSE

Expose a common operation as a typed, ergonomic helper instead of forcing callers to use the raw generated client.

## CRITICAL

- **Helpers wrap `generated/`, never bypass it** — call the generated `asyncio` (async) function, never `requests.get` or a custom HTTP path.
- **Tests must mock the transport layer**, not the helper. Use `httpx.MockTransport` so the auth + retry middleware runs.
- **404 → empty list pattern** — for collection-style "find by code" helpers, translate 404 to `[]`. This matches the StockTrim API quirk.
- **No `# noqa`, no `# type: ignore`** — refactor (e.g., into a dataclass) instead of suppressing.

## ASSUMES

- The generated client already exposes the underlying endpoint (run `/regenerate-client` first if not).
- The domain module exists (`helpers/products.py`, `helpers/purchase_orders.py`, etc.). For a new domain, copy the structure of an existing one.

## STANDARD PATH

### 1. Locate the generated call

```bash
grep -rn 'def asyncio' stocktrim_public_api_client/generated/api/<domain>/
```

Pick the function that matches the operation. Note its signature — the helper will adapt it.

### 2. Add the helper

Edit `stocktrim_public_api_client/helpers/<domain>.py`:

```python
async def find_by_code(self, code: str) -> Product | None:
    """Find a product by its code, or return None if not found."""
    try:
        return await api_products_get.asyncio(client=self._client, code=code)
    except UnexpectedStatus as exc:
        if exc.status_code == HTTPStatus.NOT_FOUND:
            return None
        raise
```

Conventions:

- Helper methods are `async`. They `await` the generated `asyncio` call.
- Return types use the generated model directly. No re-wrapping unless the domain demands it.
- Use `HTTPStatus.NOT_FOUND` (not magic `404`).
- Keep the helper thin — no business logic; it's an ergonomics layer.

### 3. Add the test

Edit `tests/test_helpers.py` (or a domain-specific test file). Match the existing pattern:

```python
async def test_find_by_code_returns_product(mock_api_credentials):
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={...}))
    async with StockTrimClient(transport=transport) as client:
        product = await client.products.find_by_code("ABC")
    assert product is not None
    assert product.code == "ABC"


async def test_find_by_code_returns_none_on_404(mock_api_credentials):
    transport = httpx.MockTransport(lambda req: httpx.Response(404))
    async with StockTrimClient(transport=transport) as client:
        product = await client.products.find_by_code("MISSING")
    assert product is None
```

### 4. Run the test, then full check

```bash
uv run pytest tests/test_helpers.py::test_find_by_code_returns_product -x
uv run pytest tests/test_helpers.py::test_find_by_code_returns_none_on_404 -x
uv run poe check
```

ALL must pass.

### 5. Commit

Use scope `feat(client)` for a new helper:

```bash
git add stocktrim_public_api_client/helpers/<domain>.py tests/test_helpers.py
git commit -m "feat(client): add <domain>.<method> helper"
```

## EDGE CASES

- [Endpoint not in generated client] — Run `/regenerate-client` first. The endpoint may not exist in the live spec; if so, file a feedback issue with StockTrim.
- [Helper needs to span multiple endpoints] — Compose existing helpers; don't reach into `generated/` again.
- [Method name shadows a built-in] — Rename (e.g., `list()` → `find_all()`). Don't `noqa` it.

## RELATED

- `/add-mcp-tool` — Wrap a helper as an MCP tool
- `domain-advisor` — Explains existing helper conventions
- `tests/test_helpers.py` — canonical mocking patterns
