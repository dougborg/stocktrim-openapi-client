"""Supplier onboarding workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for onboarding new suppliers
with their associated product mappings.
"""

from __future__ import annotations

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.observability import observe_tool
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.product_supplier import (
    ProductSupplier,
)
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)

logger = get_logger(__name__)

# ============================================================================
# Tool: create_supplier_with_products
# ============================================================================


class SupplierProductMapping(BaseModel):
    """Product mapping for supplier onboarding."""

    product_code: str = Field(description="Product code")
    supplier_product_code: str | None = Field(
        default=None, description="Supplier's SKU code for this product"
    )
    cost_price: float | None = Field(
        default=None, description="Cost price from this supplier"
    )


class CreateSupplierWithProductsRequest(BaseModel):
    """Request for creating a supplier with product mappings."""

    supplier_code: str = Field(description="Unique supplier code")
    supplier_name: str = Field(description="Supplier name")
    is_active: bool = Field(default=True, description="Whether supplier is active")
    email_address: str | None = Field(default=None, description="Contact email")
    primary_contact_name: str | None = Field(default=None, description="Contact person")
    default_lead_time: int | None = Field(
        default=None, description="Default lead time in days"
    )
    street_address: str | None = Field(default=None, description="Street address")
    city: str | None = Field(default=None, description="City")
    state: str | None = Field(default=None, description="State/province")
    country: str | None = Field(default=None, description="Country")
    post_code: str | None = Field(default=None, description="Postal code")
    product_mappings: list[SupplierProductMapping] = Field(
        default_factory=list, description="List of products to map to this supplier"
    )


class ProductMappingSummary(BaseModel):
    """Summary of a product mapping operation."""

    product_code: str = Field(description="Product code")
    success: bool = Field(description="Whether mapping was successful")
    error: str | None = Field(default=None, description="Error message if failed")


class CreateSupplierWithProductsResponse(BaseModel):
    """Response with supplier creation and mapping results."""

    supplier_code: str = Field(description="Created supplier code")
    supplier_name: str = Field(description="Created supplier name")
    supplier_id: str | None = Field(description="Created supplier ID")
    mappings_attempted: int = Field(description="Number of product mappings attempted")
    mappings_successful: int = Field(
        description="Number of product mappings completed successfully"
    )
    mapping_details: list[ProductMappingSummary] = Field(
        description="Details of each product mapping"
    )
    message: str = Field(description="Summary message")


