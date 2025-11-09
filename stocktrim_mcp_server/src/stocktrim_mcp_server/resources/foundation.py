"""Foundation resources for StockTrim MCP Server.

Provides core entity resources for products, customers, suppliers, locations,
and inventory. These resources enable AI agents to explore the system state
without making tool calls.
"""

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ResourceError

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_public_api_client.client_types import UNSET

logger = get_logger(__name__)


# ============================================================================
# Product Resources
# ============================================================================


async def _get_product_resource(product_code: str, context: Context) -> dict:
    """Get detailed information about a product.

    Args:
        product_code: Product code to retrieve
        context: Request context with services

    Returns:
        Product details as dictionary

    Raises:
        ResourceError: If product not found
    """
    services = get_services(context)
    product = await services.products.get_by_code(product_code)

    if not product:
        raise ResourceError(f"Product not found: {product_code}")

    return {
        "product_code": product.product_code_readable
        if product.product_code_readable not in (None, UNSET)
        else product_code,
        "product_id": product.product_id
        if product.product_id not in (None, UNSET)
        else None,
        "name": product.name if product.name not in (None, UNSET) else None,
        "category": product.category if product.category not in (None, UNSET) else None,
        "cost": float(product.cost) if product.cost not in (None, UNSET) else None,
        "price": float(product.price) if product.price not in (None, UNSET) else None,
        "stock_on_hand": float(product.stock_on_hand)
        if product.stock_on_hand not in (None, UNSET)
        else None,
        "discontinued": product.discontinued
        if product.discontinued not in (None, UNSET)
        else False,
        "ignore_seasonality": product.ignore_seasonality
        if product.ignore_seasonality not in (None, UNSET)
        else False,
        "supplier_code": product.supplier_code
        if product.supplier_code not in (None, UNSET)
        else None,
    }


async def _get_products_catalog_resource(context: Context) -> dict:
    """Get catalog of all products (limited to 50 items for token budget).

    Args:
        context: Request context with services

    Returns:
        Product catalog with pagination info
    """
    services = get_services(context)
    products = await services.products.list_all()

    product_list = []
    # Limit to 50 products for token budget
    for product in products[:50]:
        product_list.append(
            {
                "product_code": product.product_code_readable
                if product.product_code_readable not in (None, UNSET)
                else None,
                "name": product.name if product.name not in (None, UNSET) else None,
                "category": product.category
                if product.category not in (None, UNSET)
                else None,
                "price": float(product.price)
                if product.price not in (None, UNSET)
                else None,
                "discontinued": product.discontinued
                if product.discontinued not in (None, UNSET)
                else False,
            }
        )

    return {
        "products": product_list,
        "total_shown": len(product_list),
        "note": "Limited to 50 products. Use get_product tool for specific products.",
    }


# ============================================================================
# Customer Resources
# ============================================================================


async def _get_customer_resource(customer_code: str, context: Context) -> dict:
    """Get detailed information about a customer.

    Args:
        customer_code: Customer code to retrieve
        context: Request context with services

    Returns:
        Customer details as dictionary

    Raises:
        ResourceError: If customer not found
    """
    services = get_services(context)
    customer = await services.customers.get_by_code(customer_code)

    if not customer:
        raise ResourceError(f"Customer not found: {customer_code}")

    return {
        "customer_code": customer.code
        if customer.code not in (None, UNSET)
        else customer_code,
        "name": customer.name if customer.name not in (None, UNSET) else None,
        "email": customer.email_address
        if customer.email_address not in (None, UNSET)
        else None,
        "phone": customer.phone if customer.phone not in (None, UNSET) else None,
        "address": {
            "street": customer.street_address
            if customer.street_address not in (None, UNSET)
            else None,
            "city": customer.city if customer.city not in (None, UNSET) else None,
            "state": customer.state if customer.state not in (None, UNSET) else None,
            "post_code": customer.post_code
            if customer.post_code not in (None, UNSET)
            else None,
            "country": customer.country
            if customer.country not in (None, UNSET)
            else None,
        },
    }


# ============================================================================
# Supplier Resources
# ============================================================================


async def _get_supplier_resource(supplier_code: str, context: Context) -> dict:
    """Get detailed information about a supplier.

    Args:
        supplier_code: Supplier code to retrieve
        context: Request context with services

    Returns:
        Supplier details as dictionary

    Raises:
        ResourceError: If supplier not found
    """
    services = get_services(context)
    supplier = await services.suppliers.get_by_code(supplier_code)

    if not supplier:
        raise ResourceError(f"Supplier not found: {supplier_code}")

    return {
        "supplier_code": supplier.supplier_code
        if supplier.supplier_code not in (None, UNSET)
        else supplier_code,
        "supplier_id": supplier.id if supplier.id not in (None, UNSET) else None,
        "name": supplier.supplier_name
        if supplier.supplier_name not in (None, UNSET)
        else None,
        "email": supplier.email_address
        if supplier.email_address not in (None, UNSET)
        else None,
        "primary_contact": supplier.primary_contact_name
        if supplier.primary_contact_name not in (None, UNSET)
        else None,
        "default_lead_time": supplier.default_lead_time
        if supplier.default_lead_time not in (None, UNSET)
        else None,
        "street_address": supplier.street_address
        if supplier.street_address not in (None, UNSET)
        else None,
        "state": supplier.state if supplier.state not in (None, UNSET) else None,
        "country": supplier.country if supplier.country not in (None, UNSET) else None,
        "post_code": supplier.post_code
        if supplier.post_code not in (None, UNSET)
        else None,
    }


