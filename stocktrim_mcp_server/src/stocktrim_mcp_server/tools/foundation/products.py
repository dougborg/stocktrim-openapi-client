"""Product management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params
from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria import (
    OrderPlanFilterCriteria,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: get_product
# ============================================================================


class GetProductRequest(BaseModel):
    """Request model for getting a product."""

    code: str = Field(..., description="Product code to retrieve")


class ProductInfo(BaseModel):
    """Product information."""

    code: str
    description: str | None
    unit_of_measurement: str | None
    is_active: bool
    cost_price: float | None
    selling_price: float | None


@unpack_pydantic_params
async def get_product(
    request: Annotated[GetProductRequest, Unpack()], context: Context
) -> ProductInfo | None:
    """Get a product by code.

    This tool retrieves detailed information about a specific product
    from StockTrim inventory.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        ProductInfo if found, None if not found

    Example:
        Request: {"code": "WIDGET-001"}
        Returns: {"code": "WIDGET-001", "description": "Widget", ...}
    """
    services = get_services(context)
    product = await services.products.get_by_code(request.code)

    if not product:
        return None

    # Build ProductInfo from response
    return ProductInfo(
        code=product.product_code_readable or product.product_id or "",
        description=product.name,
        unit_of_measurement=None,  # Not available in ProductsResponseDto
        is_active=not (product.discontinued or False),
        cost_price=product.cost if not isinstance(product.cost, Unset) else None,
        selling_price=product.price if not isinstance(product.price, Unset) else None,
    )


# ============================================================================
# Tool 2: search_products
# ============================================================================


class SearchProductsRequest(BaseModel):
    """Request model for searching products."""

    search_query: str = Field(
        ..., description="Search query for product name, code, or category"
    )


class SearchProductsResponse(BaseModel):
    """Response containing matching products."""

    products: list[ProductInfo]
    total_count: int


@unpack_pydantic_params
async def search_products(
    request: Annotated[SearchProductsRequest, Unpack()], context: Context
) -> SearchProductsResponse:
    """Search for products by name, code, or category keywords.

    This tool searches across product fields (name, code, category) using
    the StockTrim Order Plan API's searchString parameter. Useful for finding
    products when you don't know the exact product code.

    Search matches against:
    - Product names (e.g., "blue widget")
    - Product codes (e.g., "WIDG" matches "WIDGET-001")
    - Categories (e.g., "electronics")
    - Other product attributes

    Args:
        request: Request containing search query
        context: Server context with StockTrimClient

    Returns:
        SearchProductsResponse with matching products

    Example:
        search_query="blue widget"
        Returns: {"products": [{"code": "WIDGET-001", "description": "Blue Widget", ...}], "total_count": 1}

        search_query="electronics"
        Returns: {"products": [...], "total_count": 15}
    """
    services = get_services(context)

    # Use Order Plan API with searchString filter for keyword search
    filter_criteria = OrderPlanFilterCriteria(
        search_string=request.search_query,
    )

    # Query order plan which searches across product fields
    order_plan_results = await services.client.order_plan.query(filter_criteria)

    # Build response from order plan results, filtering out items without product codes
    product_infos = []
    for item in order_plan_results:
        # Skip items without a valid product code
        if item.product_code in (None, UNSET, ""):
            continue

        product_infos.append(
            ProductInfo(
                code=item.product_code,
                description=item.name if item.name not in (None, UNSET) else None,
                unit_of_measurement=None,  # Not available in SkuOptimizedResultsDto
                is_active=not (item.is_discontinued or False),
                cost_price=item.sku_cost
                if item.sku_cost not in (None, UNSET)
                else None,
                selling_price=item.sku_price
                if item.sku_price not in (None, UNSET)
                else None,
            )
        )

    return SearchProductsResponse(
        products=product_infos,
        total_count=len(product_infos),
    )


# ============================================================================
# Tool 3: create_product
# ============================================================================


class CreateProductRequest(BaseModel):
    """Request model for creating a product."""

    code: str = Field(..., description="Unique product code")
    description: str = Field(..., description="Product description")
    unit_of_measurement: str | None = Field(
        default=None, description="Unit of measurement (e.g., 'EA', 'KG')"
    )
    is_active: bool = Field(default=True, description="Whether product is active")
    cost_price: float | None = Field(default=None, description="Cost price")
    selling_price: float | None = Field(default=None, description="Selling price")


@unpack_pydantic_params
async def create_product(
    request: Annotated[CreateProductRequest, Unpack()], context: Context
) -> ProductInfo:
    """Create a new product.

    This tool creates a new product in StockTrim inventory.

    Args:
        request: Request containing product details
        context: Server context with StockTrimClient

    Returns:
        ProductInfo for the created product

    Example:
        Request: {"code": "WIDGET-001", "description": "Blue Widget", "unit_of_measurement": "EA"}
        Returns: {"code": "WIDGET-001", "description": "Blue Widget", ...}
    """
    services = get_services(context)
    created_product = await services.products.create(
        code=request.code,
        description=request.description,
        cost_price=request.cost_price,
        selling_price=request.selling_price,
    )

    # Build ProductInfo from response
    return ProductInfo(
        code=created_product.product_code_readable or created_product.product_id or "",
        description=created_product.name,
        unit_of_measurement=None,
        is_active=not (created_product.discontinued or False),
        cost_price=created_product.cost
        if not isinstance(created_product.cost, Unset)
        else None,
        selling_price=created_product.price
        if not isinstance(created_product.price, Unset)
        else None,
    )


# ============================================================================
# Tool 4: delete_product
# ============================================================================


class DeleteProductRequest(BaseModel):
    """Request model for deleting a product."""

    code: str = Field(..., description="Product code to delete")


class DeleteProductResponse(BaseModel):
    """Response for product deletion."""

    success: bool
    message: str


@unpack_pydantic_params
async def delete_product(
    request: Annotated[DeleteProductRequest, Unpack()], context: Context
) -> DeleteProductResponse:
    """Delete a product by code.

    🔴 HIGH-RISK OPERATION: This action permanently deletes product data
    and cannot be undone. User confirmation is required via elicitation.

    This tool deletes a product from StockTrim inventory after obtaining
    explicit user confirmation through the MCP elicitation protocol.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        DeleteProductResponse indicating success or cancellation

    Example:
        Request: {"code": "WIDGET-001"}
        Returns: {"success": true, "message": "Product WIDGET-001 deleted successfully"}
                 or {"success": false, "message": "Deletion cancelled by user"}
    """
    services = get_services(context)

    # Get product details for preview
    product = await services.products.get_by_code(request.code)

    if not product:
        return DeleteProductResponse(
            success=False,
            message=f"Product not found: {request.code}",
        )

    # Build preview information
    product_code = product.product_code_readable or product.product_id or request.code
    product_name = product.name or "Unnamed Product"
    status_emoji = "🔴" if product.discontinued else "🟢"
    status_text = "Discontinued" if product.discontinued else "Active"

    # Request user confirmation via elicitation
    result = await context.elicit(
        message=f"""⚠️ Delete product {product_code}?

{status_emoji} **{product_name}**
Status: {status_text}

This action will permanently delete the product and cannot be undone.

Proceed with deletion?""",
        response_type=None,  # Simple yes/no approval
    )

    # Handle elicitation response
    match result:
        case AcceptedElicitation():
            # User confirmed - proceed with deletion
            success, message = await services.products.delete(request.code)
            return DeleteProductResponse(
                success=success,
                message=f"✅ {message}" if success else message,
            )

        case DeclinedElicitation():
            # User declined
            return DeleteProductResponse(
                success=False,
                message=f"❌ Deletion of product {product_code} declined by user",
            )

        case CancelledElicitation():
            # User cancelled
            return DeleteProductResponse(
                success=False,
                message=f"❌ Deletion of product {product_code} cancelled by user",
            )

        case _:
            # Unexpected response type
            return DeleteProductResponse(
                success=False,
                message=f"Unexpected elicitation response for product {product_code}",
            )


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register product tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(get_product)
    mcp.tool()(search_products)
    mcp.tool()(create_product)
    mcp.tool()(delete_product)
