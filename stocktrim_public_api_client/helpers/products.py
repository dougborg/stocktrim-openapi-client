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
        """Get all products, optionally filtered by code or page.

        Args:
            code: Optional product code filter.
            page_no: Optional page number for pagination.

        Returns:
            List of ProductsResponseDto objects.

        Example:
            >>> products = await client.products.get_all()
            >>> products = await client.products.get_all(code="WIDGET")
        """
        response = await get_api_products.asyncio_detailed(
            client=self._client,
            code=code,
            page_no=page_no,
        )
        result = unwrap(response)
        return result if isinstance(result, list) else []

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
