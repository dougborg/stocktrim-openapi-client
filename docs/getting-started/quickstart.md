# Quick Start Guide

This guide will help you get started with the StockTrim OpenAPI Client in minutes.

## Prerequisites

- Python 3.11+
- StockTrim API credentials (tenant ID and signature)

## Step 1: Install the Package

```bash
pip install stocktrim-openapi-client
```

## Step 2: Set Up Authentication

Create a `.env` file in your project root:

```bash
STOCKTRIM_API_AUTH_ID=your_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
```

## Step 3: Your First API Call

Create a Python file and add:

```python
import asyncio
from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.api.products import get_api_products

async def main():
    async with StockTrimClient() as client:
        # Get all products
        response = await get_api_products.asyncio_detailed(client=client)

        if response.status_code == 200:
            products = response.parsed
            print(f"Found {len(products)} products")

            # Print first product
            if products:
                product = products[0]
                print(f"First product: {product.code} - {product.description}")
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 4: Using Helper Methods

The client includes convenient helper methods for common operations:

```python
import asyncio
from stocktrim_public_api_client import StockTrimClient

async def main():
    async with StockTrimClient() as client:
        # Find a specific product by code
        product = await client.products.find_by_code("WIDGET-001")
        if product:
            print(f"Found: {product.description}")

        # Search for products with code prefix
        widgets = await client.products.search("WIDGET")
        print(f"Found {len(widgets)} widgets")

        # Get all customers
        customers = await client.customers.get_all()
        print(f"Total customers: {len(customers)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Operations

### Create a Product

```python
from stocktrim_public_api_client.generated.api.products import post_api_products
from stocktrim_public_api_client.generated.models import ProductsRequestDto

async with StockTrimClient() as client:
    new_product = ProductsRequestDto(
        code="NEW-001",
        description="New Product",
        unit_price=19.99
    )

    response = await post_api_products.asyncio_detailed(
        client=client,
        body=[new_product]
    )
```

### Get Suppliers

```python
from stocktrim_public_api_client.generated.api.suppliers import get_api_suppliers

async with StockTrimClient() as client:
    response = await get_api_suppliers.asyncio_detailed(client=client)
    if response.status_code == 200:
        suppliers = response.parsed
        for supplier in suppliers:
            print(f"{supplier.code}: {supplier.name}")
```

### Create a Sales Order

```python
from stocktrim_public_api_client.generated.api.sales_orders import post_api_sales_orders
from stocktrim_public_api_client.generated.models import SalesOrderRequestDto

async with StockTrimClient() as client:
    order = SalesOrderRequestDto(
        order_number="SO-001",
        customer_code="CUST-001",
        # ... other fields
    )

    response = await post_api_sales_orders.asyncio_detailed(
        client=client,
        body=[order]
    )
```

## Error Handling

The client automatically retries failed requests with exponential backoff:

```python
async with StockTrimClient() as client:
    try:
        response = await get_api_products.asyncio_detailed(client=client)

        if response.status_code == 200:
            products = response.parsed
        elif response.status_code == 404:
            print("Products not found")
        else:
            print(f"Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
```

## Next Steps

- [Configuration Guide](configuration.md) - Advanced configuration options
- [Client Usage Guide](../user-guide/client-guide.md) - Detailed client usage
- [Helper Methods](../user-guide/helper-methods.md) - All convenience methods
- [API Reference](../api/client.md) - Complete API documentation
