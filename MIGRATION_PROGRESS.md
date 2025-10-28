# Migration Progress: Katana Patterns → StockTrim

**Status**: 🟡 In Progress (3/16 commits complete - 19% done) **Branch**: `main`
**Started**: 2025-10-28 **Last Updated**: 2025-10-28

## Overview

Migrating infrastructure and library improvements from `katana-openapi-client` to
`stocktrim-openapi-client`. This is a **greenfield migration** with no backward
compatibility concerns (v0.1.0 Beta).

## Objectives

1. **Build System**: Migrate from Poetry → UV workspace with Hatchling
1. **Transport Layer**: Implement sophisticated resilience patterns (retries,
   pagination, error logging)
1. **Utilities**: Add response unwrapping and typed exception hierarchy
1. **Helpers**: Create domain helper classes for ergonomic API access
1. **Testing**: Comprehensive fixture library and mock patterns
1. **Documentation**: Migrate from Sphinx → MkDocs Material with ADRs
1. **MCP Server**: Create "hello world" stub that verifies StockTrim connection
1. **CI/CD**: Enhanced workflows with security scanning and dual-package releases

## Key Decisions

- ✅ **Wholesale UV migration** - Clean break from Poetry
- ✅ **Break everything** - No compatibility preservation, v0.1.0 greenfield
- ✅ **MkDocs Material** - Modern documentation
- ✅ **One PR, multiple commits** - Atomic but organized
- ✅ **MCP "hello world"** - Minimal stub server with connection verification
- ✅ **No cruft** - Clean, opinionated implementations

______________________________________________________________________

## Progress Tracker

### ✅ Phase 1: Build System & Tooling (COMPLETE)

#### ✅ Commit 1: Migrate to UV workspace with Hatchling

**Status**: Committed (`4d47f54`), Pushed **Files Changed**: 4 files (+2225/-2719 lines)

**Changes**:

- Replaced Poetry with UV workspace configuration
- Updated `pyproject.toml`:
  - Build backend: `poetry.core.masonry.api` → `hatchling.build`
  - Added `[tool.uv.workspace]` with members: `[".", "stocktrim_mcp_server"]`
  - Added `[tool.hatch.build.targets.wheel]` configuration
  - Updated dependencies to katana versions
  - Added `httpx-retries>=0.4.3,<0.5.0`
  - Updated `ruff>=0.12.4,<0.13`
  - Added `docs` extras with MkDocs Material dependencies
  - Updated semantic release: `tag_format = "client-v{version}"`
  - Added `validate-openapi-redocly` task
- Created `stocktrim_mcp_server/pyproject.toml` (minimal package)
- Removed `poetry.lock`
- Generated `uv.lock` (unified workspace lockfile)
- Updated poethepoet help message: `poetry run poe` → `uv run poe`

**Verification**:

```bash
uv sync --all-extras  # Should complete successfully
uv run poe help       # Should display task list
```

#### ✅ Commit 2: Update code quality tooling

**Status**: Committed (`56f0c92`), Pushed **Files Changed**: 2 files (+162/-12 lines)

**Changes**:

- Updated `.pre-commit-config.yaml`:
  - Added `--allow-multiple-documents, --unsafe` to check-yaml (for OpenAPI specs)
  - Added CHANGELOG.md exclusion to mdformat
  - Added local pytest hook: `bash -c '~/.local/bin/uv run poe test'`
- Updated `.gitignore`:
  - Added `.ruff_cache/` exclusion
  - Cleaned up debug file patterns
  - Better organization and comments
- `.yamllint.yml` already correctly configured (no changes)

**Verification**:

```bash
uv run pre-commit run --all-files  # All hooks should pass
```

#### ✅ Commit 3: Add devcontainer setup

**Status**: Committed (`302fd30`), Pushed **Files Changed**: 4 files (+344 lines)

**Changes**:

- Created `.devcontainer/devcontainer.json`:
  - Python 3.13 base image
  - Features: Git, GitHub CLI, Node.js LTS
  - VS Code extensions: Python, Ruff, Copilot, Docker, YAML
  - Auto-format on save with Ruff
  - pytest integration
  - Port 8000 forwarded for MCP server
  - Resource requirements: 4 CPU, 8GB RAM, 32GB storage
- Created `.devcontainer/oncreate.sh` (prebuild caching)
- Created `.devcontainer/setup.sh` (post-create finalization)
- Created `.devcontainer/README.md` (comprehensive documentation)

**Verification**:

```bash
# In VS Code: "Reopen in Container"
# After container starts:
uv run poe test
```

______________________________________________________________________

### 🟡 Phase 2: Core Client Architecture (IN PROGRESS)

#### ⏳ Commit 4: Rename types.py → client_types.py

**Status**: Not Started **Estimated Changes**: ~50+ files

**Plan**:

1. Rename `stocktrim_public_api_client/generated/types.py` →
   `stocktrim_public_api_client/generated/client_types.py`
1. Update all imports throughout codebase:
   - In `generated/api/` modules (20+ files)
   - In `generated/models/` modules (40+ files)
   - In `generated/client.py`
   - In `generated/errors.py`
1. Update `scripts/regenerate_client.py` to handle this transformation automatically
1. Verify: `uv run poe lint` should pass

**Why**: Avoids naming conflicts with Python's built-in `types` module and follows
katana convention.

#### ⏳ Commit 5: Rewrite StockTrimClient with katana transport pattern

**Status**: Not Started **Estimated Changes**: 1 file (~500 lines)

**Current Implementation**:

```python
# stocktrim_public_api_client/stocktrim_client.py (current)
class ResilientAsyncTransport(AsyncHTTPTransport):
    # Basic retry with tenacity
    # Custom auth injection
    # Simple error handling

class StockTrimClient:
    # Wrapper around AuthenticatedClient
    def __init__(...):
        self.client = AuthenticatedClient(...)
```

**Target Implementation** (StockTrim-specific - simpler than katana):

```python
# stocktrim_public_api_client/stocktrim_client.py (new)

class ErrorLoggingTransport(AsyncHTTPTransport):
    """Parse ErrorResponse/DetailedErrorResponse models, log details"""

def create_resilient_transport(...) -> AsyncHTTPTransport:
    """Factory for layered transport composition"""
    # AsyncHTTPTransport → ErrorLogging → Retry (5xx idempotent only)
    # NOTE: No rate limiting (429) - StockTrim doesn't have rate limits
    # NOTE: No pagination transport - StockTrim API doesn't paginate

class StockTrimClient(AuthenticatedClient):
    """Inherits from (not wraps) AuthenticatedClient"""
    # Lazy-loaded domain helpers as properties
    # Event hooks for observability (optional)
```

**StockTrim Simplifications**:

- ❌ No `RateLimitAwareRetry` - StockTrim doesn't have rate limits
- ❌ No `PaginationTransport` - StockTrim API doesn't paginate
- ℹ️ **Mostly direct resource access** - Few list APIs, primarily GET by ID
- ✅ Keep `ErrorLoggingTransport` - Better error visibility
- ✅ Basic retry on 5xx for idempotent methods (GET, HEAD, OPTIONS, TRACE)
- ✅ Custom auth header injection (api-auth-id, api-auth-signature)

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/katana_client.py`
  (lines 1-400+)

**Breaking Changes**:

- Old: `client = StockTrimClient(); api_client = client.client`
- New: `client = StockTrimClient()` (IS the authenticated client)

**Verification**:

```bash
uv run poe test  # Existing tests will fail (expected)
uv run poe lint  # Should pass
```

______________________________________________________________________

### 📋 Phase 3: Utilities & Helpers (PLANNED)

#### ⏳ Commit 6: Create utils.py with response unwrapping

**Status**: Not Started **Estimated Changes**: 1 new file (~300 lines)

**Plan**:

Create `stocktrim_public_api_client/utils.py` with:

1. **Typed Exception Hierarchy**:

   ```python
   class APIError(Exception): ...
   class AuthenticationError(APIError): ...  # 401
   class ValidationError(APIError): ...      # 422, includes validation_errors
   class RateLimitError(APIError): ...       # 429
   class ServerError(APIError): ...          # 5xx
   ```

1. **Response Unwrapping Functions**:

   - `unwrap(response)` - Raises typed exceptions on error
   - `unwrap_data(response)` - Extracts `.data` field from list responses
   - `is_success(response)` / `is_error(response)` - Status checks
   - `get_error_message(response)` - Extract error from response
   - `handle_response(response, on_success, on_error)` - Callback-based handling

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/utils.py`

**Verification**:

```bash
uv run poe lint
# Add unit tests for each function
```

#### ⏳ Commit 7: Create domain helper classes

**Status**: Not Started **Estimated Changes**: 6+ new files (~1000 lines)

**Plan**:

Create `stocktrim_public_api_client/helpers/` package for **all** StockTrim entities:

1. `helpers/base.py` - Base class with `_client` access
1. `helpers/products.py` - Products CRUD + search
1. `helpers/inventory.py` - Inventory/stock operations
1. `helpers/customers.py` - Customers CRUD + search
1. `helpers/suppliers.py` - Suppliers CRUD + search
1. `helpers/sales_orders.py` - Sales orders CRUD + status
1. `helpers/purchase_orders.py` - Purchase orders CRUD + status
1. `helpers/locations.py` - Locations management
1. `helpers/bill_of_materials.py` - BOM operations
1. `helpers/order_planning.py` - Order planning operations
1. `helpers/forecasting.py` - Forecasting operations
1. Additional helpers for any other major entity groups in the API

