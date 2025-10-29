# Domain Helpers

Helper methods provide ergonomic wrappers around the generated API.

## Design Principles

### 1. Clear Intent

Method names clearly express their purpose:

```python
# ✅ Clear intent
product = await client.products.find_by_code("WIDGET-001")

# ❌ Less clear
response = await get_api_products.asyncio_detailed(client=client)
products = [p for p in response.parsed if p.code == "WIDGET-001"]
```

### 2. Handle Inconsistencies

Smooth over API quirks:

```python
# Helper handles single vs. list returns
customer = await client.customers.find_by_code("CUST-001")

# Instead of checking if result is list or single item
response = await get_api_customers.asyncio_detailed(...)
customers = response.parsed
customer = customers[0] if customers and len(customers) == 1 else None
```

### 3. Common Patterns

Implement frequently-used workflows:

```python
# Common pattern: search by prefix
widgets = await client.products.search("WIDGET")

# Instead of filtering manually
response = await get_api_products.asyncio_detailed(client=client)
widgets = [p for p in response.parsed if p.code.startswith("WIDGET")]
```

### 4. Optional Simplification

Reduce boilerplate for simple use cases:

```python
# Simple case
all_customers = await client.customers.list_all()

# Verbose alternative
response = await get_api_customers.asyncio_detailed(client=client)
all_customers = response.parsed if response.status_code == 200 else []
```

## Helper Architecture

### Base Helper Pattern

```python
class BaseHelper:
    def __init__(self, client: StockTrimClient):
        self.client = client

    async def _call_api(self, api_method, **kwargs):
        """Wrapper for API calls with error handling."""
        response = await api_method.asyncio_detailed(
            client=self.client,
            **kwargs
        )
        return response
```

### Domain-Specific Helpers

Each helper focuses on one domain:

- `ProductsHelper` - Product operations
- `CustomersHelper` - Customer operations
- `SuppliersHelper` - Supplier operations
- `SalesOrdersHelper` - Sales order operations
- `PurchaseOrdersHelper` - Purchase order operations
- `LocationsHelper` - Location/warehouse operations

## Common Methods

### `find_by_code(code: str)`

Find a single item by exact code match.

```python
product = await client.products.find_by_code("WIDGET-001")
if product:
    print(f"Found: {product.description}")
```

### `search(code_prefix: str)`

Find items with code starting with prefix.

```python
widgets = await client.products.search("WIDGET")
print(f"Found {len(widgets)} widgets")
```

### `exists(code: str)`

Check if an item exists.

```python
if await client.products.exists("WIDGET-001"):
    print("Product exists")
```

### `list_all()`

Get all items of a type.

```python
all_products = await client.products.list_all()
print(f"Total products: {len(all_products)}")
```

## Helper Registration

Helpers are registered on the client:

```python
class StockTrimClient:
    def __init__(self, ...):
        ...
        # Register helpers
        self.products = ProductsHelper(self)
        self.customers = CustomersHelper(self)
        self.suppliers = SuppliersHelper(self)
        ...
```

This provides a fluent API:

```python
async with StockTrimClient() as client:
    # Fluent access to helpers
    product = await client.products.find_by_code("...")
    customer = await client.customers.find_by_code("...")
    supplier = await client.suppliers.find_by_code("...")
```

## Error Handling in Helpers

Helpers handle common error cases:

```python
async def find_by_code(self, code: str):
    response = await self._call_api(
        get_api_products,
        code=code
    )

    if response.status_code == 200:
        products = response.parsed
        return products[0] if products else None
    elif response.status_code == 404:
        return None  # Not found is normal
    else:
        # Let caller handle unexpected errors
        raise UnexpectedStatus(response.status_code)
```

## Benefits

### 1. Discoverability

IDE autocomplete shows available helpers:

```python
client.products.  # IDE shows: find_by_code, search, exists, list_all
```

### 2. Consistency

All helpers follow the same patterns:

```python
# Same pattern across all domains
product = await client.products.find_by_code("...")
customer = await client.customers.find_by_code("...")
supplier = await client.suppliers.find_by_code("...")
```

### 3. Testability

Helpers can be mocked independently:

```python
async def test_product_search():
    mock_client = Mock(spec=StockTrimClient)
    helper = ProductsHelper(mock_client)

    # Test helper logic without API calls
    ...
```

### 4. Extensibility

Add new helpers without modifying generated code:

```python
class CustomHelper:
    def __init__(self, client: StockTrimClient):
        self.client = client

    async def my_custom_workflow(self):
        # Combine multiple API calls
        ...

# Register custom helper
client.custom = CustomHelper(client)
```

## MCP Tool Integration

Helpers map directly to MCP tools:

| Helper Method | MCP Tool |
|---------------|----------|
| `products.find_by_code()` | `stocktrim_get_product` |
| `products.search()` | `stocktrim_search_products` |
| `products.list_all()` | `stocktrim_list_products` |
| `customers.list_all()` | `stocktrim_list_customers` |

This creates a consistent experience across:
- Python API
- Claude Desktop
- Other MCP clients

## Next Steps

- [Architecture Overview](overview.md) - Overall architecture
- [Transport Layer](transport.md) - Resilience implementation
- [Helper API Reference](../api/helpers.md) - Complete helper API
