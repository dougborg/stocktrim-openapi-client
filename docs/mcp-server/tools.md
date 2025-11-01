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

### `stocktrim_get_purchase_order`
Get a specific purchase order by reference number.

**Parameters:**
- `reference_number` (string): Purchase order reference number

**Returns:**
Purchase order details including supplier, line items, status, and calculated total cost.

### `stocktrim_list_purchase_orders`
List all purchase orders.

**Returns:**
List of purchase orders with summary information.

### `stocktrim_create_purchase_order`
Create a new purchase order.

**Parameters:**
- `supplier_code` (string, required): Supplier code
- `supplier_name` (string, optional): Supplier name
- `line_items` (array, required): Line items for the purchase order
  - `product_code` (string): Product code
  - `quantity` (number): Quantity to order (must be > 0)
  - `unit_price` (number, optional): Unit price
- `order_date` (string, optional): Order date in ISO format (YYYY-MM-DD). Defaults to current date.
- `location_code` (string, optional): Location code
- `location_name` (string, optional): Location name
- `reference_number` (string, optional): Custom reference number
- `client_reference_number` (string, optional): Client reference number
- `status` (string, optional): Purchase order status (Draft, Approved, Sent, Received). Defaults to "Draft".

**Returns:**
Created purchase order with reference number, supplier details, status, calculated total cost, and line item count.

**Example:**
```json
{
  "supplier_code": "SUP-001",
  "supplier_name": "Acme Supplies",
  "line_items": [
    {"product_code": "WIDGET-001", "quantity": 100, "unit_price": 15.50}
  ],
  "status": "Draft"
}
```

### `stocktrim_delete_purchase_order`
Delete a purchase order by reference number.

**Parameters:**
- `reference_number` (string): Purchase order reference number to delete

**Returns:**
Success/failure status and message.

**Note:** The StockTrim API does not support updating purchase orders. To modify a purchase order, you must delete and recreate it.

### `stocktrim_list_sales_orders`
List all sales orders.

### `stocktrim_create_sales_order`
Create a new sales order.

**Parameters:**
- `order` (object): Sales order data

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
