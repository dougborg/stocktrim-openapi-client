# StockTrim API Client Guide

## Overview

The StockTrim OpenAPI Client is a production-ready Python library for interacting with
the StockTrim Inventory Management API. It implements transport-layer resilience for
automatic retries and custom authentication.

## Architecture Highlights

### Transport-Layer Resilience Pattern

Unlike traditional API clients that add retry logic as decorators or wrappers, this
client implements resilience at the HTTP transport level. This means **every API call**
automatically gets:

- Exponential backoff retries for network failures
- Custom authentication headers (`api-auth-id` and `api-auth-signature`)
- Consistent error handling

```python
# All these calls automatically get resilience features:
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products
from stocktrim_public_api_client.generated.api.customers import get_api_customers

async with StockTrimClient() as client:
    # Automatic retries + auth headers
    products = await get_api_products.asyncio_detailed(client=client)
    customers = await get_api_customers.asyncio_detailed(client=client)
```

### Multi-Integration API Architecture

StockTrim's API follows a unique multi-integration pattern with two types of models:

#### DTO Models (Native StockTrim Data)

Models with "Dto" suffix represent StockTrim's native data format:

- `CustomerDto` - StockTrim's internal customer format
- `ProductDto` - StockTrim's internal product format
- `SupplierDto` - StockTrim's internal supplier format

```python
# CustomerDto - StockTrim native format
{
    "code": "CUST001",
    "name": "John Doe",
    "street_address": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701"
}
```

#### Integration Models (Third-Party Formats)

Models without "Dto" suffix represent third-party integration formats:

- `Customer` - Square POS integration format
- `Product` - Third-party product integration format

```python
# Customer - Square POS integration format
{
    "given_name": "John",
    "family_name": "Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "version": 1,
    "address": {
        "address_line_1": "123 Main St",
        "locality": "Springfield",
        "administrative_district_level_1": "IL",
        "postal_code": "62701"
    }
}
```

This architecture allows StockTrim to:

1. Maintain clean native data structures
1. Support multiple POS/ERP integrations (Square, Shopify, etc.)
1. Transform data between formats as needed

## Authentication

StockTrim uses custom header authentication instead of bearer tokens:

### Required Headers

- `api-auth-id`: Your tenant ID
- `api-auth-signature`: Your tenant name

### Environment Setup

```bash
# .env file
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
```

### Client Initialization

```python
# Option 1: Environment variables (recommended)
async with StockTrimClient() as client:
    # Headers added automatically from environment
    pass

# Option 2: Direct initialization
async with StockTrimClient(
    api_auth_id="your_tenant_id",
    api_auth_signature="your_tenant_name"
) as client:
    pass
```

## API Endpoints

### Core Inventory Management

```python
from stocktrim_public_api_client.generated.api import (
    products, customers, suppliers, inventory,
    purchase_orders, sales_orders, locations
)

async with StockTrimClient() as client:
    # Products
    products_response = await products.get_api_products.asyncio_detailed(client=client)

    # Customers (both formats available)
    customers_dto = await customers.get_api_customers_dto.asyncio_detailed(client=client)
    customers_square = await customers.get_api_customers.asyncio_detailed(client=client)

    # Inventory levels
    inventory_response = await inventory.get_api_inventory.asyncio_detailed(client=client)

    # Orders
    po_response = await purchase_orders.get_api_purchaseorders.asyncio_detailed(client=client)
    so_response = await sales_orders.get_api_salesorders.asyncio_detailed(client=client)
```

### Working with Responses

```python
# Standard response pattern
response = await products.get_api_products.asyncio_detailed(client=client)

if response.status_code == 200:
    products_data = response.parsed
    # products_data is a list of Product objects
    for product in products_data:
        print(f"Product: {product.name}")
elif response.status_code == 404:
    print("No products found")
else:
    print(f"Error: {response.status_code}")
```

### Error Handling

The transport layer handles common errors automatically, but you should still handle
business logic errors:

```python
from stocktrim_public_api_client.generated.errors import UnexpectedStatus

try:
    response = await products.get_api_products.asyncio_detailed(client=client)

    if response.status_code == 200:
        # Success
        products = response.parsed
    elif response.status_code == 404:
        # No data (common in test environments)
        products = []
    else:
        # Unexpected status
        print(f"API returned {response.status_code}: {response.content}")

except Exception as e:
    # Network errors, auth failures, etc.
    print(f"Request failed: {e}")
```

## Data Models

### Understanding Model Types

#### DTO Models (StockTrim Native)

- Simple, flat structure optimized for StockTrim's internal operations
- Field names follow StockTrim conventions (code, name, street_address)
- Minimal nesting, focused on essential business data

#### Integration Models (Third-Party)

- Complex, nested structures matching external API formats
- Field names follow third-party conventions (given_name, family_name)
- Include metadata like timestamps, versions, external IDs

### Common Model Patterns