**Decision**: ✅ Create domain helpers for **all** entities in the StockTrim API to
provide ergonomic access patterns across the entire surface area.

**Pattern**:

```python
class Products(Base):
    async def list(self, **filters) -> list[Product]: ...
    async def get(self, id: str) -> Product: ...
    async def create(self, data: ProductCreate) -> Product: ...
    async def update(self, id: str, data: ProductUpdate) -> Product: ...
    async def delete(self, id: str) -> None: ...
    async def search(self, query: str, limit: int = 50) -> list[Product]: ...
```

**Wire into StockTrimClient**:

```python
class StockTrimClient(AuthenticatedClient):
    @cached_property
    def products(self) -> Products:
        return Products(self)

    @cached_property
    def inventory(self) -> Inventory:
        return Inventory(self)
    # etc.
```

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/helpers/`
  (base.py, products.py, materials.py, etc.)

**Verification**:

```bash
uv run poe lint
# Add unit tests with mocked transport
```

______________________________________________________________________

### 📋 Phase 4: Testing Infrastructure (PLANNED)

#### ⏳ Commit 8: Enhance testing infrastructure

**Status**: Not Started **Estimated Changes**: 1 file (~500 lines)

**Plan**:

Overhaul `tests/conftest.py` with comprehensive fixtures:

1. **Credential Fixtures**:
   - `mock_api_credentials`
   - `setup_test_env` (auto-used)
1. **Client Fixtures**:
   - `stocktrim_client`
   - `stocktrim_client_limited_pages`
   - `stocktrim_client_with_mock_transport`
1. **Transport Mocking**:
   - `mock_transport_handler`
   - `mock_transport`
   - `httpx.MockTransport` integration
1. **Response Fixtures**:
   - `mock_response`
   - `mock_paginated_responses`
   - `mock_rate_limited_response`
   - `mock_server_error_response`
1. **Helper Functions**:
   - `create_mock_paginated_response()`
   - `create_paginated_mock_handler()`

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/tests/conftest.py`

**Verification**:

```bash
uv run poe test-unit  # Should pass with new fixtures
```

#### ⏳ Commit 9: Update existing tests for new architecture

**Status**: Not Started **Estimated Changes**: ~10 test files

**Plan**:

Rewrite existing tests for new client pattern:

1. Update `tests/test_stocktrim_client.py`:
   - Remove wrapper pattern tests
   - Add transport layer tests (pagination, error logging, retry)
   - Test helper classes
   - Test event hooks
1. Update integration tests to use new client API
1. Add tests for `utils.py` functions
1. Add tests for helper classes

**Breaking Test Changes**:

- Old: `client.client.products.list(...)`
- New: `client.products.list(...)`

**Verification**:

```bash
uv run poe test-coverage  # Should achieve 85%+ coverage
```

______________________________________________________________________

### 📋 Phase 5: Scripts & Automation (PLANNED)

#### ⏳ Commit 10: Enhance regeneration script

**Status**: Not Started **Estimated Changes**: 1 file (~200 lines additional)

**Plan**:

Enhance `scripts/regenerate_client.py`:

1. **Add Redocly CLI Validation**:

   ```python
   # After openapi-spec-validator
   print("Validating with Redocly CLI...")
   subprocess.run(["npx", "@redocly/cli", "lint", "stocktrim-openapi.yaml"], check=True)
   ```

1. **Add Post-Processing Steps**:

   ```python
   # Fix types → client_types imports
   # Fix RST docstring formatting
   # Modernize Union types: Union[A, B] → A | B
   ```

1. **Add Auto-Fixes**:

   ```python
   subprocess.run(["ruff", "check", "--fix", "--unsafe-fixes", "stocktrim_public_api_client/generated/"], check=True)
   ```

