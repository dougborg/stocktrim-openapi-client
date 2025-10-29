"""Sales order operations."""

from __future__ import annotations

from typing import Any, cast

from stocktrim_public_api_client.generated.api.sales_orders import (
    delete_api_sales_orders,
    get_api_sales_orders,
    post_api_sales_orders,
)
from stocktrim_public_api_client.generated.models.sales_order_request_dto import (
    SalesOrderRequestDto,
)
from stocktrim_public_api_client.generated.models.sales_order_response_dto import (
    SalesOrderResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class SalesOrders(Base):
    """Sales order management."""

    async def list(self, **filters: Any) -> list[SalesOrderResponseDto]:
        """List all sales orders.

        Args:
            **filters: Optional filtering parameters.

        Returns:
            List of SalesOrderResponseDto objects.

        Example:
            >>> sales_orders = await client.sales_orders.list()
        """
        response = await get_api_sales_orders.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def get(self, product_id: str) -> list[SalesOrderResponseDto]:
        """Get sales orders filtered by product ID.

        Args:
            product_id: The product ID to filter by.

        Returns:
            List of SalesOrderResponseDto objects.

        Example:
            >>> orders = await client.sales_orders.get("prod-123")
        """
        response = await get_api_sales_orders.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def create(self, order_data: SalesOrderRequestDto) -> SalesOrderResponseDto:
        """Create a new sales order.

        Args:
            order_data: SalesOrderRequestDto model with order details.

        Returns:
            SalesOrderResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SalesOrderRequestDto,
            ... )
            >>> order = await client.sales_orders.create(
            ...     SalesOrderRequestDto(order_number="SO-001", ...)
            ... )
        """
        response = await post_api_sales_orders.asyncio_detailed(
            client=self._client,
            body=order_data,
        )
        return cast(SalesOrderResponseDto, unwrap(response))

    async def delete(self, product_id: str | None = None) -> None:
        """Delete sales orders, optionally filtered by product ID.

        Args:
            product_id: Optional product ID to filter deletions.

        Example:
            >>> await client.sales_orders.delete(product_id="prod-123")
        """
        await delete_api_sales_orders.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )
