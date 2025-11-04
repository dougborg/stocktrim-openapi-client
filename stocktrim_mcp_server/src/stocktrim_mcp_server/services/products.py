"""Product management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import ProductsResponseDto

logger = logging.getLogger(__name__)


class ProductService(BaseService):
    """Service for product management operations."""

    async def get_by_code(self, code: str) -> ProductsResponseDto | None:
        """Get a single product by code.

        Args:
            code: Product code

        Returns:
            Product details if found, None otherwise

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Product code")
        logger.info(f"Getting product: {code}")

        product = await self._client.products.find_by_code(code)

        if not product:
            logger.warning(f"Product not found: {code}")
            return None

        logger.info(f"Product retrieved: {code}")
        return product

    async def search(self, prefix: str) -> list[ProductsResponseDto]:
        """Search products by code prefix.

        Args:
            prefix: Product code prefix to search for

        Returns:
            List of matching products

        Raises:
            ValueError: If prefix is empty
            Exception: If API call fails
        """
        self.validate_not_empty(prefix, "Search prefix")
        logger.info(f"Searching products with prefix: {prefix}")

        products = await self._client.products.search(prefix)

        logger.info(f"Found {len(products)} products matching prefix: {prefix}")
        return products

    async def create(
        self,
        code: str,
        description: str,
        cost_price: float | None = None,
        selling_price: float | None = None,
    ) -> ProductsResponseDto:
        """Create a new product.

        Args:
            code: Unique product code
            description: Product description
            cost_price: Cost price (optional)
            selling_price: Selling price (optional)

        Returns:
            Created product details

        Raises:
            ValueError: If required fields are empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Product code")
        self.validate_not_empty(description, "Product description")

        logger.info(f"Creating product: {code}")

        # Import ProductsRequestDto from generated models
        from stocktrim_public_api_client.generated.models import ProductsRequestDto

        # Create product DTO
        # Note: product_id is the internal ID - we use the code as product_code_readable
        product_dto = ProductsRequestDto(
            product_id=code,  # Use code as the product ID for creation
            product_code_readable=code,
            name=description,
            cost=cost_price,
            price=selling_price,
        )

        # Create product
        created_product = await self._client.products.create(product_dto)

        if not created_product:
            raise Exception(f"Failed to create product {code}")

        logger.info(f"Product created: {code}")
        return created_product

    async def delete(self, code: str) -> tuple[bool, str]:
        """Delete a product by code.

        Args:
            code: Product code to delete

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Product code")
        logger.info(f"Deleting product: {code}")

        # Check if product exists first
        product = await self._client.products.find_by_code(code)
        if not product:
            return False, f"Product {code} not found"

        # Delete product
        await self._client.products.delete(code)

        logger.info(f"Product deleted: {code}")
        return True, f"Product {code} deleted successfully"