async def _create_supplier_with_products_impl(
    request: CreateSupplierWithProductsRequest, context: Context
) -> str:
    """Implementation of create_supplier_with_products tool.

    Args:
        request: Request with supplier and product mapping details
        context: Server context with StockTrimClient

    Returns:
        Markdown formatted report with creation results

    Raises:
        Exception: If supplier creation fails
    """
    logger.info(f"Creating supplier: {request.supplier_code}")

    try:
        # Get services from context
        services = get_services(context)

        # Step 1: Create the supplier first with all fields
        created_supplier = await services.suppliers.create(
            code=request.supplier_code,
            name=request.supplier_name,
            email=request.email_address,
            primary_contact=request.primary_contact_name,
            default_lead_time=request.default_lead_time,
            street_address=request.street_address,
            address_line_1=request.city,  # Using city as address_line_1
            state=request.state,
            country=request.country,
            post_code=request.post_code,
        )

        if not created_supplier:
            raise ValueError(f"Failed to create supplier: {request.supplier_code}")

        logger.info(f"Supplier created: {request.supplier_code}")

        # Step 2: Create product-supplier mappings
        # Only proceed with mappings if supplier creation succeeded
        mapping_details: list[ProductMappingSummary] = []
        successful_mappings = 0

        for mapping in request.product_mappings:
            try:
                # Fetch existing product
                existing_product = await services.products.get_by_code(
                    mapping.product_code
                )

                if not existing_product:
                    mapping_details.append(
                        ProductMappingSummary(
                            product_code=mapping.product_code,
                            success=False,
                            error=f"Product not found: {mapping.product_code}",
                        )
                    )
                    logger.warning(f"Product not found: {mapping.product_code}")
                    continue

                # Build the product supplier mapping
                # Get supplier ID from the created supplier
                supplier_id = (
                    created_supplier.id
                    if created_supplier.id not in (None, UNSET)
                    else None
                )

                if not supplier_id:
                    raise ValueError("Created supplier has no ID")

                # Get existing suppliers list or create new one
                existing_suppliers = (
                    existing_product.suppliers
                    if existing_product.suppliers not in (None, UNSET)
                    else []
                )

                # Ensure it's a list
                if existing_suppliers is None:
                    existing_suppliers = []

                # Create new supplier mapping
                new_supplier_mapping = ProductSupplier(
                    supplier_id=supplier_id,
                    supplier_name=request.supplier_name,
                    supplier_sku_code=mapping.supplier_product_code or UNSET,
                )

                # Add new mapping to existing suppliers
                updated_suppliers = [*list(existing_suppliers), new_supplier_mapping]

                # Update product with new supplier mapping
                update_data = ProductsRequestDto(
                    product_id=existing_product.product_id,
                    product_code_readable=existing_product.product_code_readable
                    if existing_product.product_code_readable not in (None, UNSET)
                    else UNSET,
                    suppliers=updated_suppliers,
                )

                # Also update cost if provided
                if mapping.cost_price is not None:
                    update_data.cost = mapping.cost_price
                    # Set the primary supplier code
                    update_data.supplier_code = request.supplier_code

                # Update product using client directly for complex supplier mapping
                await services.client.products.create(update_data)

                mapping_details.append(
                    ProductMappingSummary(
                        product_code=mapping.product_code,
                        success=True,
                    )
                )
                successful_mappings += 1
                logger.info(
                    f"Product mapping created: {mapping.product_code} -> {request.supplier_code}"
                )

            except Exception as e:
                mapping_details.append(
                    ProductMappingSummary(
                        product_code=mapping.product_code,
                        success=False,
                        error=str(e),
                    )
                )
                logger.error(
                    f"Failed to create mapping for {mapping.product_code}: {e}"
                )

        # Build markdown report
        report_lines = [
            "# Supplier Onboarding Complete",
            "",
            f"## Supplier: {request.supplier_name} ({request.supplier_code})",
            "",
            "**Status**: ✅ Created successfully",
            "",
        ]

        # Add supplier details
        if created_supplier.id not in (None, UNSET):
            report_lines.append(f"**Supplier ID**: {created_supplier.id}")

        if request.email_address:
            report_lines.append(f"**Email**: {request.email_address}")

        if request.primary_contact_name:
            report_lines.append(f"**Primary Contact**: {request.primary_contact_name}")

        if request.default_lead_time:
            report_lines.append(
                f"**Default Lead Time**: {request.default_lead_time} days"
            )

        # Add address if provided
        address_parts = []
        if request.street_address:
            address_parts.append(request.street_address)
        if request.city:
            address_parts.append(request.city)
        if request.state:
            address_parts.append(request.state)
        if request.post_code:
            address_parts.append(request.post_code)
        if request.country:
            address_parts.append(request.country)

        if address_parts:
            report_lines.extend(["", "**Address**:", ", ".join(address_parts)])

        # Add product mappings section
        if request.product_mappings:
            report_lines.extend(
                [
                    "",
                    f"## Product Mappings: {successful_mappings}/{len(request.product_mappings)} successful",
                    "",
                ]
            )

            # Group by success/failure
            successful = [m for m in mapping_details if m.success]
            failed = [m for m in mapping_details if not m.success]

            if successful:
                report_lines.append("### ✅ Successfully Mapped:")
                for mapping in successful:
                    report_lines.append(f"- {mapping.product_code}")

            if failed:
                report_lines.extend(["", "### ❌ Failed Mappings:"])
                for mapping in failed:
                    report_lines.append(f"- {mapping.product_code}: {mapping.error}")

        # Add next steps
        report_lines.extend(
            [
                "",
                "## Next Steps",
                "",
                "- Review and verify supplier contact information",
            ]
        )

        if successful_mappings > 0:
            report_lines.append("- Review product cost prices and lead times")
            report_lines.append(
                "- Use `review_urgent_order_requirements` to check reorder needs"
            )
        else:
            report_lines.append(
                "- Use `create_products` to add products for this supplier"
            )
            report_lines.append("- Link existing products using product update tools")

        report = "\n".join(report_lines)

        logger.info(
            f"Supplier onboarding complete: {request.supplier_code} "
            f"({successful_mappings}/{len(request.product_mappings)} mappings)"
        )
        return report

    except Exception as e:
        logger.error(f"Failed to create supplier {request.supplier_code}: {e}")
        raise