# ============================================================================
# Location Resources
# ============================================================================


async def _get_location_resource(location_code: str, context: Context) -> dict:
    """Get detailed information about a location.

    Args:
        location_code: Location code to retrieve
        context: Request context with services

    Returns:
        Location details as dictionary

    Raises:
        ResourceError: If location not found
    """
    services = get_services(context)
    locations = await services.locations.list_all()

    # Find matching location
    location = None
    for loc in locations:
        if loc.location_code == location_code:
            location = loc
            break

    if not location:
        raise ResourceError(f"Location not found: {location_code}")

    return {
        "location_code": location.location_code
        if location.location_code not in (None, UNSET)
        else location_code,
        "location_id": location.id if location.id not in (None, UNSET) else None,
        "name": location.location_name
        if location.location_name not in (None, UNSET)
        else None,
        "external_id": location.external_id
        if location.external_id not in (None, UNSET)
        else None,
    }


# ============================================================================
# Inventory Resources
# ============================================================================


async def _get_inventory_resource(
    location_code: str, product_code: str, context: Context
) -> dict:
    """Get inventory levels for a product at a location.

    Args:
        location_code: Location code
        product_code: Product code
        context: Request context with services

    Returns:
        Inventory details as dictionary
    """
    services = get_services(context)

    # Verify location exists
    locations = await services.locations.list_all()
    location_exists = any(loc.location_code == location_code for loc in locations)
    if not location_exists:
        raise ResourceError(f"Location not found: {location_code}")

    # Verify product exists
    product = await services.products.get_by_code(product_code)
    if not product:
        raise ResourceError(f"Product not found: {product_code}")

    # Get inventory - this may return None if no inventory record exists
    # In that case, return zero inventory rather than error
    try:
        # Note: The inventory service doesn't have a direct get method yet
        # For MVP, we'll return basic info from product
        return {
            "location_code": location_code,
            "product_code": product_code,
            "quantity": float(product.stock_on_hand)
            if product.stock_on_hand not in (None, UNSET)
            else 0.0,
            "note": "Showing product-level stock. Use inventory tools for location-specific data.",
        }
    except Exception as e:
        logger.warning(
            f"Error getting inventory for {product_code} at {location_code}: {e}"
        )
        # Return zero inventory on error
        return {
            "location_code": location_code,
            "product_code": product_code,
            "quantity": 0.0,
            "note": "No inventory data available.",
        }


# ============================================================================
# Resource Registration
# ============================================================================


def register_foundation_resources(mcp: FastMCP) -> None:
    """Register foundation resources with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.resource(
        uri="stocktrim://products/{product_code}",
        name="Product Details",
        description="Get detailed information about a specific product",
        mime_type="application/json",
    )
    async def get_product_resource(product_code: str, context: Context) -> dict:
        """Get product details by product code."""
        return await _get_product_resource(product_code, context)

    @mcp.resource(
        uri="stocktrim://products/catalog",
        name="Products Catalog",
        description="Browse product catalog (limited to 50 items)",
        mime_type="application/json",
    )
    async def get_products_catalog_resource(context: Context) -> dict:
        """Get product catalog."""
        return await _get_products_catalog_resource(context)

    @mcp.resource(
        uri="stocktrim://customers/{customer_code}",
        name="Customer Details",
        description="Get detailed information about a specific customer",
        mime_type="application/json",
    )
    async def get_customer_resource(customer_code: str, context: Context) -> dict:
        """Get customer details by customer code."""
        return await _get_customer_resource(customer_code, context)

    @mcp.resource(
        uri="stocktrim://suppliers/{supplier_code}",
        name="Supplier Details",
        description="Get detailed information about a specific supplier",
        mime_type="application/json",
    )
    async def get_supplier_resource(supplier_code: str, context: Context) -> dict:
        """Get supplier details by supplier code."""
        return await _get_supplier_resource(supplier_code, context)

    @mcp.resource(
        uri="stocktrim://locations/{location_code}",
        name="Location Details",
        description="Get detailed information about a specific location/warehouse",
        mime_type="application/json",
    )
    async def get_location_resource(location_code: str, context: Context) -> dict:
        """Get location details by location code."""
        return await _get_location_resource(location_code, context)

    @mcp.resource(
        uri="stocktrim://inventory/{location_code}/{product_code}",
        name="Inventory Levels",
        description="Get inventory levels for a product at a specific location",
        mime_type="application/json",
    )
    async def get_inventory_resource(
        location_code: str, product_code: str, context: Context
    ) -> dict:
        """Get inventory levels for product at location."""
        return await _get_inventory_resource(location_code, product_code, context)
