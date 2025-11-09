# Available MCP Tools

The StockTrim MCP Server provides 20+ tools for interacting with the StockTrim API,
organized into **Foundation Tools** (direct API access) and **Workflow Tools**
(high-level business operations).

## Safety and User Confirmation

Some tools perform destructive operations that require explicit user confirmation. These
tools use the MCP elicitation protocol to request approval before execution.

**Risk Levels:**

- 🔴 **HIGH-RISK**: Requires user confirmation (permanent deletion)
- 🟡 **MEDIUM-HIGH**: May require confirmation (critical modifications)
- 🟠 **MEDIUM**: May require confirmation (financial obligations)
- 🟢 **LOW**: No confirmation (reversible operations)
- ⚪ **SAFE**: No confirmation (read-only operations)

For details on safety patterns and confirmation workflows, see
[Safety Patterns](./safety-patterns.md).

## Tool Categories

### Foundation Tools vs Workflow Tools

**Foundation Tools** provide direct CRUD access to StockTrim entities:

- Direct mapping to API endpoints
- Maximum flexibility and control
- Require multiple calls for complex operations
- Best for custom workflows and integrations

**Workflow Tools** combine multiple operations for common business tasks:

- Intent-based, high-level operations
- Reduce API calls and complexity
- Built-in error handling and validation
- Best for standard inventory management workflows

**When to use which?**

- Use **Workflow Tools** for standard operations (reordering, forecast updates, supplier
  onboarding)
- Use **Foundation Tools** for custom logic, specific entity access, or building new
  workflows

For complete workflow examples and best practices, see
[Workflow Examples](./examples.md).

______________________________________________________________________

## Workflow Tools

These high-level tools combine multiple API operations to accomplish common business
goals.

### Forecast Management

#### `forecasts_update_and_monitor`

Trigger forecast recalculation and monitor progress with real-time updates.

**Parameters:**

- `wait_for_completion` (boolean, default: true): Wait and report progress
- `poll_interval_seconds` (integer, 1-60, default: 5): Status check interval
- `timeout_seconds` (integer, 30-3600, default: 600): Maximum wait time

**Returns:** Markdown-formatted status report with completion status, elapsed time, and
next steps