@observe_tool
async def create_supplier_with_products(
    request: CreateSupplierWithProductsRequest, ctx: Context
) -> str:
    """Onboard a new supplier with complete configuration and product mappings.

    This workflow tool creates a new supplier with full contact and address details,
    then establishes mappings between the supplier and specified products. The
    operation follows a transactional approach:

    1. Create the supplier with all configuration details
    2. If supplier creation succeeds, create product-supplier mappings
    3. If supplier creation fails, no mappings are attempted

    Individual mapping failures are logged but don't fail the entire operation,
    allowing partial success when some products don't exist or have issues.

    ## How It Works

    1. Creates supplier record with contact and address information
    2. For each product mapping:
       - Fetches existing product details
       - Adds supplier to product's supplier list
       - Updates cost price if provided
    3. Returns markdown report with detailed results

    ## Use Cases

    - **Onboard new suppliers**: Complete setup with contact details and address
    - **Supplier relationships**: Link suppliers to their product catalog
    - **Cost management**: Set initial cost prices during onboarding
    - **Lead time setup**: Configure default lead times for planning

    ## Typical Workflow

    1. Create supplier with contact and address details
    2. Link to existing products or plan to add new products
    3. Review product mappings and costs
    4. Use `review_urgent_order_requirements` to check reorder needs

    ## Advantages Over Manual Approach

    **Manual Approach** (5-10 API calls):
    - Create supplier (1 API call)
    - For each product: fetch product, update product with supplier (2 calls x N products)
    - No validation or error handling
    - Results scattered across multiple responses

    **Workflow Tool** (1 call):
    - All operations in single tool invocation
    - Automatic error handling per product
    - Success/failure summary
    - Actionable markdown report with next steps

    Args:
        request: Request with supplier details and optional product mappings
        ctx: Server context with StockTrimClient

    Returns:
        Markdown report with supplier details and mapping results

    Example:
        Request: {
            "supplier_code": "SUP-NEW",
            "supplier_name": "New Supplier Inc",
            "email_address": "orders@newsupplier.com",
            "primary_contact_name": "Jane Smith",
            "default_lead_time": 14,
            "street_address": "123 Main St",
            "city": "Portland",
            "state": "OR",
            "country": "USA",
            "post_code": "97201",
            "product_mappings": [
                {
                    "product_code": "WIDGET-001",
                    "supplier_product_code": "NS-WIDGET-001",
                    "cost_price": 15.50
                }
            ]
        }

    See Also:
        - `review_urgent_order_requirements`: Check reorder needs by supplier
        - `generate_purchase_orders_from_urgent_items`: Generate POs for supplier
        - `list_suppliers`: View all suppliers
        - `get_supplier`: Get supplier details
    """
    return await _create_supplier_with_products_impl(request, ctx)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register supplier onboarding workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(create_supplier_with_products)