```python
# Working with CustomerDto (StockTrim native)
customer_dto = CustomerDto(
    code="CUST001",
    name="John Doe",
    email="john@example.com",
    phone="555-1234",
    street_address="123 Main St",
    city="Springfield",
    state="IL",
    postal_code="62701"
)

# Working with Customer (Square integration)
customer_square = Customer(
    given_name="John",
    family_name="Doe",
    email_address="john@example.com",
    phone_number="555-1234",
    address=Address(
        address_line_1="123 Main St",
        locality="Springfield",
        administrative_district_level_1="IL",
        postal_code="62701"
    )
)
```

## Best Practices

### 1. Use Environment Variables for Credentials

```python
# ✅ Good - credentials from environment
async with StockTrimClient() as client:
    pass

# ❌ Avoid - hardcoded credentials
async with StockTrimClient(
    api_auth_id="hardcoded_id",
    api_auth_signature="hardcoded_signature"
) as client:
    pass
```

### 2. Handle Both Success and Empty Responses

```python
# ✅ Good - handle 404 as normal case
response = await get_api_products.asyncio_detailed(client=client)
if response.status_code == 200:
    products = response.parsed
elif response.status_code == 404:
    products = []  # Empty is normal in test environments
```

### 3. Choose the Right Model Type

```python
# ✅ Use DTO models for StockTrim operations
customers_dto = await get_api_customers_dto.asyncio_detailed(client=client)

# ✅ Use integration models for third-party sync
customers_square = await get_api_customers.asyncio_detailed(client=client)
```

### 4. Use Context Managers

```python
# ✅ Good - automatic cleanup
async with StockTrimClient() as client:
    response = await some_api.asyncio_detailed(client=client)

# ❌ Avoid - manual cleanup required
client = StockTrimClient()
try:
    response = await some_api.asyncio_detailed(client=client)
finally:
    await client.close()
```

## Development Workflow

### Project Setup

```bash
# Clone and setup
git clone <repo>
cd stocktrim-openapi-client
uv sync --all-extras
uv run poe pre-commit-install
```

### Quality Checks

```bash
# Run all quality checks
uv run poe check

# Individual checks
uv run poe lint          # Type checking with mypy
uv run poe format-check  # Formatting validation
uv run poe test          # Run test suite
```

### Code Formatting

```bash
# Auto-format all code
uv run poe format

# Python-only formatting
uv run poe format-python
```

### Client Regeneration

```bash
# Regenerate from latest OpenAPI spec
uv run poe regenerate-client

# Always format after regeneration
uv run poe format
```

## Troubleshooting

### Authentication Issues

```python
# Verify credentials are loaded
import os
print(f"Auth ID: {os.getenv('STOCKTRIM_API_AUTH_ID')}")
print(f"Auth Signature: {os.getenv('STOCKTRIM_API_AUTH_SIGNATURE')}")
```

### API Response Debugging

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check raw response
response = await api_method.asyncio_detailed(client=client)
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content: {response.content}")
```

### Model Type Confusion

```python
# Check model type in IDE or runtime
from stocktrim_public_api_client.generated.models import Customer, CustomerDto

# Different field names indicate different integration formats
customer = Customer()  # Square format: given_name, family_name
customer_dto = CustomerDto()  # StockTrim format: code, name
```

## Performance Notes

### No Pagination Required

Unlike many APIs, StockTrim doesn't use pagination. The transport layer is simplified
compared to Katana's client since we don't need auto-pagination logic.

### No Rate Limiting

StockTrim's API doesn't implement rate limiting, so the transport layer focuses on retry
logic for network failures rather than rate limit handling.

### Connection Reuse

The client automatically reuses HTTP connections when used as a context manager:

```python
async with StockTrimClient() as client:
    # All these calls reuse the same connection
    response1 = await api1.asyncio_detailed(client=client)
    response2 = await api2.asyncio_detailed(client=client)
    response3 = await api3.asyncio_detailed(client=client)
```

## Integration Examples

### Syncing Customer Data Between Systems

```python
async def sync_customers():
    async with StockTrimClient() as client:
        # Get StockTrim native customers
        stocktrim_response = await get_api_customers_dto.asyncio_detailed(client=client)

        # Get Square integration customers
        square_response = await get_api_customers.asyncio_detailed(client=client)

        if stocktrim_response.status_code == 200:
            stocktrim_customers = stocktrim_response.parsed
            print(f"Found {len(stocktrim_customers)} StockTrim customers")

        if square_response.status_code == 200:
            square_customers = square_response.parsed
            print(f"Found {len(square_customers)} Square customers")
```

### Inventory Level Monitoring

```python
async def check_low_inventory():
    async with StockTrimClient() as client:
        inventory_response = await get_api_inventory.asyncio_detailed(client=client)

        if inventory_response.status_code == 200:
            inventory_items = inventory_response.parsed

            low_stock = [
                item for item in inventory_items
                if item.quantity_on_hand < item.reorder_point
            ]

            if low_stock:
                print(f"Low inventory alert: {len(low_stock)} items need reordering")
                for item in low_stock:
                    print(f"- {item.product_code}: {item.quantity_on_hand} remaining")
```

This guide provides comprehensive coverage of the StockTrim client architecture,
multi-integration patterns, and practical usage examples. The transport-layer resilience
pattern ensures reliable API interactions while the dual model system supports both
native StockTrim operations and third-party integrations.
