# StockTrim MCP Server - Workflow Examples

This guide provides complete, real-world examples of using the StockTrim MCP Server
workflow tools. Each example includes the full request/response flow and explains when
to use each approach.

## Table of Contents

- [Workflow 1: Automated Inventory Reordering](#workflow-1-automated-inventory-reordering)
- [Workflow 2: Forecast Management and Analysis](#workflow-2-forecast-management-and-analysis)
- [Workflow 3: New Supplier Onboarding](#workflow-3-new-supplier-onboarding)
- [Workflow 4: Product Lifecycle Management](#workflow-4-product-lifecycle-management)
- [Workflow 5: Custom Order Fulfillment](#workflow-5-custom-order-fulfillment)
- [Advanced Patterns](#advanced-patterns)

______________________________________________________________________

## Workflow 1: Automated Inventory Reordering

**Business Goal**: Identify items approaching stockout and automatically generate
purchase orders grouped by supplier.

**When to Use**:

- Regular weekly/monthly reorder cycles
- After significant sales events
- When inventory drops below critical levels

### Approach A: Fully Automated (Recommended)

This approach uses workflow tools to minimize API calls and group operations
efficiently.

#### Step 1: Review Urgent Items

```json
{
  "tool": "review_urgent_order_requirements",
  "request": {
    "days_threshold": 30,
    "location_codes": ["WAREHOUSE-A"],
    "supplier_codes": null
  }
}
```

**Response**:

```json
{
  "suppliers": [
    {
      "supplier_code": "SUP-001",
      "items": [
        {
          "product_code": "WIDGET-001",
          "description": "Premium Widget",
          "current_stock": 45.0,
          "days_until_stock_out": 12,
          "recommended_order_qty": 200.0,
          "supplier_code": "SUP-001",
          "estimated_unit_cost": 15.50,
          "location_name": "Main Warehouse"
        },
        {
          "product_code": "WIDGET-002",
          "description": "Standard Widget",
          "current_stock": 20.0,
          "days_until_stock_out": 8,
          "recommended_order_qty": 150.0,
          "supplier_code": "SUP-001",
          "estimated_unit_cost": 12.00,
          "location_name": "Main Warehouse"
        }
      ],
      "total_items": 2,
      "total_estimated_cost": 4900.00
    },
    {
      "supplier_code": "SUP-002",
      "items": [
        {
          "product_code": "GADGET-001",
          "description": "Electronic Gadget",
          "current_stock": 5.0,
          "days_until_stock_out": 3,
          "recommended_order_qty": 100.0,
          "supplier_code": "SUP-002",
          "estimated_unit_cost": 25.00,
          "location_name": "Main Warehouse"
        }
      ],
      "total_items": 1,
      "total_estimated_cost": 2500.00
    }
  ],
  "total_items": 3,
  "total_estimated_cost": 7400.00
}
```

**Analysis**: We have 3 urgent items across 2 suppliers totaling $7,400. GADGET-001 is
most urgent (3 days).

#### Step 2: Generate Purchase Orders

After reviewing the recommendations, generate draft POs for approved suppliers:

```json
{
  "tool": "generate_purchase_orders_from_urgent_items",
  "request": {
    "days_threshold": 30,
    "supplier_codes": ["SUP-001", "SUP-002"],
    "location_codes": ["WAREHOUSE-A"]
  }
}
```

**Response**:

```json
{
  "purchase_orders": [
    {
      "reference_number": "PO-2024-0156",
      "supplier_code": "SUP-001",
      "supplier_name": "Acme Widgets Inc",
      "item_count": 2,
      "status": "Draft"
    },
    {
      "reference_number": "PO-2024-0157",
      "supplier_code": "SUP-002",
      "supplier_name": "Global Electronics",
      "item_count": 1,
      "status": "Draft"
    }
  ],
  "total_count": 2
}
```

**Next Steps**: Review the draft POs in StockTrim UI and approve for ordering.

______________________________________________________________________

### Approach B: Manual/Step-by-Step

Use foundation tools when you need granular control over each step.

#### Step 1: List Products with Low Stock

```json
{
  "tool": "list_products",
  "request": {
    "category": "Widgets",
    "page_size": 50
  }
}
```

#### Step 2: Check Inventory Levels

For each product from step 1:

```json
{
  "tool": "get_inventory",
  "request": {
    "product_code": "WIDGET-001",
    "location_code": "WAREHOUSE-A"
  }
}
```

#### Step 3: Create Purchase Order Manually

```json
{
  "tool": "create_purchase_order",
  "request": {
    "supplier_code": "SUP-001",
    "reference_number": "PO-2024-0156",
    "line_items": [
      {
        "product_code": "WIDGET-001",
        "quantity": 200,
        "unit_price": 15.50
      }
    ],
    "expected_delivery_date": "2024-02-15"
  }
}
```

**Trade-offs**:

- ✅ More control over each step
- ✅ Can customize quantities and pricing
- ❌ Requires many more API calls
- ❌ Manual calculation of reorder quantities
- ❌ Risk of missing items or suppliers

______________________________________________________________________

## Workflow 2: Forecast Management and Analysis

**Business Goal**: Update forecasts and identify products needing attention.

**When to Use**:

- After importing new sales data
- Weekly/monthly forecast reviews
- Before planning major purchasing decisions
- When investigating demand anomalies

### Step 1: Trigger Forecast Recalculation

```json
{
  "tool": "forecasts_update_and_monitor",
  "request": {
    "wait_for_completion": true,
    "poll_interval_seconds": 5,
    "timeout_seconds": 600
  }
}
```

**Response** (markdown formatted):

```markdown
# Forecast Update Status

**Status**: ✅ Complete

**Time Elapsed**: 45.2 seconds

**Progress**: 100%

Forecast calculation completed successfully.

## Next Steps
- Use `forecasts_get_for_products` to review updated forecasts
- Use `review_urgent_order_requirements` to generate purchase orders
- Check specific products or categories for forecast accuracy
```

### Step 2: Review Updated Forecasts

Query forecasts with filters to focus on specific categories:

```json
{
  "tool": "forecasts_get_for_products",
  "request": {
    "category": "Widgets",
    "location_code": "WAREHOUSE-A",
    "sort_by": "days_until_stockout",
    "max_results": 20
  }
}
```

**Response** (markdown formatted):

```markdown
# Forecast Data

**Filters**: Category: Widgets, Location: WAREHOUSE-A
**Results**: Showing 20 of 45 total items
**Sorted by**: days_until_stockout

## Summary
- **Total Recommended Order Quantity**: 2,450 units
- **Average Days Until Stockout**: 18.3 days

## Product Forecasts

### WIDGET-001 - Premium Widget
**Priority**: 🔴 HIGH
- **Current Stock**: 45 units
- **Days Until Stockout**: 5.2 days
- **Recommended Order**: 200 units
- **Safety Stock**: 50 units
- **Lead Time**: 14 days

### WIDGET-002 - Standard Widget
**Priority**: 🟡 MEDIUM
- **Current Stock**: 120 units
- **Days Until Stockout**: 12.5 days
- **Recommended Order**: 150 units
- **Safety Stock**: 40 units
- **Lead Time**: 10 days

[... 18 more products ...]

## Next Steps
- Review high priority items (< 7 days until stockout)
- Use `review_urgent_order_requirements` to plan purchase orders
- Use `generate_purchase_orders_from_urgent_items` to create draft POs
- Update forecast settings for products with unexpected recommendations
```

### Step 3: Adjust Forecast Settings for Anomalies

If a product's forecast seems off (e.g., WIDGET-001 shows unexpectedly high demand):

```json
{
  "tool": "update_forecast_settings",
  "request": {
    "product_code": "WIDGET-001",
    "lead_time_days": 14,
    "safety_stock_days": 10,
    "service_level": 98.0,
    "minimum_order_quantity": 50.0
  }
}
```

**Response**:

```json
{
  "product_code": "WIDGET-001",
  "lead_time": 14,
  "forecast_period": 10,
  "service_level": 98.0,
  "minimum_order_quantity": 50.0,
  "message": "Successfully updated forecast settings for WIDGET-001"
}
```

### Step 4: Re-run Forecast with New Settings

```json
{
  "tool": "forecasts_update_and_monitor",
  "request": {
    "wait_for_completion": true,
    "poll_interval_seconds": 5,
    "timeout_seconds": 300
  }
}
```

**Best Practice**: After updating forecast settings for multiple products, always re-run
the forecast calculation to see the impact of your changes.

______________________________________________________________________

## Workflow 3: New Supplier Onboarding

**Business Goal**: Add a new supplier and map their products in a single operation.

**When to Use**:

- Onboarding new vendors
- Adding alternative suppliers for existing products
- Supplier consolidation projects

### Approach A: Workflow Tool (Recommended)

```json
{
  "tool": "create_supplier_with_products",
  "request": {
    "supplier_code": "SUP-NEW-001",
    "supplier_name": "NewTech Suppliers Ltd",
    "is_active": true,
    "product_mappings": [
      {
        "product_code": "WIDGET-001",
        "supplier_product_code": "NT-WID-001",
        "cost_price": 14.50
      },
      {
        "product_code": "WIDGET-002",
        "supplier_product_code": "NT-WID-002",
        "cost_price": 11.00
      },
      {
        "product_code": "GADGET-001",
        "supplier_product_code": "NT-GAD-001",
        "cost_price": 24.00
      }
    ]
  }
}
```

**Response**:

```json
{
  "supplier_code": "SUP-NEW-001",
  "supplier_name": "NewTech Suppliers Ltd",
  "supplier_id": "12345",
  "mappings_attempted": 3,
  "mappings_successful": 3,
  "mapping_details": [
    {
      "product_code": "WIDGET-001",
      "success": true,
      "error": null
    },
    {
      "product_code": "WIDGET-002",
      "success": true,
      "error": null
    },
    {
      "product_code": "GADGET-001",
      "success": true,
      "error": null
    }
  ],
  "message": "Supplier 'SUP-NEW-001' created successfully. 3/3 product mappings completed."
}
```

**Advantages**:

- ✅ Single API operation
- ✅ Atomic transaction (supplier created first, then mappings)
- ✅ Detailed success/failure tracking per product
- ✅ Automatic rollback if supplier creation fails

### Approach B: Step-by-Step Foundation Tools

#### Step 1: Create Supplier

```json
{
  "tool": "create_suppliers",
  "request": {
    "suppliers": [
      {
        "code": "SUP-NEW-001",
        "name": "NewTech Suppliers Ltd",
        "is_active": true
      }
    ]
  }
}
```

#### Step 2: Update Each Product with Supplier Mapping

For each product, update with new supplier info (requires more complex logic):

```json
{
  "tool": "get_product",
  "request": {
    "product_code": "WIDGET-001"
  }
}
```

Then update product with supplier details (this is complex - workflow tool handles it
automatically).

**Trade-offs**:

- ✅ More flexibility for custom logic
- ❌ Requires multiple API calls
- ❌ Manual handling of partial failures
- ❌ More complex error handling

______________________________________________________________________

## Workflow 4: Product Lifecycle Management

**Business Goal**: Manage product discontinuation and forecast configuration.

**When to Use**:

- Product end-of-life processes
- Seasonal product management
- SKU rationalization projects

### Scenario: Discontinuing a Product

When discontinuing a product, you typically want to:

1. Stop forecasting demand
1. Mark as discontinued
1. Clear remaining inventory

```json
{
  "tool": "configure_product",
  "request": {
    "product_code": "WIDGET-OLD",
    "discontinue": true,
    "configure_forecast": false
  }
}
```

**Response**:

```json
{
  "product_code": "WIDGET-OLD",
  "discontinued": true,
  "ignore_seasonality": true,
  "message": "Successfully configured product WIDGET-OLD"
}
```

### Scenario: Seasonal Product Activation

When activating a seasonal product (e.g., holiday items):

```json
{
  "tool": "configure_product",
  "request": {
    "product_code": "HOLIDAY-001",
    "discontinue": false,
    "configure_forecast": true
  }
}
```

**Response**:

```json
{
  "product_code": "HOLIDAY-001",
  "discontinued": false,
  "ignore_seasonality": false,
  "message": "Successfully configured product HOLIDAY-001"
}
```

**Best Practice**: After activating seasonal products, update their forecast settings
and trigger a forecast recalculation:

```json
{
  "tool": "update_forecast_settings",
  "request": {
    "product_code": "HOLIDAY-001",
    "lead_time_days": 30,
    "safety_stock_days": 14,
    "service_level": 99.0
  }
}
```

______________________________________________________________________

## Workflow 5: Customer Order Fulfillment

**Business Goal**: Process customer orders while maintaining inventory accuracy.

**When to Use**:

- Processing e-commerce orders
- Manual order entry
- Drop-shipping workflows

### Complete Order Flow

#### Step 1: Verify Customer Exists

```json
{
  "tool": "get_customer",
  "request": {
    "customer_code": "CUST-001"
  }
}
```

**Response**:

```json
{
  "id": "customer-123",
  "code": "CUST-001",
  "name": "Acme Corporation",
  "email": "orders@acme.com",
  "phone": "+1-555-0123"
}
```

#### Step 2: Verify Product and Check Stock

```json
{
  "tool": "get_product",
  "request": {
    "product_code": "WIDGET-001"
  }
}
```

**Response**:

```json
{
  "product_id": "prod-456",
  "product_code_readable": "WIDGET-001",
  "name": "Premium Widget",
  "cost": 15.50,
  "sale_price": 29.99
}
```

#### Step 3: Check Inventory Availability

```json
{
  "tool": "get_inventory",
  "request": {
    "product_code": "WIDGET-001",
    "location_code": "WAREHOUSE-A"
  }
}
```

**Response**:

```json
{
  "product_code": "WIDGET-001",
  "location_code": "WAREHOUSE-A",
  "quantity": 150.0,
  "reserved_quantity": 20.0,
  "available_quantity": 130.0
}
```

**Check**: Customer wants 25 units. Available: 130 units. ✅ Can fulfill.

#### Step 4: Create Sales Order

```json
{
  "tool": "create_sales_order",
  "request": {
    "customer_code": "CUST-001",
    "reference_number": "SO-2024-0089",
    "order_date": "2024-01-15",
    "line_items": [
      {
        "product_code": "WIDGET-001",
        "quantity": 25,
        "unit_price": 29.99
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Portland",
      "state": "OR",
      "postal_code": "97201",
      "country": "US"
    }
  }
}
```

**Response**:

```json
{
  "order_id": "so-789",
  "reference_number": "SO-2024-0089",
  "status": "Pending",
  "total_amount": 749.75,
  "message": "Sales order created successfully"
}
```

#### Step 5: Update Inventory After Shipment

Once the order ships, deduct from inventory:

```json
{
  "tool": "set_inventory",
  "request": {
    "product_code": "WIDGET-001",
    "location_code": "WAREHOUSE-A",
    "quantity": 125.0,
    "adjustment_reason": "Sales Order SO-2024-0089 shipped"
  }
}
```

**Response**:

```json
{
  "product_code": "WIDGET-001",
  "location_code": "WAREHOUSE-A",
  "previous_quantity": 150.0,
  "new_quantity": 125.0,
  "adjustment": -25.0,
  "message": "Inventory updated successfully"
}
```

______________________________________________________________________

## Advanced Patterns

### Pattern 1: Multi-Location Reordering

When managing multiple warehouses, review urgent items per location:

```json
{
  "tool": "review_urgent_order_requirements",
  "request": {
    "days_threshold": 30,
    "location_codes": ["WAREHOUSE-A", "WAREHOUSE-B", "WAREHOUSE-C"]
  }
}
```

Then generate POs per location or per supplier depending on your logistics.

### Pattern 2: Forecast Analysis Loop

Iteratively refine forecasts:

1. Run forecast calculation
1. Review results for anomalies
1. Adjust settings for outliers
1. Re-run forecast
1. Repeat until forecasts stabilize

**Python Pseudocode**:

```python
# Step 1: Run initial forecast
forecasts_update_and_monitor(wait_for_completion=True)

# Step 2: Get products with unexpected forecasts
results = forecasts_get_for_products(sort_by="days_until_stockout", max_results=50)

# Step 3: Identify anomalies (e.g., < 3 days or > 180 days)
anomalies = [p for p in results if p.days_until_stockout < 3 or p.days_until_stockout > 180]

# Step 4: Update settings for anomalies
for product in anomalies:
    update_forecast_settings(
        product_code=product.code,
        lead_time_days=adjusted_lead_time,
        safety_stock_days=adjusted_safety_stock
    )

# Step 5: Re-run forecast
forecasts_update_and_monitor(wait_for_completion=True)
```

### Pattern 3: Supplier Performance Analysis

Track urgent items by supplier to identify reliability issues:

```json
{
  "tool": "review_urgent_order_requirements",
  "request": {
    "days_threshold": 14,
    "supplier_codes": null
  }
}
```

Analyze response to find suppliers with frequent urgent items (may indicate longer lead
times or quality issues).

### Pattern 4: Batch Product Configuration

When updating settings for multiple products (e.g., category-wide changes):

```python
# Get all products in category
products = list_products(category="Widgets")

# Update each product's forecast settings
for product in products:
    update_forecast_settings(
        product_code=product.code,
        service_level=95.0,
        minimum_order_quantity=10.0
    )

# Trigger forecast recalculation
forecasts_update_and_monitor(wait_for_completion=True)
```

______________________________________________________________________

## Error Handling Best Practices

### Handle None Returns Gracefully

Foundation tools return `None` when entities don't exist:

```python
customer = get_customer("CUST-999")
if customer is None:
    # Customer doesn't exist - create it or show error
    print("Customer not found. Please create customer first.")
else:
    # Customer exists - proceed with order
    create_sales_order(customer_code=customer.code, ...)
```

### Validate Before Complex Operations

Always verify prerequisites before multi-step workflows:

```python
# Verify all products exist before creating supplier mapping
product_codes = ["WIDGET-001", "WIDGET-002", "GADGET-001"]
for code in product_codes:
    product = get_product(code)
    if product is None:
        raise ValueError(f"Product {code} not found - cannot create supplier mapping")

# All products exist - proceed with supplier creation
create_supplier_with_products(
    supplier_code="SUP-NEW-001",
    product_mappings=[...]
)
```

### Handle Partial Failures in Batch Operations

Workflow tools provide detailed failure tracking:

```python
result = create_supplier_with_products(...)

if result.mappings_successful < result.mappings_attempted:
    print(f"Warning: Only {result.mappings_successful}/{result.mappings_attempted} products mapped")

    # Check which ones failed
    for mapping in result.mapping_details:
        if not mapping.success:
            print(f"Failed: {mapping.product_code} - {mapping.error}")
```

______________________________________________________________________

## Performance Optimization Tips

### Minimize API Calls

- ✅ Use workflow tools instead of multiple foundation tool calls
- ✅ Batch operations when possible (`create_products` instead of individual calls)
- ✅ Cache frequently accessed data (customer lists, product catalogs)

### Forecast Calculation Timing

- Run forecasts during off-peak hours (forecasts can take several minutes)
- Use `wait_for_completion=false` for async workflows
- Increase `timeout_seconds` for large catalogs (1000+ products)

### Query Result Limits

- Use `max_results` parameter to limit response sizes
- Filter by location/category/supplier to reduce result sets
- Paginate through large datasets instead of requesting everything at once

______________________________________________________________________

## Common Troubleshooting Scenarios

### Forecast Calculation Timeout

If `forecasts_update_and_monitor` times out:

1. Check if calculation is still running:
   `forecasts_update_and_monitor(wait_for_completion=false)`
1. Increase timeout: `timeout_seconds=1800` (30 minutes)
1. Query partial results: `forecasts_get_for_products` will show any completed forecasts

### Empty Forecast Results

If `forecasts_get_for_products` returns no data:

1. Verify products have sales history data
1. Check filters (category/location/supplier) aren't too restrictive
1. Run forecast calculation: `forecasts_update_and_monitor`
1. Try query without filters to confirm data exists

### Purchase Order Generation Produces No POs

If `generate_purchase_orders_from_urgent_items` returns empty:

1. Check `days_threshold` isn't too strict (try 60 or 90 days)
1. Verify `location_codes` and `supplier_codes` filters are correct
1. Run `review_urgent_order_requirements` first to see if any items qualify
1. Ensure forecasts have been calculated recently

______________________________________________________________________

## Next Steps

- Review [MCP Server Tools Reference](./tools.md) for complete API documentation
- See [Logging Guide](./logging.md) for observability features
- Check [FastMCP Documentation](https://github.com/jlowin/fastmcp) for server internals
- Report issues at https://github.com/dougborg/stocktrim-openapi-client/issues