**Example:** See
[Forecast Management Workflow](./examples.md#workflow-2-forecast-management-and-analysis)

#### `forecasts_get_for_products`

Query forecast data with filters and get formatted markdown reports.

**Parameters:**

- `product_codes` (array, optional): Specific products to query
- `category` (string, optional): Product category filter
- `supplier_code` (string, optional): Supplier filter
- `location_code` (string, optional): Location filter
- `sort_by` (string, default: "days_until_stockout"): Sort order (days_until_stockout,
  recommended_quantity, product_code)
- `max_results` (integer, 1-500, default: 50): Limit results

**Returns:** Markdown report with forecast data, priority indicators, and
recommendations

**Example:** See
[Forecast Management Workflow](./examples.md#workflow-2-forecast-management-and-analysis)

#### `update_forecast_settings`

Update forecast parameters for a product (lead time, safety stock, service level).

**Parameters:**

- `product_code` (string, required): Product code to update
- `lead_time_days` (integer, optional): Lead time in days
- `safety_stock_days` (integer, optional): Safety stock in days
- `service_level` (float, 0-100, optional): Service level percentage
- `minimum_order_quantity` (float, optional): Minimum order quantity

**Returns:** Updated settings and success message

**Example:** See
[Forecast Management Workflow](./examples.md#workflow-2-forecast-management-and-analysis)

### Urgent Order Management

#### `review_urgent_order_requirements`

Identify items approaching stockout, grouped by supplier for efficient purchasing.

**Parameters:**

- `days_threshold` (integer, default: 30): Days until stockout threshold
- `location_codes` (array, optional): Filter by specific locations
- `category` (string, optional): Filter by product category
- `supplier_codes` (array, optional): Filter by specific suppliers

**Returns:** Urgent items grouped by supplier with cost estimates and urgency indicators

**Example:** See
[Automated Inventory Reordering](./examples.md#workflow-1-automated-inventory-reordering)

#### `generate_purchase_orders_from_urgent_items`

Auto-generate draft purchase orders based on forecast recommendations.

**Parameters:**

- `days_threshold` (integer, default: 30): Days until stockout threshold (for API
  consistency)
- `location_codes` (array, optional): Filter by specific locations
- `supplier_codes` (array, optional): Only generate POs for specific suppliers
- `category` (string, optional): Filter by product category

**Returns:** List of generated purchase orders with reference numbers and item counts

**Note:** Generated POs are in Draft status by default. Review in StockTrim UI before
approving.

**Example:** See
[Automated Inventory Reordering](./examples.md#workflow-1-automated-inventory-reordering)

### Supplier Management

#### `create_supplier_with_products`

Onboard a new supplier and map their products in a single atomic operation.

**Parameters:**

- `supplier_code` (string, required): Unique supplier code
- `supplier_name` (string, required): Supplier name
- `is_active` (boolean, default: true): Whether supplier is active
- `product_mappings` (array, required): List of product mappings
  - `product_code` (string): Product code
  - `supplier_product_code` (string, optional): Supplier's SKU code
  - `cost_price` (float, optional): Cost price from this supplier

**Returns:** Supplier details, mapping success/failure counts, and detailed results per
product

**Example:** See
[New Supplier Onboarding](./examples.md#workflow-3-new-supplier-onboarding)

### Product Management

#### `configure_product`

Configure product settings (discontinue status, forecast configuration).

**Parameters:**

- `product_code` (string, required): Product code to configure
- `discontinue` (boolean, optional): Mark product as discontinued
- `configure_forecast` (boolean, optional): Enable/disable forecast calculation

**Returns:** Updated product configuration and success message

**Example:** See
[Product Lifecycle Management](./examples.md#workflow-4-product-lifecycle-management)

______________________________________________________________________

## Foundation Tools

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

### `delete_product` 🔴

Delete a product by code.

**Risk Level:** 🔴 HIGH-RISK - Requires user confirmation via elicitation

**Parameters:**

- `code` (string): Product code to delete

**Returns:** Success status and message

**Safety:** This operation permanently deletes product data and cannot be undone. User
confirmation is required before execution. See
[Safety Patterns](./safety-patterns.md#high-risk-requires-confirmation).

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

### `delete_supplier` 🔴

Delete a supplier by code.

**Risk Level:** 🔴 HIGH-RISK - Requires user confirmation via elicitation

**Parameters:**

- `code` (string): Supplier code to delete

**Returns:** Success status and message

**Safety:** This operation permanently deletes supplier data and all associations
(product mappings, purchase order history) and cannot be undone. User confirmation is
required before execution. See
[Safety Patterns](./safety-patterns.md#high-risk-requires-confirmation).

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

#### `delete_sales_orders` 🔴

Delete sales orders for a specific product.

**Risk Level:** 🔴 HIGH-RISK - Requires user confirmation via elicitation

**Parameters:**

- `product_id` (string, required): Product ID to delete orders for

**Returns:** Success status and message

**Safety:** This operation permanently deletes all sales orders for a product and cannot
be undone. User confirmation is required before execution. For safety, `product_id` is
required - cannot delete all orders without a filter. See
[Safety Patterns](./safety-patterns.md#high-risk-requires-confirmation).

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

**Returns:** Purchase order details including supplier, line items, status, and
calculated total cost.

#### `list_purchase_orders`

List all purchase orders.

**Returns:** List of purchase orders with summary information.

#### `create_purchase_order`

Create a new purchase order.

**Parameters:**

- `supplier_code` (string, required): Supplier code
- `supplier_name` (string, optional): Supplier name
- `line_items` (array, required): Line items for the purchase order
  - `product_code` (string): Product code
  - `quantity` (number): Quantity to order (must be > 0)
  - `unit_price` (number, optional): Unit price
- `order_date` (datetime, optional): Order date in ISO format. Defaults to current date
  if not provided.
- `location_code` (string, optional): Location code
- `location_name` (string, optional): Location name
- `reference_number` (string, optional): Custom reference number
- `client_reference_number` (string, optional): Client reference number
- `status` (string, optional): Purchase order status (Draft, Approved, Sent, Received).
  Defaults to "Draft".

**Returns:** Created purchase order with reference number, supplier details, status,
calculated total cost, and line item count.

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

#### `delete_purchase_order` 🔴

Delete a purchase order by reference number.

**Risk Level:** 🔴 HIGH-RISK - Requires user confirmation via elicitation

**Parameters:**

- `reference_number` (string, required): Purchase order reference number to delete

**Returns:** Success status and message

**Safety:** This operation permanently deletes purchase order data and cannot be undone.
User confirmation is required before execution. See
[Safety Patterns](./safety-patterns.md#high-risk-requires-confirmation).

**Note:** The StockTrim API does not support updating purchase orders. To modify a
purchase order, you must delete and recreate it.

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
