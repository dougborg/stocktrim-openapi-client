# Available MCP Tools

The StockTrim MCP Server provides 20+ tools for interacting with the StockTrim API.

## Product Tools

### `stocktrim_get_product`
Get a single product by code.

**Parameters:**
- `code` (string): Product code

### `stocktrim_search_products`
Search for products by code prefix.

**Parameters:**
- `code_prefix` (string): Search prefix

### `stocktrim_list_products`
List all products.

### `stocktrim_create_products`
Create one or more products.

**Parameters:**
- `products` (array): List of product objects

### `stocktrim_delete_products`
Delete products by code.

**Parameters:**
- `codes` (array): List of product codes

## Customer Tools

### `stocktrim_list_customers`
List all customers.

### `stocktrim_get_customer`
Get a specific customer by code.

**Parameters:**
- `code` (string): Customer code

### `stocktrim_create_customers`
Create one or more customers.

**Parameters:**
- `customers` (array): List of customer objects

## Supplier Tools

### `stocktrim_list_suppliers`
List all suppliers.

### `stocktrim_get_supplier`
Get a specific supplier by code.

**Parameters:**
- `code` (string): Supplier code

### `stocktrim_create_suppliers`
Create one or more suppliers.

**Parameters:**
- `suppliers` (array): List of supplier objects

## Inventory Tools

### `stocktrim_get_inventory`
Get current inventory levels.

### `stocktrim_set_inventory`
Set inventory levels for products.

**Parameters:**
- `inventory_items` (array): List of inventory updates

## Order Tools

### Sales Order Tools

#### `create_sales_order`
Create a new sales order for a specific product.

**Parameters:**
- `product_id` (string, required): Product ID for the order
- `order_date` (datetime, required): Order date in ISO format
- `quantity` (float, required): Quantity ordered (must be > 0)
- `external_reference_id` (string, optional): External reference ID
- `unit_price` (float, optional): Unit price
- `location_code` (string, optional): Location code
- `location_name` (string, optional): Location name
- `customer_code` (string, optional): Customer code
- `customer_name` (string, optional): Customer name

**Returns:** Created sales order with ID and details

**Example:**
```json
{
  "product_id": "prod-123",
  "order_date": "2024-01-15T10:00:00Z",
  "quantity": 10.0,
  "customer_code": "CUST-001",
  "unit_price": 29.99
}
```

#### `get_sales_orders`
Get sales orders, optionally filtered by product.

**Parameters:**
- `product_id` (string, optional): Filter by product ID

**Returns:** List of sales orders with total count

**Example:**
```json
{
  "product_id": "prod-123"
}
```

#### `list_sales_orders`
List all sales orders with optional product filter (alias for `get_sales_orders`).

**Parameters:**
- `product_id` (string, optional): Filter by product ID

**Returns:** List of sales orders with total count

#### `delete_sales_orders`
Delete sales orders for a specific product.

**Parameters:**
- `product_id` (string, required): Product ID to delete orders for

**Returns:** Success status and count of deleted orders

**Note:** For safety, `product_id` is required. Cannot delete all orders without a filter.

**Example:**
```json
{
  "product_id": "prod-123"
}
```

### Purchase Order Tools

#### `get_purchase_order`
Get a purchase order by reference number.

**Parameters:**
- `reference_number` (string, required): Purchase order reference number

**Returns:** Purchase order details

#### `list_purchase_orders`
List all purchase orders.

**Returns:** List of purchase orders with total count

#### `delete_purchase_order`
Delete a purchase order by reference number.

**Parameters:**
- `reference_number` (string, required): Reference number to delete

**Returns:** Success status and message

## Location Tools

### `stocktrim_list_locations`
List all locations/warehouses.

### `stocktrim_create_location`
Create a new location.

**Parameters:**
- `location` (object): Location data

## Planning Tools

### `stocktrim_run_order_plan`
Run inventory planning and get recommended orders.

**Parameters:**
- `filter_criteria` (object, optional): Filtering options

### `stocktrim_run_forecast`
Trigger demand forecasting calculations.

## Configuration Tools

### `stocktrim_get_configuration`
Get system configuration values.

**Parameters:**
- `configuration_name` (string): Config key to retrieve

## Bill of Materials Tools

### `stocktrim_list_boms`
List all bills of materials.

### `stocktrim_create_bom`
Create a new bill of materials.

**Parameters:**
- `bom` (object): BOM data

## Next Steps

- [Claude Desktop Setup](claude-desktop.md) - Set up these tools in Claude Desktop
- [Overview](overview.md) - Learn how the MCP server works
