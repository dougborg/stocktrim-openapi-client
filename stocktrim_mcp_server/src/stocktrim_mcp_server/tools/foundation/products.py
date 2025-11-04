"""Product management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services

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


async def get_product(
    request: GetProductRequest, context: Context
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
        code=product.code or "",
        description=product.description,
        unit_of_measurement=product.unit_of_measurement,
        is_active=product.is_active or False,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
    )


# ============================================================================
# Tool 2: search_products
# ============================================================================


class SearchProductsRequest(BaseModel):
    """Request model for searching products."""

    prefix: str = Field(..., description="Product code prefix to search for")


class SearchProductsResponse(BaseModel):
    """Response containing matching products."""

    products: list[ProductInfo]
    total_count: int


async def search_products(
    request: SearchProductsRequest, context: Context
) -> SearchProductsResponse:
    """Search for products by code prefix.

    This tool finds all products whose code starts with the given prefix.
    Useful for discovering products in a category or product line.

    Args:
        request: Request containing search prefix
        context: Server context with StockTrimClient

    Returns:
        SearchProductsResponse with matching products

    Example:
        Request: {"prefix": "WIDGET"}
        Returns: {"products": [...], "total_count": 5}
    """
    services = get_services(context)
    products = await services.products.search(request.prefix)

    # Build response
    product_infos = [
        ProductInfo(
            code=p.code or "",
            description=p.description,
            unit_of_measurement=p.unit_of_measurement,
            is_active=p.is_active or False,
            cost_price=p.cost_price,
            selling_price=p.selling_price,
        )
        for p in products
    ]

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


async def create_product(
    request: CreateProductRequest, context: Context
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
        code=created_product.code or "",
        description=created_product.description,
        unit_of_measurement=created_product.unit_of_measurement,
        is_active=created_product.is_active or False,
        cost_price=created_product.cost_price,
        selling_price=created_product.selling_price,
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


async def delete_product(
    request: DeleteProductRequest, context: Context
) -> DeleteProductResponse:
    """Delete a product by code.

    This tool deletes a product from StockTrim inventory.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        DeleteProductResponse indicating success

    Example:
        Request: {"code": "WIDGET-001"}
        Returns: {"success": true, "message": "Product WIDGET-001 deleted successfully"}
    """
    services = get_services(context)
    success, message = await services.products.delete(request.code)

    return DeleteProductResponse(
        success=success,
        message=message,
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