1. **Add Streaming Output for Tests**

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/scripts/regenerate_client.py`

**Verification**:

```bash
uv run poe regenerate-client  # Should complete without errors
uv run poe validate-all       # Both validators should pass
```

______________________________________________________________________

### 📋 Phase 6: CI/CD Workflows (PLANNED)

#### ⏳ Commit 11: Update CI/CD workflows

**Status**: Not Started **Estimated Changes**: 4 workflow files

**Plan**:

1. **Update `.github/workflows/ci.yml`**:
   - Matrix strategy: Python 3.11, 3.12, 3.13, `fail-fast: false`
   - Concurrency control: `cancel-in-progress`
   - Split into separate jobs: `test`, `quality`
   - Switch to `astral-sh/setup-uv@v7`
1. **Update `.github/workflows/release.yml`**:
   - Dual-package support (client + MCP)
   - Commit-scoped releases: `(client)` and `(mcp)` scopes
   - Manual trigger with `force_publish` options
   - Docker multi-arch builds (amd64, arm64) for MCP server
   - Artifact attestations for provenance
1. **Update `.github/workflows/docs.yml`**:
   - Path-based triggers: `docs/**`, `mkdocs.yml`
   - MkDocs build and deploy
1. **Update `.github/workflows/security.yml`**:
   - Trivy vulnerability scanner (SARIF output)
   - Semgrep static analysis
   - Dependency review on PRs
   - Weekly scheduled scans

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/.github/workflows/`

**Verification**:

```bash
# Push to branch and verify workflows run
gh workflow list
gh run list
```

______________________________________________________________________

### 📋 Phase 7: Documentation Migration (PLANNED)

#### ⏳ Commit 12: Migrate to MkDocs Material

**Status**: Not Started **Estimated Changes**: ~15 files

**Plan**:

1. **Create `mkdocs.yml`**:

   ```yaml
   site_name: StockTrim OpenAPI Client
   theme:
     name: material
     features:
       - navigation.tabs.sticky
       - navigation.sections
       - content.code.copy
   plugins:
     - search
     - mkdocstrings[python]
     - gen-files
     - literate-nav
     - swagger-ui-tag
   markdown_extensions:
     - pymdownx.superfences: # mermaid diagrams
         custom_fences:
           - name: mermaid
             class: mermaid
     - pymdownx.tabbed
     - pymdownx.arithmatex
   ```

1. **Migrate Content**:

   - `docs/index.md` ← README.md
   - Keep `docs/STOCKTRIM_CLIENT_GUIDE.md` (update for new patterns)
   - Keep `docs/TESTING_GUIDE.md` (update for new fixtures)
   - Add `docs/COOKBOOK.md` (common usage patterns)
   - Keep `docs/CONTRIBUTING.md`, `docs/CODE_OF_CONDUCT.md`

1. **Remove Sphinx**:

   - Delete `docs/conf.py`
   - Remove sphinx dependencies from `pyproject.toml`
   - Update docs tasks in `pyproject.toml`:
     - `docs-build = "mkdocs build"`
     - `docs-serve = "mkdocs serve"`

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/mkdocs.yml`
- `/Users/dougborg/Projects/katana-openapi-client/docs/`

**Verification**:

```bash
uv run poe docs-build  # Should build to site/
uv run poe docs-serve  # Should serve on http://localhost:8000
```

#### ⏳ Commit 13: Add ADR documentation

**Status**: Not Started **Estimated Changes**: 7+ new files

**Plan**:

Create `docs/adr/` directory with Architecture Decision Records:

1. `0001-transport-layer-resilience.md` - Why transport-layer pattern over decorators
1. `0002-openapi-code-generation.md` - Why openapi-python-client
1. `0003-transparent-pagination.md` - Auto-pagination design
1. `0004-defer-observability-to-httpx.md` - Use httpx event hooks
1. `0005-response-unwrapping-utilities.md` - utils.py design
1. `0006-domain-helper-classes.md` - Ergonomic API access
1. `0007-migrate-from-poetry-to-uv.md` - Why UV workspace

**Template**:

```markdown
# ADR-XXXX: Title

**Status**: Accepted
**Date**: 2025-10-28
**Deciders**: Doug Borg

## Context

[Background and problem statement]

## Decision

[Chosen approach]

## Consequences

### Positive

- [Benefits]

### Negative

- [Tradeoffs]

## Alternatives Considered

- [Option 1]: [Why rejected]
```

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/docs/adr/`

**Verification**:

```bash
uv run poe docs-build  # ADRs should appear in navigation
```

______________________________________________________________________

### 📋 Phase 8: MCP Server & Finalization (PLANNED)

#### ⏳ Commit 14: Create MCP server stub package

**Status**: Not Started **Estimated Changes**: 5+ new files

**Plan**:

Create minimal MCP server in `stocktrim_mcp_server/`:

1. **Update `stocktrim_mcp_server/pyproject.toml`**:

   - Add proper dependencies (mcp, stocktrim-openapi-client)

1. **Create `src/stocktrim_mcp_server/__init__.py`**

1. **Create `src/stocktrim_mcp_server/server.py`**:

   ```python
   from mcp.server import Server
   from mcp.server.stdio import stdio_server
   from stocktrim_public_api_client import StockTrimClient

   @server.tool()
   async def verify_connection() -> dict:
       """Verify connection to StockTrim API."""
       async with StockTrimClient() as client:
           # Make a simple API call to verify auth
           response = await client.products.list(limit=1)
           return {"status": "connected", "message": "StockTrim API accessible"}

   @server.tool()
   async def get_product(product_id: str) -> dict:
       """Get product details by ID."""
       async with StockTrimClient() as client:
           product = await client.products.get(product_id)
           return product.to_dict()

   @server.tool()
   async def check_inventory(product_id: str) -> dict:
       """Check inventory levels for a product."""
       async with StockTrimClient() as client:
           inventory = await client.inventory.get_stock_levels(product_id)
           return inventory.to_dict()

   @server.tool()
   async def list_orders(order_type: str = "sales", limit: int = 10) -> list[dict]:
       """List recent orders (sales or purchase)."""
       async with StockTrimClient() as client:
           if order_type == "sales":
               orders = await client.sales_orders.list(limit=limit)
           else:
               orders = await client.purchase_orders.list(limit=limit)
           return [order.to_dict() for order in orders]

   async def main():
       async with stdio_server() as (read_stream, write_stream):
           await server.run(read_stream, write_stream)
   ```

1. **Create `README.md`**:

   - Installation instructions
   - Configuration for Claude Desktop
   - Available tools

1. **Create `Dockerfile`** (multi-arch):

   ```dockerfile
   FROM python:3.13-slim
   WORKDIR /app
   COPY . .
   RUN pip install uv && uv sync
   CMD ["uv", "run", "stocktrim-mcp-server"]
   ```

1. **Update `release.yml` workflow**:

   - Add Docker build for MCP server
   - Multi-arch: linux/amd64, linux/arm64

**Key Files to Reference**:

- `/Users/dougborg/Projects/katana-openapi-client/katana_mcp_server/`

**Verification**:

```bash
cd stocktrim_mcp_server
uv run stocktrim-mcp-server  # Should start and accept MCP protocol
# Test with MCP client
```

#### ⏳ Commit 15: Update root documentation

**Status**: Not Started **Estimated Changes**: 2 files

**Plan**:

1. **Rewrite `README.md`**:

   ```markdown
   # StockTrim OpenAPI Client

   ## Installation

   \`\`\`bash
   uv add stocktrim-openapi-client
   # or
   pip install stocktrim-openapi-client
   \`\`\`

   ## Quick Start

   \`\`\`python
   from stocktrim_public_api_client import StockTrimClient

   async with StockTrimClient() as client:
       # Domain helpers for ergonomic access
       products = await client.products.list()
       inventory = await client.inventory.get_stock_levels()

       # Or use generated API methods directly
       from stocktrim_public_api_client.generated.api.products import get_products
       response = await get_products.asyncio(client=client)
   \`\`\`

   ## Features

   - ✨ **Transport-Layer Resilience**: Auto-retry with exponential backoff
   - 🔄 **Smart Pagination**: Automatic page collection
   - 🎯 **Domain Helpers**: Ergonomic API access
   - 📝 **Typed Exceptions**: Clear error handling
   - 🧪 **Comprehensive Tests**: 85%+ coverage
   - 📦 **UV Workspace**: Modern monorepo structure

   ## MCP Server

   Install Claude Desktop integration:

   \`\`\`bash
   uv add stocktrim-mcp-server
   stocktrim-mcp-server  # Start MCP server
   \`\`\`

   ## Documentation

   Full documentation: https://dougborg.github.io/stocktrim-openapi-client/
   ```

1. **Update `CHANGELOG.md`**:

   - Document v0.1.0 → v0.2.0 migration notes
   - Breaking changes
   - New features

**Verification**:

```bash
uv run poe format-markdown-check
```

#### ⏳ Commit 16: Run full quality checks and fixes

**Status**: Not Started **Estimated Changes**: Various auto-fixes

**Plan**:

Run all quality checks and fix issues:

```bash
# 1. Sync workspace
uv sync --all-extras

# 2. Format code
uv run poe format

# 3. Auto-fix linting issues
uv run poe lint-ruff-fix

# 4. Run all linters
uv run poe lint  # mypy, ruff, yamllint - must pass

# 5. Run tests with coverage
uv run poe test-coverage  # Must achieve 85%+ on custom code

# 6. Validate OpenAPI
uv run poe validate-all  # Both validators must pass

# 7. Build documentation
uv run poe docs-build

# 8. Regenerate client (verify script works)
uv run poe regenerate-client

# 9. Run pre-commit on all files
uv run pre-commit run --all-files
```

**Validation Checklist**:

- [ ] UV workspace builds: `uv sync`
- [ ] All tests pass: Python 3.11, 3.12, 3.13
- [ ] Coverage ≥85% on custom code
- [ ] All linters pass: ruff, mypy, yamllint
- [ ] Pre-commit hooks pass
- [ ] Documentation builds: `uv run poe docs-build`
- [ ] MCP server starts: `uv run stocktrim-mcp-server`
- [ ] Regeneration works: `uv run poe regenerate-client`
- [ ] CI/CD workflows valid
- [ ] No Poetry remnants remain

______________________________________________________________________

## Project Context

### Sister Project Reference

**Katana OpenAPI Client**: `/Users/dougborg/Projects/katana-openapi-client`

This project serves as the reference implementation for all patterns being migrated.

### Key Architectural Patterns

#### 1. Transport-Layer Resilience (ADR-001)

**Why**: Retries and resilience at HTTP transport level (not decorators) means:

- ✅ Zero boilerplate for users
- ✅ Survives client regeneration
- ✅ Consistent behavior across all endpoints
- ✅ Type safety preserved
- ✅ httpx-native (no custom protocols)

**Implementation**: Simplified layered transport composition (StockTrim-specific)

```
AsyncHTTPTransport (httpx base)
  ↓
ErrorLoggingTransport (parse error models, detailed logging)
  ↓
RetryTransport (5xx on idempotent methods only)
```

**StockTrim Simplifications**:

- ❌ **No rate limiting** - StockTrim API doesn't have rate limits (no 429 handling)
- ❌ **No pagination transport** - StockTrim API doesn't use pagination headers
- ✅ **Basic retries** - 5xx errors on idempotent methods (GET, HEAD, OPTIONS, TRACE)
- ✅ **Error logging** - Parse and log detailed error responses
- ✅ **Custom auth** - Inject api-auth-id and api-auth-signature headers

#### 2. Domain Helper Classes (ADR-007)

**Why**: Generated API is verbose. Helpers provide ergonomic access:

```python
# Without helpers (generated API)
from stocktrim_public_api_client.generated.api.products import list_products
response = await list_products.asyncio_detailed(client=client, limit=50, offset=0)
if response.status_code == 200:
    products = response.parsed.data

# With helpers
products = await client.products.list(limit=50)
```

#### 3. Response Unwrapping Utilities (ADR-006)

**Why**: Consistent error handling across application:

```python
from stocktrim_public_api_client.utils import unwrap, ValidationError

try:
    product = unwrap(response)  # Raises typed exception on error
except ValidationError as e:
    print(f"Validation failed: {e.validation_errors}")
```

#### 4. UV Workspace (ADR-009, ADR-010)

**Why**: Monorepo for client + MCP server:

- Single lockfile (`uv.lock`)
- Shared dependencies
- Coordinated releases
- Faster CI/CD

### Breaking Changes Summary

**Client API**:

- Old: `client = StockTrimClient(); api_client = client.client`
- New: `client = StockTrimClient()` (inherits from AuthenticatedClient)

**Import Paths**:

- Old: `from stocktrim_public_api_client.generated.types import ...`
- New: `from stocktrim_public_api_client.generated.client_types import ...`

**Build System**:

- Old: `poetry install && poetry run poe <task>`
- New: `uv sync && uv run poe <task>`

**Documentation**:

- Old: Sphinx (`docs/_build/html`)
- New: MkDocs Material (`site/`)

______________________________________________________________________

## Development Commands

### Setup

```bash
# Clone and setup
git clone https://github.com/dougborg/stocktrim-openapi-client.git
cd stocktrim-openapi-client

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Sync dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Daily Development

```bash
# Run tests
uv run poe test
uv run poe test-coverage

# Linting and formatting
uv run poe format        # Auto-format
uv run poe lint          # Check
uv run poe fix           # Format + auto-fix

# Quick check (format + lint + test)
uv run poe check

# Full CI pipeline
uv run poe ci

# Documentation
uv run poe docs-build
uv run poe docs-serve    # http://localhost:8000
uv run poe docs-autobuild

# OpenAPI
uv run poe regenerate-client
uv run poe validate-all

# View all commands
uv run poe help
```

### Testing

```bash
# All tests (excluding slow docs tests)
uv run poe test

# With coverage
uv run poe test-coverage

# Unit tests only
uv run poe test-unit

# Integration tests only
uv run poe test-integration

# Documentation tests (CI only, 10-min timeout)
uv run poe test-docs
```

______________________________________________________________________

## File Structure

```
stocktrim-openapi-client/          # Root workspace
├── pyproject.toml                 # Main client package config
├── uv.lock                        # Unified lockfile
├── stocktrim_public_api_client/   # Client package
│   ├── __init__.py
│   ├── stocktrim_client.py        # Custom client (TO BE REWRITTEN)
│   ├── utils.py                   # (TO BE CREATED)
│   ├── helpers/                   # (TO BE CREATED)
│   │   ├── base.py
│   │   ├── products.py
│   │   ├── inventory.py
│   │   └── ...
│   └── generated/                 # Auto-generated code
│       ├── client.py
│       ├── types.py               # (TO BE RENAMED → client_types.py)
│       ├── errors.py
│       ├── api/                   # 20+ endpoint modules
│       └── models/                # 40+ model files
├── stocktrim_mcp_server/          # MCP server package
│   ├── pyproject.toml             # (TO BE UPDATED)
│   ├── README.md                  # (TO BE CREATED)
│   ├── Dockerfile                 # (TO BE CREATED)
│   └── src/stocktrim_mcp_server/  # (TO BE CREATED)
│       ├── __init__.py
│       └── server.py
├── tests/                         # Test suite
│   ├── conftest.py                # (TO BE ENHANCED)
│   ├── test_stocktrim_client.py   # (TO BE REWRITTEN)
│   └── ...
├── docs/                          # Documentation
│   ├── index.md                   # (TO BE CREATED - from README)
│   ├── STOCKTRIM_CLIENT_GUIDE.md  # (TO BE UPDATED)
│   ├── TESTING_GUIDE.md           # (TO BE UPDATED)
│   ├── COOKBOOK.md                # (TO BE CREATED)
│   └── adr/                       # (TO BE CREATED)
│       ├── 0001-transport-layer-resilience.md
│       └── ...
├── scripts/                       # Development scripts
│   └── regenerate_client.py       # (TO BE ENHANCED)
├── .github/workflows/             # CI/CD
│   ├── ci.yml                     # (TO BE UPDATED)
│   ├── release.yml                # (TO BE UPDATED)
│   ├── docs.yml                   # (TO BE UPDATED)
│   └── security.yml               # (TO BE UPDATED)
├── .devcontainer/                 # ✅ COMPLETE
│   ├── devcontainer.json
│   ├── oncreate.sh
│   ├── setup.sh
│   └── README.md
├── .pre-commit-config.yaml        # ✅ UPDATED
├── .gitignore                     # ✅ UPDATED
├── .yamllint.yml                  # ✅ CORRECT
└── mkdocs.yml                     # (TO BE CREATED)
```

______________________________________________________________________

## Testing Strategy

### Current State (v0.1.0)

- Basic unit tests for client initialization
- Simple integration test structure
- Coverage: ~60%

### Target State (v0.2.0)

- **Unit Tests**: Mock all external dependencies
  - Transport layer tests (pagination, retries, error logging)
  - Helper class tests
  - Utils function tests
- **Integration Tests**: Marked separately, require credentials
- **Documentation Tests**: Slow, CI-only, validate generated docs
- **Coverage Target**: 85%+ on custom code (excluding generated)

### Test Fixtures (from katana)

```python
# Credentials
@pytest.fixture
def mock_api_credentials():
    return {"auth_id": "test-id", "auth_signature": "test-sig"}

# Clients
@pytest.fixture
async def stocktrim_client(mock_api_credentials):
    async with StockTrimClient(**mock_api_credentials) as client:
        yield client

# Mock Responses
def create_mock_paginated_response(page: int, total_pages: int, data: list):
    return Response(
        status_code=200,
        headers={"X-Page": str(page), "X-Total-Pages": str(total_pages)},
        json={"data": data}
    )

# Mock Transport
@pytest.fixture
def mock_transport(mock_response):
    return httpx.MockTransport(lambda req: mock_response)
```

______________________________________________________________________

## CI/CD Strategy

### Current Workflows (v0.1.0)

1. **ci.yml**: Basic test matrix
1. **release.yml**: Semantic versioning
1. **docs.yml**: Sphinx build
1. **security.yml**: Basic scanning

### Target Workflows (v0.2.0)

1. **ci.yml** (Enhanced):

   ```yaml
   strategy:
     matrix:
       python-version: ["3.11", "3.12", "3.13"]
     fail-fast: false
   jobs:
     test: [format-check, lint, test-coverage, codecov]
     quality: [validate-openapi, docs-build, docs-tests]
   ```

1. **release.yml** (Dual-package):

   ```yaml
   # Client release on (client) commits
   # MCP release on (mcp) commits
   # Docker multi-arch builds for MCP
   # PyPI trusted publishing
   # Artifact attestations
   ```

1. **docs.yml** (MkDocs):

   ```yaml
   # Build MkDocs site
   # Deploy to GitHub Pages
   # Trigger on docs/** changes
   ```

1. **security.yml** (Enhanced):

   ```yaml
   # Trivy: Vulnerability scanning
   # Semgrep: Static analysis
   # Dependency review on PRs
   # Weekly scheduled scans
   ```

______________________________________________________________________

## Next Session Prep

### When Resuming Work

1. **Pull Latest Changes**:

   ```bash
   git pull origin main
   uv sync --all-extras
   ```

1. **Verify Current State**:

   ```bash
   uv run poe test    # Should pass
   uv run poe lint    # Should pass
   git log --oneline -5
   ```

1. **Start Next Commit**: See "Phase 2: Core Client Architecture" above

### Quick Reference Links

- **Katana Client**:
  `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/katana_client.py`
- **Katana Utils**:
  `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/utils.py`
- **Katana Helpers**:
  `/Users/dougborg/Projects/katana-openapi-client/katana_public_api_client/helpers/`
- **Katana Tests**: `/Users/dougborg/Projects/katana-openapi-client/tests/conftest.py`
- **Katana CI**: `/Users/dougborg/Projects/katana-openapi-client/.github/workflows/`
- **Katana MCP**: `/Users/dougborg/Projects/katana-openapi-client/katana_mcp_server/`

### StockTrim-Specific Considerations

**API Characteristics** (from OpenAPI spec analysis):

- ✅ **No rate limiting** - Can simplify retry logic (no 429 handling needed)
- ✅ **No pagination** - Can remove PaginationTransport entirely
- ✅ **Custom auth** - Uses `api-auth-id` (Tenant Id) + `api-auth-signature` (Tenant
  Name) headers
- ℹ️ **Mixed access patterns**:
  - Some GET endpoints for lists: `/api/Products`, `/api/Customers`, `/api/Suppliers`
  - Some GET by ID: `/api/Customers/{code}`, `/api/V2/PurchaseOrders/{referenceNumber}`
  - Some POST for bulk operations: `/api/SalesOrdersBulk`, `/api/SuppliersBulk`
  - Query parameter filtering: `/api/boms?productId=...&componentId=...`
- ✅ **Square integration** - Dedicated `/api/Square` endpoint for external system sync

**Domain Model** (from OpenAPI spec):

Core Entities:

- **Products** - GET (list), POST (create), DELETE
- **Customers** - GET (list), GET by code, PUT (update)
- **Suppliers** - GET (list), POST (create), DELETE + Bulk GET
- **Locations** - GET (list), POST (create) - has V2 version
- **Inventory** - POST (adjustments/updates)
- **Bill of Materials (BOMs)** - POST, GET (with filters), DELETE

Orders:

- **Sales Orders** - GET, POST, DELETE + Bulk operations (POST, PUT)
  - Special: `/api/SalesOrders/All` (delete all)
  - Special: `/api/SalesOrders/Range` (delete range)
  - By Location: `/api/SalesOrdersLocation` (DELETE)
- **Purchase Orders** - GET, POST, DELETE
  - V2: GET list, GET by referenceNumber
  - Order Plan: POST `/api/V2/PurchaseOrders/OrderPlan`

Operations:

- **Order Plan** - POST (generate order plan)
- **Run Forecast Calculations** - POST
- **Processing Status** - GET
- **Configuration** - GET by name
- **Inventory Management Settings** - GET, POST
- **InFlow** - POST (external integration)
- **Square** - POST (Square POS integration)

**Decisions Made**:

- ✅ **Domain helpers**: Create helpers for **all** StockTrim entities (not just the most
  common)
- ✅ **MCP server tools**: Implement `verify_connection`, `get_product`,
  `check_inventory`, `list_orders`
- ✅ **DTO vs Integration models**: Yes, document the dual model architecture
  - StockTrim has internal models (domain helpers) and external resource models (Square,
    etc.)
  - Similar pattern to Katana's multi-integration architecture

**Questions Still to Address**:

- [ ] Any StockTrim-specific error types beyond the base hierarchy?
- [ ] Documentation: Any StockTrim-specific guides needed beyond the standard set?
- [ ] Should MCP server expose create/update operations or stay read-only initially?

______________________________________________________________________

## Success Criteria

### PR Ready When:

- [ ] All 16 commits completed
- [ ] All tests pass (Python 3.11-3.13)
- [ ] Coverage ≥85% on custom code
- [ ] All linters pass (mypy, ruff, yamllint)
- [ ] Pre-commit hooks pass
- [ ] Documentation builds and looks good
- [ ] MCP server starts and accepts connections
- [ ] Regeneration script works
- [ ] CI/CD workflows validate
- [ ] README updated with new patterns
- [ ] CHANGELOG documents breaking changes

### Post-Merge:

- [ ] Tag release: `client-v0.2.0`
- [ ] Publish to PyPI (if enabled)
- [ ] Deploy documentation to GitHub Pages
- [ ] Close migration issue/PR

______________________________________________________________________

**Last Updated**: 2025-10-28 **Completed By**: Claude (Assistant) **Next Session**:
Continue with Commit 4 (types.py → client_types.py)
