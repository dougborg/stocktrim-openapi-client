"""Product management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

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


async def _get_product_impl(
    request: GetProductRequest, context: Context
) -> ProductInfo | None:
    """Implementation of get_product tool.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        ProductInfo if found, None otherwise

    Raises:
        ValueError: If product code is empty or invalid
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Product code cannot be empty")

    logger.info(f"Getting product: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the find_by_code convenience method
        product = await client.products.find_by_code(request.code)

        if not product:
            logger.warning(f"Product not found: {request.code}")
            return None

        # Build ProductInfo from response
        product_info = ProductInfo(
            code=product.code or "",
            description=product.description,
            unit_of_measurement=product.unit_of_measurement,
            is_active=product.is_active or False,
            cost_price=product.cost_price,
            selling_price=product.selling_price,
        )

        logger.info(f"Product retrieved: {request.code}")
        return product_info

    except Exception as e:
        logger.error(f"Failed to get product {request.code}: {e}")
        raise


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
    return await _get_product_impl(request, context)


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


async def _search_products_impl(
    request: SearchProductsRequest, context: Context
) -> SearchProductsResponse:
    """Implementation of search_products tool.

    Args:
        request: Request containing search prefix
        context: Server context with StockTrimClient

    Returns:
        SearchProductsResponse with matching products

    Raises:
        ValueError: If prefix is empty
        Exception: If API call fails
    """
    if not request.prefix or not request.prefix.strip():
        raise ValueError("Search prefix cannot be empty")

    logger.info(f"Searching products with prefix: {request.prefix}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Use the search convenience method
        products = await client.products.search(request.prefix)

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

        response = SearchProductsResponse(
            products=product_infos,
            total_count=len(product_infos),
        )

        logger.info(
            f"Found {response.total_count} products matching prefix: {request.prefix}"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to search products with prefix {request.prefix}: {e}")
        raise


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
    return await _search_products_impl(request, context)


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


async def _create_product_impl(
    request: CreateProductRequest, context: Context
) -> ProductInfo:
    """Implementation of create_product tool.

    Args:
        request: Request containing product details
        context: Server context with StockTrimClient

    Returns:
        ProductInfo for the created product

    Raises:
        ValueError: If required fields are missing
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Product code cannot be empty")
    if not request.description or not request.description.strip():
        raise ValueError("Product description cannot be empty")

    logger.info(f"Creating product: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Import ProductsRequestDto from generated models
        from stocktrim_public_api_client.generated.models import ProductsRequestDto

        # Create product DTO
        # Note: product_id is the internal ID - we use the code as product_code_readable
        product_dto = ProductsRequestDto(
            product_id=request.code,  # Use code as the product ID for creation
            product_code_readable=request.code,
            name=request.description,
            cost=request.cost_price,
            price=request.selling_price,
        )

        # Create product (API accepts single object, not list)
        created_product = await client.products.create(product_dto)

        if not created_product:
            raise Exception(f"Failed to create product {request.code}")

        # Build ProductInfo from response
        product_info = ProductInfo(
            code=created_product.code or "",
            description=created_product.description,
            unit_of_measurement=created_product.unit_of_measurement,
            is_active=created_product.is_active or False,
            cost_price=created_product.cost_price,
            selling_price=created_product.selling_price,
        )

        logger.info(f"Product created: {request.code}")
        return product_info

    except Exception as e:
        logger.error(f"Failed to create product {request.code}: {e}")
        raise


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
    return await _create_product_impl(request, context)


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


async def _delete_product_impl(
    request: DeleteProductRequest, context: Context
) -> DeleteProductResponse:
    """Implementation of delete_product tool.

    Args:
        request: Request containing product code
        context: Server context with StockTrimClient

    Returns:
        DeleteProductResponse indicating success

    Raises:
        ValueError: If product code is empty
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Product code cannot be empty")

    logger.info(f"Deleting product: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Check if product exists first
        product = await client.products.find_by_code(request.code)
        if not product:
            return DeleteProductResponse(
                success=False,
                message=f"Product {request.code} not found",
            )

        # Delete product
        await client.products.delete(request.code)

        logger.info(f"Product deleted: {request.code}")
        return DeleteProductResponse(
            success=True,
            message=f"Product {request.code} deleted successfully",
        )

    except Exception as e:
        logger.error(f"Failed to delete product {request.code}: {e}")
        raise


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
    return await _delete_product_impl(request, context)


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
