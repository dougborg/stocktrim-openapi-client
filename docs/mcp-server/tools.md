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

### `stocktrim_list_sales_orders`
List all sales orders.

### `stocktrim_create_sales_order`
Create a new sales order.

**Parameters:**
- `order` (object): Sales order data

### `stocktrim_list_purchase_orders`
List all purchase orders.

### `stocktrim_create_purchase_order`
Create a new purchase order.

**Parameters:**
- `order` (object): Purchase order data

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
