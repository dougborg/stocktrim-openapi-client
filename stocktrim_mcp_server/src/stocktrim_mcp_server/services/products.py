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

    async def list_all(self) -> list[ProductsResponseDto]:
        """List all products.

        Returns:
            List of all products

        Raises:
            Exception: If API call fails
        """
        logger.info("Listing all products")

        products = await self._client.products.get_all()

        logger.info(f"Found {len(products)} products")
        return products

    async def find_by_exact_code(self, code: str) -> list[ProductsResponseDto]:
        """Find products by exact code match.

        Note: The StockTrim Products API only supports exact code matching,
        not prefix or partial matching. For keyword search functionality,
        use the Order Plan API.

        Args:
            code: Exact product code to search for

        Returns:
            List of matching products (0 or 1 item for exact match)

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Product code")
        logger.info(f"Finding product with exact code: {code}")

        products = await self._client.products.find_by_exact_code(code)

        logger.info(f"Found {len(products)} products matching code: {code}")
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
        # Note: StockTrim API requires both product_id and product_code_readable.
        # - product_id: Internal unique identifier (required, used as primary key)
        # - product_code_readable: Display/reference code (optional/nullable, shown to users)
        #   While technically optional, it's recommended to provide this for better UX
        # We set both to the same value (code) since:
        # 1. Users think of "code" as the primary identifier
        # 2. This ensures consistent IDs that match the user-facing code
        product_dto = ProductsRequestDto(
            product_id=code,  # Internal ID (must match user code for consistency)
            product_code_readable=code,  # User-facing code
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
