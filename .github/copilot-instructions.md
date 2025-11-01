# AI Agent Instructions for StockTrim OpenAPI Client

## Architecture Overview

This is a production-ready Python client for the StockTrim Inventory Management API
built with a **transport-layer resilience** approach. The key architectural decision is
implementing retry logic and custom authentication at the HTTP transport level rather
than as decorators or wrapper methods.

### Core Components

- **`stocktrim_public_api_client/stocktrim_client.py`**: Main client with custom retry
  transport (`IdempotentOnlyRetry`) - all resilience happens automatically
- **`stocktrim_public_api_client/generated/client.py`**: Generated OpenAPI client (base
  classes)
- **`stocktrim_public_api_client/generated/api/`**: Generated API endpoint modules
  (**don't edit directly**)
- **`stocktrim_public_api_client/generated/models/`**: Generated data models (**don't
  edit directly**)
- **`stocktrim_public_api_client/helpers/`**: Domain-specific helper classes (Products,
  Customers, Inventory, etc.)
- **`stocktrim_public_api_client/utils.py`**: Error handling utilities with typed
  exceptions
- **`stocktrim_public_api_client/client_types.py`**: Renamed from `types.py` during
  generation to avoid conflicts

### The Transport Layer Pattern

**Key insight**: Instead of wrapping API methods, we intercept at the httpx transport
level using `IdempotentOnlyRetry` (extends `httpx_retries.Retry`). This means ALL API
calls through `StockTrimClient` get automatic retries and authentication without code
changes in the generated client.

**Retry behavior**:

- Only retries 5xx server errors (not 4xx client errors)
- Only retries idempotent methods (GET, HEAD, OPTIONS, TRACE)
- POST/PUT/DELETE are NOT retried to prevent duplicate operations
- Uses exponential backoff via `httpx_retries`

**Error logging**: `ErrorLoggingTransport` logs 4xx client errors with full request
context for debugging.

```python
# Generated API methods work transparently with resilience:
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products
from stocktrim_public_api_client.utils import unwrap

async with StockTrimClient() as client:
    # This call automatically gets retries (5xx only, idempotent methods) and auth headers:
    response = await get_api_products.asyncio_detailed(client=client)
    products = unwrap(response)  # Raises typed exceptions on errors
```

### StockTrim-Specific Features

- **Custom Header Authentication**: Automatic `api-auth-id` and `api-auth-signature`
  headers
- **No Pagination**: StockTrim API doesn't use pagination, so transport is simplified
- **No Rate Limiting**: No evidence of rate limits in StockTrim API
- **Inventory Focus**: Optimized for inventory management operations

## Monorepo Structure

This is a **UV workspace** containing two packages:

- **`stocktrim-openapi-client`**: The main OpenAPI client library (root package)
- **`stocktrim-mcp-server`**: Model Context Protocol server for AI agents (in
  `stocktrim_mcp_server/`)

For MCP server development, see comprehensive docs in `docs/mcp-server/`:

- `overview.md` - Architecture and tool design
- `tools.md` - Available tools and usage
- `installation.md` - Setup instructions
- `claude-desktop.md` - Claude Desktop integration

### Automatic MCP Publishing

The GitHub Actions workflow automatically:

1. Publishes the client package when code changes
1. Updates the MCP server to depend on the new client version
1. Publishes the updated MCP server to PyPI
1. Both packages maintain synchronized versioning

## Development Workflows

### UV-Based Task Commands (Critical)

**IMPORTANT**: This project uses **UV** for dependency management, NOT Poetry.

```bash
# Format ALL files (Python + Markdown)
uv run poe format

# Type checking with ty (Astral's fast Rust-based type checker)
uv run poe lint

# Check formatting without changes
uv run poe format-check

# Python-only formatting
uv run poe format-python

# Quick development check (format-check + lint + test)
uv run poe check

# Auto-fix formatting and linting issues
uv run poe fix

# Full CI pipeline
uv run poe ci

# Regenerate OpenAPI client with automatic type fixing
uv run poe regenerate-client

# Show all available tasks
uv run poe help
```

### Pre-commit Hooks (ALWAYS Use)

Pre-commit hooks are **mandatory** for development - they automatically format and check
code before commits:

```bash
# Install pre-commit hooks (run once after clone)
uv run poe pre-commit-install

# Run pre-commit on all files (for testing)
uv run poe pre-commit-run

# Update pre-commit hook versions
uv run poe pre-commit-update
```

**CRITICAL**: Pre-commit hooks run automatically on `git commit` and will:

- Format code with ruff
- Fix trailing whitespace and file endings
- Check YAML syntax
- Validate large files and merge conflicts

**If pre-commit fails**: Fix the issues and commit again. Never use
`git commit --no-verify` to bypass hooks.

**Development Workflow with Pre-commit**:

1. Make code changes
1. `git add .` (stage changes)
1. `git commit -m "message"` (pre-commit runs automatically)
1. If pre-commit fails: fix issues, `git add .`, commit again
1. If pre-commit passes: commit succeeds

**Development Workflow with UV**:

1. Clone and setup: `uv sync --all-extras`
1. Install pre-commit: `uv run poe pre-commit-install`
1. Make changes and run: `uv run poe check`
1. Commit with conventional format: `git commit -m "feat: description"`

## StockTrim API Integration

### Environment Setup

```bash
# Create .env file with credentials
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
```

### API Authentication

StockTrim uses custom header authentication:

- `api-auth-id`: Tenant ID
- `api-auth-signature`: Tenant Name

The transport layer automatically adds these headers to all requests.

### Error Handling Pattern

The `utils.py` module provides typed exceptions that inherit from `APIError`:

- **`AuthenticationError`** (401): Invalid credentials
- **`PermissionError`** (403): Insufficient permissions
- **`NotFoundError`** (404): Resource not found
- **`ValidationError`** (400, 422): Invalid request data
- **`ServerError`** (5xx): Server-side errors

Use `unwrap()` to automatically raise typed exceptions:

```python
from stocktrim_public_api_client.utils import unwrap, NotFoundError

try:
    response = await get_api_products.asyncio_detailed(client=client)
    products = unwrap(response)  # Raises on error status
except NotFoundError:
    # Handle specific error type
    pass
```

### Helper Classes Architecture

Helpers in `stocktrim_public_api_client/helpers/` follow a consistent pattern:

1. **Inherit from `Base`**: Provides `self._client` access
1. **Wrap generated API calls**: Use `unwrap()` for error handling
1. **Provide convenience methods**: e.g., `find_by_code()`, `exists()`,
   `find_or_create()`
1. **Type annotations**: Full type hints for IDE support

Example helper pattern:

```python
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap

class Products(Base):
    async def find_by_code(self, code: str) -> ProductsResponseDto | None:
        """Find product by exact code match."""
        products = await self.get_all(code=code)
        return products[0] if products else None
```

**Critical Idempotent Pattern** - `find_or_create()`:

The `Customers.find_or_create()` method demonstrates the idempotent pattern used across
helpers:

```python
async def find_or_create(self, code: str, **defaults) -> CustomerDto:
    """Get customer by code, or create if doesn't exist (idempotent)."""
    try:
        return await self.get(code)
    except Exception:
        # Customer doesn't exist, create it
        new_customer = CustomerDto(code=code, **defaults)
        result = await self.update(new_customer)
        return result[0] if result else new_customer
```

This pattern ensures operations are **safe to retry** - calling multiple times with the
same parameters always results in the same state.

### Common API Endpoints

Based on the OpenAPI spec, main endpoints include:

- Products: `/api/Products`
- Customers: `/api/Customers`
- Suppliers: `/api/Suppliers`
- Inventory: `/api/Inventory`
- Purchase Orders: `/api/PurchaseOrders`
- Sales Orders: `/api/SalesOrders`
- Locations: `/api/Locations`

## Conventional Commits (REQUIRED)

This project uses semantic-release for automated versioning with **separate releases**
for client and MCP server packages. Commit message scopes determine which packages are
released.

### Commit Types

- **`feat:`** - New features (triggers minor version bump)
- **`fix:`** - Bug fixes (triggers patch version bump)
- **`docs:`** - Documentation changes (patch bump)
- **`style:`** - Code style changes (patch bump)
- **`refactor:`** - Code refactoring (patch bump)
- **`perf:`** - Performance improvements (patch bump)
- **`test:`** - Test changes (patch bump)
- **`chore:`** - Build/tooling changes (patch bump)
- **`ci:`** - CI/CD changes (patch bump)

### Commit Scopes for Multi-Package Releases

**IMPORTANT**: This monorepo has two packages that release independently based on commit
scope:

#### No Scope or `(client)` Scope → Releases CLIENT + MCP

Changes to the OpenAPI client trigger both package releases:

```bash
# These release BOTH packages:
git commit -m "feat: add retry logic for network failures"
git commit -m "fix: handle missing authentication headers"
git commit -m "feat(client): add new Products helper method"
git commit -m "fix(client): correct transport error handling"
```

**Why both?** When the client changes, the MCP server automatically picks up the new
client version and releases to keep them in sync.

#### `(mcp)` Scope → Releases MCP ONLY

Changes only to the MCP server:

```bash
# These release ONLY the MCP server:
git commit -m "feat(mcp): add purchase order generation tool"
git commit -m "fix(mcp): correct forecast data parsing"
git commit -m "docs(mcp): update tool documentation"
```

### Automatic Release Behavior

1. **Client changes** (`feat:`, `fix:`, `feat(client):`, etc.)

   - ✅ Releases `stocktrim-openapi-client` with new version
   - ✅ Automatically releases `stocktrim-mcp-server` with updated client dependency
   - Creates tags: `client-v*` and `mcp-v*`

1. **MCP-only changes** (`feat(mcp):`, `fix(mcp):`, etc.)

   - ✅ Releases `stocktrim-mcp-server` only
   - ❌ Does NOT release client
   - Creates tag: `mcp-v*`

1. **Documentation/CI changes** (`docs:`, `ci:`, etc.)

   - Depends on content - if in client code → client release
   - If in MCP server code → use `(mcp)` scope

### Commit Message Examples

```bash
# ✅ Client changes (releases both packages)
git commit -m "feat: add forecast API support"
git commit -m "fix: handle 401 authentication errors correctly"
git commit -m "refactor(client): simplify transport layer"

# ✅ MCP server changes (releases MCP only)
git commit -m "feat(mcp): add urgent order review workflow"
git commit -m "fix(mcp): correct product search pagination"
git commit -m "docs(mcp): update Claude Desktop setup guide"

# ✅ Multiple changes (releases both)
git commit -m "feat(client): add new Forecasts helper

Add Forecasts helper class with methods for accessing
order plans and forecast data.

Also update MCP server to expose these via tools."

# ❌ Bad commit messages
git commit -m "update code"              # Too vague, no type
git commit -m "feat add retries"         # Missing colon
git commit -m "new: add retries"         # Invalid type
git commit -m "feat(server): add tool"   # Wrong scope (use 'mcp')
```

### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in body:

```bash
# Breaking change in client (major version bump)
git commit -m "feat(client)!: change StockTrimClient authentication API"

# Breaking change in MCP server (major version bump)
git commit -m "feat(mcp)!: redesign tool input schemas"
```

### When to Use Each Scope

| Change Location                | Scope              | Example                   | Releases       |
| ------------------------------ | ------------------ | ------------------------- | -------------- |
| `stocktrim_public_api_client/` | none or `(client)` | `feat: add helper`        | Client + MCP   |
| `stocktrim_mcp_server/`        | `(mcp)`            | `feat(mcp): add tool`     | MCP only       |
| `.github/workflows/`           | `(ci)`             | `ci: update actions`      | None (usually) |
| Root docs                      | none or `(docs)`   | `docs: update README`     | Client + MCP   |
| MCP docs                       | `(mcp)`            | `docs(mcp): update guide` | MCP only       |

## Resolving GitHub Review Comments via API

When Copilot or reviewers leave comments on PRs, threads may need to be resolved before
merging (depending on branch protection settings).

### Process for Resolving Review Threads

1. **Query review threads to find unresolved ones**:

```bash
gh api graphql -f query='
query {
  repository(owner: "dougborg", name: "stocktrim-openapi-client") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 20) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first: 1) {
            nodes {
              body
            }
          }
        }
      }
    }
  }
}'
```

2. **Resolve each unresolved thread using GraphQL mutation**:

```bash
for thread_id in "PRRT_xxx" "PRRT_yyy"; do
  gh api graphql -f query="mutation {
    resolveReviewThread(input: {threadId: \"$thread_id\"}) {
      thread { id isResolved }
    }
  }"
done
```

**Important notes**:

- Use `PRRT_*` thread IDs (not `PRRC_*` comment IDs)
- The GraphQL API is required; the REST API doesn't support resolving review threads
- Only unresolved threads (`isResolved: false`) need to be resolved
- Outdated threads (`isOutdated: true`) can still be resolved if needed
- You need `repo` permissions (or write access) to resolve threads

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test API interactions with mocked responses
- **Mock external dependencies**: Never hit real APIs in tests (use httpx.MockTransport)
- **Fixtures in conftest.py**: Centralized test fixtures for consistency

### Common Testing Patterns

**1. Fixture-Based Client Creation**

```python
# Use pre-configured fixtures from conftest.py
def test_with_client(stocktrim_client):
    """Tests receive a configured client instance."""
    assert stocktrim_client is not None

async def test_with_async_client(async_stocktrim_client):
    """Async tests use the async fixture (auto-cleanup)."""
    products = await async_stocktrim_client.products.get_all()
```

**2. Mock Response Factory Pattern**

```python
def test_custom_response(create_mock_response):
    """Use factory fixture to create custom responses."""
    response = create_mock_response(
        status_code=200,
        json_data={"code": "WIDGET-001", "name": "Widget"},
        headers={"X-Custom": "value"}
    )
```

**3. HTTP Error Response Fixtures**

Pre-built fixtures for common error scenarios:

- `mock_authentication_error_response` - 401 Unauthorized
- `mock_validation_error_response` - 422 Unprocessable Entity
- `mock_not_found_response` - 404 Not Found
- `mock_server_error_response` - 500 Internal Server Error

**4. Environment Isolation**

The `clear_env` fixture (autouse) ensures clean environment between tests:

```python
def test_with_env_vars(mock_env_credentials):
    """Tests with environment variables automatically cleaned up."""
    # Environment vars set by fixture, cleared after test
    pass
```

**5. MockTransport Pattern**

```python
def test_with_mock_transport(stocktrim_client_with_mock_transport):
    """Client with httpx.MockTransport - no real network calls."""
    # All HTTP requests go through the mock handler
    pass
```

### Running Tests

```bash
# Run all tests (excludes slow docs tests)
uv run poe test

# Run with coverage
uv run poe test-coverage

# Run specific test types
uv run poe test-unit          # Unit tests only
uv run poe test-integration   # Integration tests only
uv run poe test-docs          # Slow documentation tests (CI only)
```

## Common Tasks

### Adding New Dependencies

```bash
# Add runtime dependency
uv add some-package

# Add development dependency
uv add --dev some-dev-package

# For monorepo packages, specify the package
uv add --package stocktrim-mcp-server some-package
```

### Updating Generated Client

```bash
# Regenerate from latest StockTrim OpenAPI spec
uv run poe regenerate-client

# Validate the generated code
uv run poe validate-openapi
```

**What happens during regeneration** (`scripts/regenerate_client.py`):

1. Downloads latest OpenAPI spec from StockTrim API
1. Fixes authentication (converts header params to securitySchemes)
1. **Marks nullable fields** (STEP 2.5):
   - Scalar/date fields: adds `nullable: true`
   - Object references: uses `allOf` with `nullable: true` (OpenAPI 3.0 workaround for
     `$ref`)
1. Validates spec using openapi-spec-validator and Redocly
1. Generates client with openapi-python-client
1. **Post-processing**:
   - Renames `types.py` → `client_types.py` (avoids Python stdlib conflicts)
   - Fixes all imports to use `client_types`
   - Adds type casting for `.from_dict()` methods
   - Modernizes Union types to `|` syntax
   - Fixes RST docstring formatting
1. Runs ruff auto-formatting
1. Validates with ty type checker

**NEVER manually edit generated code** - changes will be overwritten on regeneration.

### Code Quality Checks

```bash
# Full quality check
uv run poe check

# Individual checks
uv run poe lint-ty        # Type checking with ty
uv run poe lint-ruff      # Linting with ruff
uv run poe lint-yaml      # YAML validation
uv run poe format-check   # Format validation
```

## Architecture Decisions

### Why Transport-Layer Resilience?

1. **Simplicity**: No decorators or wrappers needed
1. **Transparency**: Generated API methods work unchanged
1. **Comprehensive**: ALL requests get resilience features
1. **Maintainability**: Resilience logic in one place

### Why No Pagination for StockTrim?

Unlike other APIs, StockTrim doesn't use pagination patterns:

- No `page`, `limit`, `offset` parameters
- Simple list endpoints return full results
- Keeps transport layer simpler and focused

### Why Custom Headers?

StockTrim uses `api-auth-id` and `api-auth-signature` instead of bearer tokens:

- Tenant-based authentication model
- Headers added automatically by transport
- No manual authentication needed

### Why Automatic Type Fixing?

The regeneration script automatically fixes type issues in generated code:

- Adds proper type casting for `.from_dict()` methods
- Manages imports (`cast`, `Mapping`) automatically
- Ensures strict type checking compliance with `ty`
- Eliminates manual type fixing after regeneration

## Dependencies Management

### Core Dependencies

- **httpx**: Modern HTTP client with async support
- **httpx-retries**: Retry logic with exponential backoff (base for
  `IdempotentOnlyRetry`)
- **tenacity**: Additional retry capabilities
- **python-dotenv**: Environment variable management
- **attrs**: Generated client models
- **python-dateutil**: Date/time handling
- **pydantic**: Type validation

### Development Dependencies

- **ruff**: Fast Python linter and formatter
- **ty**: Fast Rust-based Python type checker from Astral (strict mode enabled)
- **pytest** + **pytest-asyncio**: Testing framework with async support
- **pre-commit**: Git hooks for code quality
- **uv**: Modern Python package and project manager
- **poethepoet**: Task runner for development commands
- **mkdocs** + **mkdocs-material**: Documentation site generation
- **openapi-python-client**: Client code generation from OpenAPI spec
- **python-semantic-release**: Automated versioning and releases
