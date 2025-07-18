# AI Agent Instructions for StockTrim OpenAPI Client

## Architecture Overview

This is a production-ready Python client for the StockTrim Inventory Management API built with
a **transport-layer resilience** approach. The key architectural decision is
implementing retry logic and custom authentication at the HTTP transport level
rather than as decorators or wrapper methods.

### Core Components

- **`stocktrim_public_api_client/stocktrim_client.py`**: Main client with
  `ResilientAsyncTransport` - all resilience features happen here automatically
- **`stocktrim_public_api_client/client.py`**: Generated OpenAPI client (base classes)
- **`stocktrim_public_api_client/api/`**: Generated API endpoint modules (don't edit
  directly)
- **`stocktrim_public_api_client/models/`**: Generated data models (don't edit
  directly)

### The Transport Layer Pattern

**Key insight**: Instead of wrapping API methods, we intercept at the httpx transport
level. This means ALL API calls through `StockTrimClient` get automatic retries and
authentication without any code changes needed in the generated client.

```python
# Generated API methods work transparently with resilience:
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products

async with StockTrimClient() as client:
    # This call automatically gets retries and auth headers:
    response = await get_api_products.asyncio_detailed(client=client)
```

### StockTrim-Specific Features

- **Custom Header Authentication**: Automatic `api-auth-id` and `api-auth-signature` headers
- **No Pagination**: StockTrim API doesn't use pagination, so transport is simplified
- **No Rate Limiting**: No evidence of rate limits in StockTrim API
- **Inventory Focus**: Optimized for inventory management operations

## Development Workflows

### Poe Task Commands (Critical)

```bash
# Format ALL files (Python + Markdown)
poetry run poe format

# Type checking (mypy)
poetry run poe lint

# Check formatting without changes
poetry run poe format-check

# Python-only formatting
poetry run poe format-python

# Quick development check (format-check + lint + test)
poetry run poe check

# Auto-fix formatting and linting issues
poetry run poe fix

# Full CI pipeline
poetry run poe ci

# Regenerate OpenAPI client
poetry run poe regenerate-client

# Show all available tasks
poetry run poe help
```

### Pre-commit Hooks (ALWAYS Use)

Pre-commit hooks are **mandatory** for development - they automatically format and check
code before commits:

```bash
# Install pre-commit hooks (run once after clone)
poetry run poe pre-commit-install

# Run pre-commit on all files (for testing)
poetry run poe pre-commit-run

# Update pre-commit hook versions
poetry run poe pre-commit-update
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

This project uses semantic-release for automated versioning. Follow these commit message conventions:

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

### Examples

```bash
# ✅ Good commit messages
git commit -m "feat: add retry logic for network failures"
git commit -m "fix: handle missing authentication headers"
git commit -m "docs: update API usage examples"
git commit -m "refactor: simplify transport error handling"

# ❌ Bad commit messages
git commit -m "update code"           # Too vague, no type
git commit -m "feat add retries"      # Missing colon
git commit -m "new: add retries"      # Invalid type
```

### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in body:

```bash
git commit -m "feat!: change authentication header format"
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components
- **Integration tests**: Test API interactions
- **Mock external dependencies**: Don't hit real APIs in tests

### Running Tests

```bash
# Run all tests
poetry run poe test

# Run with coverage
poetry run poe test-coverage

# Run specific test types
poetry run poe test-unit
poetry run poe test-integration
```

## Common Tasks

### Adding New Dependencies

```bash
# Add runtime dependency
poetry add some-package

# Add development dependency
poetry add --group dev some-dev-package
```

### Updating Generated Client

```bash
# Regenerate from latest StockTrim OpenAPI spec
poetry run poe regenerate-client

# Validate the generated code
poetry run poe check-generated-ast
```

### Code Quality Checks

```bash
# Full quality check
poetry run poe check

# Individual checks
poetry run poe lint-mypy      # Type checking
poetry run poe lint-ruff      # Linting
poetry run poe lint-yaml      # YAML validation
poetry run poe format-check   # Format validation
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

## Dependencies Management

### Core Dependencies

- **httpx**: Modern HTTP client with async support
- **tenacity**: Retry logic with exponential backoff
- **python-dotenv**: Environment variable management
- **attrs**: Generated client models
- **python-dateutil**: Date/time handling

### Development Dependencies

- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality
- **poetry**: Dependency and package management
