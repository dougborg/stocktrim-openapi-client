"""Supplier onboarding workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for onboarding new suppliers
with their associated product mappings.
"""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.product_supplier import (
    ProductSupplier,
)
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)
from stocktrim_public_api_client.generated.models.supplier_request_dto import (
    SupplierRequestDto,
)

logger = logging.getLogger(__name__)

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
    product_mappings: list[SupplierProductMapping] = Field(
        description="List of products to map to this supplier"
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
) -> CreateSupplierWithProductsResponse:
    """Implementation of create_supplier_with_products tool.

    Args:
        request: Request with supplier and product mapping details
        context: Server context with StockTrimClient

    Returns:
        CreateSupplierWithProductsResponse with creation results

    Raises:
        Exception: If supplier creation fails
    """
    logger.info(f"Creating supplier: {request.supplier_code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Step 1: Create the supplier first
        supplier_data = SupplierRequestDto(
            supplier_code=request.supplier_code,
            supplier_name=request.supplier_name,
        )

        created_supplier = await client.suppliers.create_one(supplier_data)

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
                existing_product = await client.products.find_by_code(
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

                await client.products.create(update_data)

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

        # Build response
        response = CreateSupplierWithProductsResponse(
            supplier_code=request.supplier_code,
            supplier_name=request.supplier_name,
            supplier_id=str(created_supplier.id)
            if created_supplier.id not in (None, UNSET)
            else None,
            mappings_attempted=len(request.product_mappings),
            mappings_successful=successful_mappings,
            mapping_details=mapping_details,
            message=f"Supplier '{request.supplier_code}' created successfully. "
            f"{successful_mappings}/{len(request.product_mappings)} product mappings completed.",
        )

        logger.info(
            f"Supplier onboarding complete: {request.supplier_code} "
            f"({successful_mappings}/{len(request.product_mappings)} mappings)"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to create supplier {request.supplier_code}: {e}")
        raise


async def create_supplier_with_products(
    request: CreateSupplierWithProductsRequest, context: Context
) -> CreateSupplierWithProductsResponse:
    """Onboard a new supplier with product mappings.

    This workflow tool creates a new supplier and establishes mappings between
    the supplier and specified products. The operation follows a transactional
    approach:

    1. Create the supplier first
    2. If supplier creation succeeds, create product-supplier mappings
    3. If supplier creation fails, no mappings are attempted

    Individual mapping failures are logged but don't fail the entire operation,
    allowing partial success when some products don't exist or have issues.

    Args:
        request: Request with supplier and product mapping details
        context: Server context with StockTrimClient

    Returns:
        CreateSupplierWithProductsResponse with detailed results

    Example:
        Request: {
            "supplier_code": "SUP-NEW",
            "supplier_name": "New Supplier Inc",
            "is_active": true,
            "product_mappings": [
                {
                    "product_code": "WIDGET-001",
                    "supplier_product_code": "SUP-SKU-001",
                    "cost_price": 15.50
                },
                {
                    "product_code": "WIDGET-002",
                    "supplier_product_code": "SUP-SKU-002",
                    "cost_price": 22.00
                }
            ]
        }
        Returns: {
            "supplier_code": "SUP-NEW",
            "supplier_name": "New Supplier Inc",
            "supplier_id": "123",
            "mappings_attempted": 2,
            "mappings_successful": 2,
            "mapping_details": [
                {"product_code": "WIDGET-001", "success": true},
                {"product_code": "WIDGET-002", "success": true}
            ],
            "message": "Supplier 'SUP-NEW' created successfully. 2/2 product mappings completed."
        }
    """
    return await _create_supplier_with_products_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register supplier onboarding workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(create_supplier_with_products)
