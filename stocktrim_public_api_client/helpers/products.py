"""Product catalog operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.products import (
    delete_api_products,
    get_api_products,
    post_api_products,
)
from stocktrim_public_api_client.generated.models.products_request_dto import (
    ProductsRequestDto,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Products(Base):
    """Product catalog management.

    Provides operations for managing products in StockTrim.
    """

    async def get_all(
        self,
        code: str | Unset = UNSET,
        page_no: str | Unset = UNSET,
    ) -> list[ProductsResponseDto]:
        """Get all products, optionally filtered by exact code match or page.

        Args:
            code: Optional product code for exact match filtering. The StockTrim API
                only supports exact code matches, not prefix or partial matching.
            page_no: Optional page number for pagination.

        Returns:
            List of ProductsResponseDto objects. Returns empty list if no products
            match the filter.

        Example:
            >>> products = await client.products.get_all()
            >>> products = await client.products.get_all(
            ...     code="WIDGET-001"
            ... )  # Exact match only
        """
        response = await get_api_products.asyncio_detailed(
            client=self._client,
            code=code,
            page_no=page_no,
        )
        # StockTrim API returns 404 when no products match the exact code filter.
        # This is non-standard REST behavior (should be 200 with empty array), but we handle it
        # by treating 404 as "no results" and returning an empty list for a consistent interface.
        # Note: The API only supports exact code matching, not prefix/partial matching.
        if response.status_code == 404:
            return []
        result = unwrap(response)
        # unwrap() returns the actual type or raises an exception on error
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def create(self, product: ProductsRequestDto) -> ProductsResponseDto:
        """Create a new product.

        Args:
            product: Product data to create.

        Returns:
            Created ProductsResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     ProductsRequestDto,
            ... )
            >>> product = await client.products.create(
            ...     ProductsRequestDto(code="WIDGET-001", description="Widget")
            ... )
        """
        response = await post_api_products.asyncio_detailed(
            client=self._client,
            body=product,
        )
        return cast(ProductsResponseDto, unwrap(response))

    async def delete(self, product_id: str | Unset = UNSET) -> None:
        """Delete product(s).

        Args:
            product_id: Optional product ID to delete. If not provided, may delete
                all products (use with caution).

        Example:
            >>> await client.products.delete(product_id="123")
        """
        await delete_api_products.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )

    # Convenience methods

    async def find_by_code(self, code: str) -> ProductsResponseDto | None:
        """Find a single product by exact code match.

        This is a convenience method that wraps get_all() and returns the first
        matching product or None if not found.

        Args:
            code: The exact product code to search for.

        Returns:
            ProductsResponseDto if found, None otherwise.

        Example:
            >>> product = await client.products.find_by_code("WIDGET-001")
            >>> if product:
            ...     print(f"Found: {product.description}")
        """
        products = await self.get_all(code=code)
        return products[0] if products else None

    async def find_by_exact_code(self, code: str) -> list[ProductsResponseDto]:
        """Find products by exact code match, returning a list.

        This method provides the same functionality as find_by_code() but returns
        a list for consistency with search patterns. Since the API only supports
        exact matching, this will return 0 or 1 products.

        Args:
            code: The exact product code to search for.

        Returns:
            List containing the matching product (0 or 1 item).

        Example:
            >>> products = await client.products.find_by_exact_code("WIDGET-001")
            >>> if products:
            ...     print(f"Found: {products[0].description}")
        """
        return await self.get_all(code=code)

    async def exists(self, code: str) -> bool:
        """Check if a product with given code exists.

        Args:
            code: The product code to check.

        Returns:
            True if product exists, False otherwise.

        Example:
            >>> if await client.products.exists("WIDGET-001"):
            ...     print("Product already exists")
        """
        product = await self.find_by_code(code)
        return product is not None

    async def get_all_paginated(self) -> list[ProductsResponseDto]:
        """Get ALL products by paginating through all pages.

        This method automatically handles pagination to fetch the complete
        product catalog from StockTrim.

        Returns:
            List of all ProductsResponseDto objects across all pages.

        Example:
            >>> all_products = await client.products.get_all_paginated()
            >>> print(f"Total products: {len(all_products)}")
        """
        all_products = []
        page_no = "0"

        while True:
            products_page = await self.get_all(page_no=page_no)
            if not products_page:
                break

            all_products.extend(products_page)

            # StockTrim API uses string page numbers and doesn't document pagination
            # We'll assume if we get fewer results, we're done
            # Typical page size appears to be 50
            if len(products_page) < 50:
                break

            page_no = str(int(page_no) + 1)

        return all_products
