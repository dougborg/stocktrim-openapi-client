# Development Setup

Guide for contributing to the StockTrim OpenAPI Client.

## Prerequisites

- Python 3.11 or higher
- uv package manager
- Git

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dougborg/stocktrim-openapi-client.git
cd stocktrim-openapi-client
```

### 2. Install uv

```bash
# Official installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --all-extras
```

### 4. Install Pre-commit Hooks

```bash
uv run poe pre-commit-install
```

## Development Workflow

### Code Quality Checks

```bash
# Run all checks (format, lint, test)
uv run poe check

# Individual checks
uv run poe format-check  # Check formatting
uv run poe lint          # Run linters
uv run poe test          # Run tests
```

### Auto-formatting

```bash
# Format all code
uv run poe format

# Format specific types
uv run poe format-python   # Python code only
uv run poe format-markdown # Markdown files only
```

### Testing

```bash
# Run all tests
uv run poe test

# Run with coverage
uv run poe test-coverage

# Run specific test types
uv run poe test-unit        # Unit tests only
uv run poe test-integration # Integration tests only
```

### Documentation

```bash
# Build documentation
uv run poe docs-build

# Serve documentation locally
uv run poe docs-serve

# Auto-rebuild on changes
uv run poe docs-autobuild
```

## Project Structure

```
stocktrim-openapi-client/
├── stocktrim_public_api_client/    # Main client package
│   ├── __init__.py
│   ├── stocktrim_client.py         # Main client class
│   ├── generated/                  # OpenAPI-generated code
│   ├── helpers/                    # Domain helper methods
│   └── utils/                      # Utility functions
├── stocktrim_mcp_server/           # MCP server package
│   └── src/
│       └── stocktrim_mcp_server/
│           ├── __init__.py
│           └── server.py           # MCP server implementation
├── tests/                          # Test suite
├── docs/                           # Documentation
├── scripts/                        # Utility scripts
└── pyproject.toml                  # Project configuration
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit files as needed. The pre-commit hooks will run automatically on commit.

### 3. Run Quality Checks

```bash
uv run poe check
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add my feature"
```

Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a pull request on GitHub.

## Regenerating the Client

If the OpenAPI spec changes:

```bash
# Regenerate client from spec
uv run poe regenerate-client

# Format the generated code
uv run poe format

# Run tests
uv run poe test
```

## Testing Guidelines

### Writing Tests

```python
import pytest
from stocktrim_public_api_client import StockTrimClient

@pytest.mark.asyncio
async def test_product_search():
    async with StockTrimClient() as client:
        products = await client.products.search("WIDGET")
        assert isinstance(products, list)
```

### Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.asyncio` - Async tests

### Mocking

```python
from unittest.mock import Mock, AsyncMock

async def test_with_mock():
    mock_client = Mock(spec=StockTrimClient)
    mock_client.products.find_by_code = AsyncMock(return_value=None)

    result = await mock_client.products.find_by_code("TEST")
    assert result is None
```

## Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
    """
    pass
```

### Adding Documentation

1. Write docstrings in code
2. Add markdown files to `docs/`
3. Update `mkdocs.yml` navigation
4. Build and preview: `uv run poe docs-serve`

## Troubleshooting

### Pre-commit Hooks Failing

```bash
# Run hooks manually
uv run poe pre-commit-run

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Test Failures

```bash
# Run tests with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_client.py::test_product_search
```

### Type Checking Errors

```bash
# Run type checker
uv run poe lint-ty

# Check specific file
uv run ty check stocktrim_public_api_client/stocktrim_client.py
```

## Release Process

Releases are automated via GitHub Actions:

1. Merge PR to `main`
2. GitHub Action runs tests
3. Semantic release calculates version
4. Creates git tag and GitHub release
5. Publishes to PyPI

## Next Steps

- [Code of Conduct](code-of-conduct.md) - Community guidelines
- [API Feedback](api-feedback.md) - Report StockTrim API issues
- [Architecture Overview](../architecture/overview.md) - Understand the codebase
