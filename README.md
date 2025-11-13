# StockTrim OpenAPI Client

A production-ready Python client library and MCP server for the
[StockTrim Inventory Management API](https://www.stocktrim.com/).

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/dougborg/stocktrim-openapi-client/actions/workflows/ci.yml/badge.svg)](https://github.com/dougborg/stocktrim-openapi-client/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dougborg/stocktrim-openapi-client/branch/main/graph/badge.svg)](https://codecov.io/gh/dougborg/stocktrim-openapi-client)
[![Security](https://github.com/dougborg/stocktrim-openapi-client/actions/workflows/security.yml/badge.svg)](https://github.com/dougborg/stocktrim-openapi-client/actions/workflows/security.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Client:
[![PyPI - Version](https://img.shields.io/pypi/v/stocktrim-openapi-client)](https://pypi.org/project/stocktrim-openapi-client/)

MCP:
[![PyPI - MCP Server](https://img.shields.io/pypi/v/stocktrim-mcp-server)](https://pypi.org/project/stocktrim-mcp-server/)

## Features

### Client Library

- **🎯 Domain Helpers**: Ergonomic wrapper methods for common operations (15+ convenience
  functions)
- **🔄 Transport-Layer Resilience**: Automatic retries with exponential backoff built
  into HTTP transport
- **⚡ Modern Python**: Fully async/await with comprehensive type hints (ty strict)
- **🔐 Custom Authentication**: Automatic handling of StockTrim `api-auth-id` and
  `api-auth-signature` headers
- **🛡️ Typed Exceptions**: Structured error handling (AuthenticationError,
  ValidationError, ServerError, etc.)
- **📦 OpenAPI Generated**: Always up-to-date with the latest StockTrim API

### MCP Server

- **🤖 AI Integration**: Natural language interface for Claude and other AI assistants
- **⚡ FastMCP**: High-performance Model Context Protocol implementation
- **🔧 Production Ready**: 43+ tools, 5 workflow prompts, and resource endpoints
- **🎯 Type-Safe**: Full Pydantic validation for all operations
- **🏗️ Service Architecture**: Clean service layer with dependency injection
- **🛡️ Safety Patterns**: User confirmation for destructive operations
- **📝 Well-Documented**: Comprehensive usage examples and troubleshooting

## Installation

### Client Library

```bash
# With UV (recommended)
uv add stocktrim-openapi-client

# With pip
pip install stocktrim-openapi-client

# With Poetry
poetry add stocktrim-openapi-client
```

### MCP Server

```bash
# With UV
uv add stocktrim-mcp-server

# With pip
pip install stocktrim-mcp-server
```

## Quick Start

### Using Domain Helpers (Recommended)

```python
from stocktrim_public_api_client import StockTrimClient

async with StockTrimClient(
    api_auth_id="your_tenant_id",
    api_auth_signature="your_tenant_name"
) as client:
    # Product operations
    product = await client.products.find_by_code("WIDGET-001")
    widgets = await client.products.search("WIDGET")
    exists = await client.products.exists("WIDGET-001")

    # Customer operations
    customer = await client.customers.get("CUST-001")
    customer = await client.customers.find_or_create(
        "CUST-002",
        name="New Customer",
        email="customer@example.com"
    )

    # Inventory operations
    await client.inventory.set_for_product(
        product_id="123",
        stock_on_hand=50.0,
        stock_on_order=100.0,
        location_code="WAREHOUSE-A"
    )
```

### Using Generated API Methods

```python
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products
from stocktrim_public_api_client.utils import unwrap

async with StockTrimClient(
    api_auth_id="your_tenant_id",
    api_auth_signature="your_tenant_name"
) as client:
    # Direct API call with automatic retries and auth
    response = await get_api_products.asyncio_detailed(client=client)

    # Unwrap response or raise typed exception
    products = unwrap(response)  # Raises AuthenticationError, ServerError, etc.
```

### MCP Server

```bash
# Set environment variables
export STOCKTRIM_API_AUTH_ID=your_tenant_id
export STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name

# Run server
uvx stocktrim-mcp-server
```

For Claude Desktop integration, see [MCP Server README](stocktrim_mcp_server/README.md).

## Domain Helpers

The client provides convenient helper classes that wrap the generated API:

### Products

- `find_by_code(code)` - Get product by exact code
- `search(code_prefix)` - Find products starting with prefix
- `exists(code)` - Check if product exists
- `get_all()` - List all products
- `create(...)` - Create new product
- `delete(product_id)` - Delete product

### Customers

- `get(code)` - Get customer by code
- `get_all()` - List all customers
- `exists(code)` - Check if customer exists
- `find_or_create(code, **defaults)` - Get or create customer (idempotent)
- `update(customer)` - Update customer

### Suppliers

- `find_by_code(code)` - Get supplier by code (handles API inconsistencies)
- `create_one(supplier)` - Create single supplier
- `exists(code)` - Check if supplier exists
- `get_all()` - List all suppliers
- `create([suppliers])` - Batch create suppliers
- `delete(code)` - Delete supplier

### Sales Orders

- `get_for_product(product_id)` - Get orders for specific product
- `delete_for_product(product_id)` - Delete all orders for product
- `get_all()` - List all orders
- `create(...)` - Create order
- `delete(...)` - Delete orders

### Purchase Orders

- `find_by_reference(reference_number)` - Get order by reference
- `exists(reference_number)` - Check if order exists
- `get_all()` - List all orders
- `create(...)` - Create order
- `delete(...)` - Delete orders

### Inventory

- `set_for_product(product_id, stock_on_hand, stock_on_order, ...)` - Set inventory
  levels
- `set(request)` - Batch set inventory

### Locations

- `get_all()` - List all locations
- `create(...)` - Create location

See [docs/user-guide/helper-methods.md](docs/user-guide/helper-methods.md) for complete
documentation.

## Error Handling

The client provides typed exceptions for structured error handling:

```python
from stocktrim_public_api_client.utils import (
    unwrap,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError
)

try:
    product = unwrap(response)
except AuthenticationError:
    print("Invalid credentials")
except ValidationError as e:
    print(f"Validation failed: {e.validation_errors}")
except NotFoundError:
    print("Product not found")
except ServerError as e:
    print(f"Server error: {e.status_code}")
```

## Configuration

### Environment Variables

```bash
# Required
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name

# Optional
STOCKTRIM_BASE_URL=https://api.stocktrim.com  # Default
```

### Programmatic Configuration

```python
async with StockTrimClient(
    api_auth_id="your_tenant_id",
    api_auth_signature="your_tenant_name",
    base_url="https://api.stocktrim.com",
    timeout=30.0,
    max_retries=5
) as client:
    # Use client
    pass
```

## Architecture

### Transport-Layer Resilience

Resilience features are implemented at the HTTP transport level:

- **Automatic retries** on 5xx errors for idempotent methods (GET, HEAD, OPTIONS, TRACE)
- **Exponential backoff** with jitter to prevent thundering herd
- **Error logging** with detailed response parsing
- **Custom authentication** injection without modifying generated code

This approach ensures:

- ✅ All generated API methods automatically get resilience features
- ✅ No code changes needed when regenerating from OpenAPI spec
- ✅ Type safety preserved throughout
- ✅ Optimal performance (resilience at lowest level)

### Domain Helpers

Helper classes provide:

- **Clear intent** with intuitive method names
- **API inconsistency handling** (e.g., single vs list returns)
- **Common patterns** for frequent workflows
- **Reduced boilerplate** for simple operations
- **Full type safety** with comprehensive hints

### MCP Server Architecture

The MCP server is built with a clean, maintainable architecture:

- **Service Layer**: Business logic separated from tool interfaces with dependency
  injection
- **Parameter Flattening**: MCP-compatible tool signatures while maintaining type safety
  (ADR 002)
- **User Confirmation Pattern**: Destructive operations require explicit confirmation
  via MCP elicitation (ADR 001)
- **Structured Logging**: Observability throughout with detailed operation tracking
- **Template System**: Consistent, formatted responses for forecast operations
- **Resource Discovery**: Read-only endpoints for context gathering without mutations

See [Architecture Decision Records](docs/architecture/decisions/) for detailed design
rationale.

## MCP Server Tools

The MCP server provides **43+ tools** organized into foundation tools and workflow
tools:

### Foundation Tools (27 functions)

Direct CRUD operations across all domains:

- **Products**: get, search, list, create, delete
- **Customers**: get, list, create
- **Suppliers**: get, list, create, delete
- **Inventory**: get, set
- **Sales Orders**: create, get, list, delete
- **Purchase Orders**: get, list, create, delete
- **Locations**: list, create
- **Planning**: run_order_plan, run_forecast
- **BOM**: list_boms, create_bom
- **Configuration**: get_configuration

### Workflow Tools (16 functions)

High-level business operations combining multiple API calls:

- **Forecast Management**: update_and_monitor, get_for_products, update_settings,
  manage_group
- **Urgent Orders**: review_requirements, generate_purchase_orders
- **Product Management**: configure_product
- **Supplier Management**: create_supplier_with_products

### MCP Prompts (5 workflow prompts)

Guided workflows for complex operations:

- **purchasing_workflow**: Comprehensive purchase order generation workflow
- **forecast_accuracy_review**: Analyze and improve forecast accuracy
- **supplier_performance_review**: Comprehensive supplier analysis
- **stockout_prevention**: Proactive inventory management and reordering
- **product_lifecycle_review**: Product performance and lifecycle analysis

### MCP Resources

Read-only discovery endpoints for context:

- **Foundation**: Products, customers, suppliers, locations, inventory
- **Reports**: inventory-status, urgent-orders, supplier-directory

Example conversation with Claude:

```
You: What products do we have starting with "WID"?
Claude: [uses search_products("WID")]
Found 3 products:
- WIDGET-001: Standard Widget ($10.00)
- WIDGET-002: Premium Widget ($15.00)
- WIDGET-SPECIAL: Custom Widget ($25.00)

You: Run the purchasing workflow to review urgent orders
Claude: [uses purchasing_workflow prompt]
Let me guide you through reviewing urgent orders and generating purchase orders...
```

See [stocktrim_mcp_server/README.md](stocktrim_mcp_server/README.md) for detailed usage.

## Code Quality & Testing

This project maintains high code quality standards with comprehensive tooling:

### Testing Infrastructure

- **50+ test files** covering client library and MCP server
- **Test categories**: unit, integration, docs markers for selective execution
- **pytest** with async support, coverage reporting, and mocking
- **Separate test suites** for client (17+ files) and MCP server (35+ files)
- **Code coverage tracking** with pytest-cov (terminal, HTML, and XML reports)

### Linting & Type Checking

- **Ruff**: Fast Python linter and formatter with comprehensive rule sets
- **ty**: Astral's strict type checker ensuring full type safety
- **yamllint**: YAML validation for configuration files
- **mdformat**: Markdown formatting with GFM and tables support

### Security Scanning

- **Trivy**: Vulnerability scanner (runs weekly and on PRs)
- **Semgrep**: Static analysis for security patterns (runs weekly and on PRs)
- **Dependency review**: Automated checks on pull requests
- Results uploaded to GitHub Security tab for tracking

### CI/CD Pipeline

- **Matrix testing**: Python 3.11, 3.12, 3.13 across all tests
- **Automated releases**: Semantic versioning with python-semantic-release
- **Documentation**: Auto-deployed to GitHub Pages on releases
- **Pre-commit hooks**: Full lint and test suite runs before commits
- **Codecov integration**: Coverage tracking and reporting

### Quality Commands

```bash
# Run full quality check suite
uv run poe check

# Individual checks
uv run poe format        # Format code with Ruff
uv run poe lint          # Lint with Ruff
uv run ty check          # Type check with ty
uv run poe test-coverage # Tests with coverage report
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/dougborg/stocktrim-openapi-client.git
cd stocktrim-openapi-client

# Install UV (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Common Tasks

```bash
# Run tests
uv run poe test

# Run linting
uv run poe lint

# Format code
uv run poe format

# Type check
uv run ty check

# Regenerate client from OpenAPI spec
uv run poe regenerate-client

# Build documentation
uv run poe docs-build

# Run all checks (format + lint + test)
uv run poe check
```

### Testing

```bash
# All tests
uv run poe test

# With coverage
uv run poe test-coverage

# Unit tests only
uv run poe test-unit

# Integration tests only
uv run poe test-integration
```

## Project Structure

```
stocktrim-openapi-client/
├── stocktrim_public_api_client/   # Client library
│   ├── stocktrim_client.py        # Main client with transport layer
│   ├── helpers/                   # Domain helper classes
│   │   ├── products.py
│   │   ├── customers.py
│   │   ├── suppliers.py
│   │   ├── sales_orders.py
│   │   ├── purchase_orders.py
│   │   ├── inventory.py
│   │   └── locations.py
│   ├── utils.py                   # Response unwrapping & exceptions
│   └── generated/                 # OpenAPI-generated code
│       ├── api/                   # API endpoint methods
│       ├── models/                # Data models
│       └── client.py              # Base client
├── stocktrim_mcp_server/          # MCP server package
│   └── src/stocktrim_mcp_server/
│       ├── server.py              # FastMCP server
│       └── tools/                 # MCP tool implementations
├── tests/                         # Test suite
├── scripts/                       # Development scripts
└── docs/                          # Documentation
```

## Documentation

- **Full Documentation**:
  [https://dougborg.github.io/stocktrim-openapi-client/](https://dougborg.github.io/stocktrim-openapi-client/)
- **Client Guide**: [docs/user-guide/client-guide.md](docs/user-guide/client-guide.md)
- **Helper Methods**:
  [docs/user-guide/helper-methods.md](docs/user-guide/helper-methods.md)
- **Testing Guide**: [docs/user-guide/testing.md](docs/user-guide/testing.md)
- **MCP Server**: [stocktrim_mcp_server/README.md](stocktrim_mcp_server/README.md)

## Contributing

Contributions are welcome! Please see:

- [Development Setup](#development) above
- [Code of Conduct](docs/contributing/code-of-conduct.md)
- [API Feedback](docs/contributing/api-feedback.md) - Constructive feedback for
  StockTrim developers

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for modern async HTTP
- Generated with
  [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
- MCP server built with [FastMCP](https://github.com/jlowin/fastmcp)
- Architecture patterns inspired by
  [katana-openapi-client](https://github.com/dougborg/katana-openapi-client)

## Support

- **Issues**:
  [GitHub Issues](https://github.com/dougborg/stocktrim-openapi-client/issues)
- **Source**: [GitHub Repository](https://github.com/dougborg/stocktrim-openapi-client)
- **StockTrim**: [www.stocktrim.com](https://www.stocktrim.com/)
