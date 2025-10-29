"""Product catalog operations."""

from __future__ import annotations

from typing import Any, cast

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

    Provides CRUD operations for products in StockTrim.

    Example:
        >>> async with StockTrimClient() as client:
        ...     products = await client.products.list()
        ...     product = await client.products.get("PROD-001")
        ...     await client.products.create(ProductsRequestDto(...))
        ...     await client.products.delete("PROD-001")
    """

    async def list(self, **filters: Any) -> list[ProductsResponseDto]:
        """List all products with optional filters.

        Args:
            **filters: Optional filtering parameters (e.g., code, page_no).

        Returns:
            List of ProductsResponseDto objects.

        Example:
            >>> products = await client.products.list()
            >>> products_filtered = await client.products.list(code="PROD")
        """
        response = await get_api_products.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def get(self, code: str) -> ProductsResponseDto:
        """Get a specific product by code.

        Args:
            code: The product code.

        Returns:
            ProductsResponseDto object.

        Example:
            >>> product = await client.products.get("PROD-001")
        """
        response = await get_api_products.asyncio_detailed(
            client=self._client,
            code=code,
        )
        result = unwrap(response)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return cast(ProductsResponseDto, result)

    async def create(self, product_data: ProductsRequestDto) -> ProductsResponseDto:
        """Create a new product.

        Args:
            product_data: ProductsRequestDto model with product details.

        Returns:
            ProductsResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     ProductsRequestDto,
            ... )
            >>> product = await client.products.create(
            ...     ProductsRequestDto(code="PROD-001", description="New Product")
            ... )
        """
        response = await post_api_products.asyncio_detailed(
            client=self._client,
            body=product_data,
        )
        return cast(ProductsResponseDto, unwrap(response))

    async def delete(self, product_id: str) -> None:
        """Delete a product.

        Args:
            product_id: The product ID to delete.

        Example:
            >>> await client.products.delete("prod-123")
        """
        await delete_api_products.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )
