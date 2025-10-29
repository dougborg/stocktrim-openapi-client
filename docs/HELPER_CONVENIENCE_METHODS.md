# Helper Convenience Methods Reference

This document catalogs all convenience methods added to the StockTrim client helpers.
These methods provide ergonomic wrappers around the raw API calls and will directly
inform MCP tool design.

## Design Principles

1. **Clear Intent**: Method names clearly express what they do
1. **Handle Inconsistencies**: Smooth over API quirks (single vs list returns)
1. **Common Patterns**: Implement frequently-used workflows
1. **Optional Simplification**: Reduce boilerplate for simple use cases

______________________________________________________________________

## Products Helper

### `find_by_code(code: str) -> ProductsResponseDto | None`

Find a single product by exact code match.

**Use Case**: Get a specific product or check if it exists **Returns**: Product object
or None if not found **MCP Tool**: `stocktrim_get_product`

```python
product = await client.products.find_by_code("WIDGET-001")
if product:
    print(f"Found: {product.description}")
```

### `search(code_prefix: str) -> list[ProductsResponseDto]`

Search for products with code starting with prefix.

**Use Case**: Find all products matching a pattern **Returns**: List of matching
products **MCP Tool**: `stocktrim_search_products`

```python
widgets = await client.products.search("WIDGET")
```

### `exists(code: str) -> bool`

Check if a product with given code exists.

**Use Case**: Validate product existence before operations **Returns**: Boolean **MCP
Tool**: Can be used internally by other tools

```python
if await client.products.exists("WIDGET-001"):
    print("Product already exists")
```

______________________________________________________________________

## Customers Helper

### `exists(code: str) -> bool`

Check if a customer with given code exists.

**Use Case**: Validate customer existence **Returns**: Boolean **MCP Tool**: Can be used
internally by other tools

```python
if await client.customers.exists("CUST-001"):
    print("Customer exists")
```

### `find_or_create(code: str, **defaults) -> CustomerDto`

Get customer by code, or create if doesn't exist.

**Use Case**: Ensure customer exists (idempotent operation) **Returns**: Customer object
(existing or newly created) **MCP Tool**: `stocktrim_ensure_customer`

```python
customer = await client.customers.find_or_create(
    "CUST-001",
    name="New Customer",
    email="customer@example.com"
)
```

______________________________________________________________________

## Suppliers Helper

### `find_by_code(code: str) -> SupplierResponseDto | None`

Find a single supplier by exact code match.

**Handles**: API's inconsistent return type (single vs list) **Use Case**: Get a
specific supplier **Returns**: Supplier object or None **MCP Tool**:
`stocktrim_get_supplier`

```python
supplier = await client.suppliers.find_by_code("SUP-001")
if supplier:
    print(f"Found: {supplier.name}")
```

### `create_one(supplier: SupplierRequestDto) -> SupplierResponseDto | None`

Create a single supplier.

**Handles**: Wraps batch API for single-item convenience **Use Case**: Create one
supplier without array syntax **Returns**: Created supplier or None **MCP Tool**:
`stocktrim_create_supplier`

```python
supplier = await client.suppliers.create_one(
    SupplierRequestDto(code="SUP-001", name="New Supplier")
)
```

### `exists(code: str) -> bool`

Check if a supplier with given code exists.

**Use Case**: Validate supplier existence **Returns**: Boolean **MCP Tool**: Can be used
internally by other tools

```python
if await client.suppliers.exists("SUP-001"):
    print("Supplier exists")
```

______________________________________________________________________

## SalesOrders Helper

### `get_for_product(product_id: str) -> list[SalesOrderResponseDto]`

Get all sales orders for a specific product.

**Clarifies**: Intent is clearer than `get_all(product_id=X)` **Use Case**: View demand
for a product **Returns**: List of sales orders **MCP Tool**:
`stocktrim_get_product_sales_orders`

```python
orders = await client.sales_orders.get_for_product("123")
```

### `delete_for_product(product_id: str) -> None`

Delete all sales orders for a specific product.

**Clarifies**: Intent is clearer than `delete(product_id=X)` **Use Case**: Clean up
orders for a discontinued product **Returns**: None **MCP Tool**:
`stocktrim_delete_product_sales_orders`

```python
await client.sales_orders.delete_for_product("123")
```

______________________________________________________________________

## PurchaseOrders Helper

### `find_by_reference(reference_number: str) -> PurchaseOrderResponseDto | None`

Find a single purchase order by reference number.

**Handles**: API's inconsistent return type (single vs list) **Use Case**: Get a
specific purchase order **Returns**: Purchase order object or None **MCP Tool**:
`stocktrim_get_purchase_order`

```python
order = await client.purchase_orders.find_by_reference("PO-001")
if order:
    print(f"Found order: {order.reference_number}")
```

### `exists(reference_number: str) -> bool`

Check if a purchase order with given reference number exists.

**Use Case**: Validate purchase order existence **Returns**: Boolean **MCP Tool**: Can
be used internally by other tools

```python
if await client.purchase_orders.exists("PO-001"):
    print("Purchase order exists")
```

______________________________________________________________________

## Inventory Helper

### `set_for_product(product_id, stock_on_hand=UNSET, stock_on_order=UNSET, location_code=UNSET, location_name=UNSET) -> PurchaseOrderResponseDto`

Set inventory levels for a single product.

**Simplifies**: No need to manually create SetInventoryRequest **Use Case**: Update
stock levels for one product **Returns**: Response object (API returns
PurchaseOrderResponseDto) **MCP Tool**: `stocktrim_set_product_inventory`

```python
result = await client.inventory.set_for_product(
    product_id="123",
    stock_on_hand=50.0,
    stock_on_order=100.0,
    location_code="WAREHOUSE-A"
)
```

______________________________________________________________________

## MCP Tool Design Recommendations

### Core CRUD Tools

Based on the convenience methods, these would be the most valuable MCP tools:

1. **Product Tools**

   - `stocktrim_get_product(code)` - Uses `find_by_code()`
   - `stocktrim_search_products(prefix)` - Uses `search()`
   - `stocktrim_create_product(...)` - Uses `create()`
   - `stocktrim_delete_product(product_id)` - Uses `delete()`

1. **Customer Tools**

   - `stocktrim_get_customer(code)` - Uses `get()`
   - `stocktrim_ensure_customer(code, **defaults)` - Uses `find_or_create()`
   - `stocktrim_list_customers()` - Uses `get_all()`

1. **Supplier Tools**

   - `stocktrim_get_supplier(code)` - Uses `find_by_code()`
   - `stocktrim_create_supplier(...)` - Uses `create_one()`
   - `stocktrim_delete_supplier(code)` - Uses `delete()`

1. **Order Tools**

   - `stocktrim_get_purchase_order(ref)` - Uses `find_by_reference()`
   - `stocktrim_create_purchase_order(...)` - Uses `create()`
   - `stocktrim_get_product_sales(product_id)` - Uses `get_for_product()`

1. **Inventory Tools**

   - `stocktrim_set_inventory(product_id, ...)` - Uses `set_for_product()`

### Tool Categories

**Read Tools** (safe, frequent use):

- get_product, get_customer, get_supplier, get_purchase_order
- search_products, list_customers
- get_product_sales

**Write Tools** (require confirmation):

- create_product, create_supplier, create_purchase_order
- ensure_customer (idempotent)
- set_inventory

**Delete Tools** (require strong confirmation):

- delete_product, delete_supplier
- delete_product_sales

### Tool Design Patterns

1. **Single Item Retrieval**: Return object or null
1. **List Retrieval**: Return array (empty if none)
1. **Creation**: Return created object
1. **Deletion**: Return success boolean
1. **Updates**: Return updated object

### Error Handling

The convenience methods already handle:

- API inconsistencies (single vs list)
- Missing items (return None instead of error)
- Type safety (proper typing throughout)

MCP tools should:

- Pass through these handled responses
- Add user-friendly error messages
- Provide confirmation for destructive operations

______________________________________________________________________

## Benefits for MCP Integration

1. **Simplified Parameters**: Fewer required fields for common operations
1. **Consistent Returns**: Predictable return types despite API quirks
1. **Clear Semantics**: Method names express intent clearly
1. **Error Resilience**: Graceful handling of missing data
1. **Type Safety**: Full type hints for better tool definitions

______________________________________________________________________

## Future Enhancements

Potential additional convenience methods based on usage patterns:

- **Bulk Operations**: `create_many_products(products: list)`
- **Filtering**: `find_customers_by_name(name: str)`
- **Aggregations**: `count_products()`, `count_orders_for_product(id)`
- **Status Checks**: `is_product_in_stock(code)`, `has_pending_orders(product_id)`
- **Batch Queries**: `get_products_by_codes(codes: list)`

These can be added as usage patterns emerge from MCP tool analytics.
