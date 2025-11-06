"""Sales order operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.sales_orders import (
    delete_api_sales_orders,
    get_api_sales_orders,
)
from stocktrim_public_api_client.generated.api.sales_orders_bulk import (
    put_api_sales_orders_bulk,
)
from stocktrim_public_api_client.generated.models.sales_order_request_dto import (
    SalesOrderRequestDto,
)
from stocktrim_public_api_client.generated.models.sales_order_response_dto import (
    SalesOrderResponseDto,
)
from stocktrim_public_api_client.generated.models.sales_order_with_line_items_request_dto import (
    SalesOrderWithLineItemsRequestDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class SalesOrders(Base):
    """Sales order management.

    Provides operations for managing sales orders in StockTrim.
    """

    async def get_all(
        self,
        product_id: str | Unset = UNSET,
    ) -> list[SalesOrderResponseDto]:
        """Get all sales orders, optionally filtered by product ID.

        Args:
            product_id: Optional product ID to filter by.

        Returns:
            List of SalesOrderResponseDto objects.

        Example:
            >>> orders = await client.sales_orders.get_all()
            >>> orders = await client.sales_orders.get_all(product_id="123")
        """
        response = await get_api_sales_orders.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )
        result = unwrap(response)
        # unwrap() returns the actual type or raises an exception on error
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def create(self, order: SalesOrderRequestDto) -> SalesOrderResponseDto:
        """Create a new sales order using the idempotent bulk endpoint.

        This method uses PUT /SalesOrdersBulk which is idempotent and safer for retries.
        It performs a create or update based on the `external_reference_id` field of
        the line item (`SalesOrderRequestDto`). The bulk request does not include an
        external reference ID at the header level; the API uses the value from the
        line item to determine whether to create or update.

        Args:
            order: Sales order data to create. Include `external_reference_id` for
                idempotent behavior.

        Returns:
            Created SalesOrderResponseDto object.

        Example:
            >>> from datetime import datetime
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SalesOrderRequestDto,
            ... )
            >>> order = await client.sales_orders.create(
            ...     SalesOrderRequestDto(
            ...         product_id="WIDGET-001",
            ...         order_date=datetime.now(),
            ...         quantity=10.0,
            ...         external_reference_id="SO-001",
            ...     )
            ... )
        """
        # Convert single order to bulk request with one line item
        bulk_request = SalesOrderWithLineItemsRequestDto(
            order_date=order.order_date,
            location_code=order.location_code,
            location_name=order.location_name,
            customer_code=order.customer_code,
            customer_name=order.customer_name,
            sale_order_line_items=[order],
        )
        response = await put_api_sales_orders_bulk.asyncio_detailed(
            client=self._client,
            body=bulk_request,
        )
        return cast(SalesOrderResponseDto, unwrap(response))

    async def delete(self, product_id: str | Unset = UNSET) -> None:
        """Delete sales order(s), optionally filtered by product ID.

        Args:
            product_id: Optional product ID to filter deletions.

        Example:
            >>> await client.sales_orders.delete(product_id="123")
        """
        await delete_api_sales_orders.asyncio_detailed(
            client=self._client,
            product_id=product_id,
        )

    # Convenience methods

    async def get_for_product(self, product_id: str) -> list[SalesOrderResponseDto]:
        """Get all sales orders for a specific product.

        This is a convenience alias for get_all() with clearer intent.

        Args:
            product_id: The product ID to get orders for.

        Returns:
            List of SalesOrderResponseDto objects for the product.

        Example:
            >>> orders = await client.sales_orders.get_for_product("123")
        """
        return await self.get_all(product_id=product_id)

    async def delete_for_product(self, product_id: str) -> None:
        """Delete all sales orders for a specific product.

        This is a convenience alias for delete() with clearer intent.

        Args:
            product_id: The product ID to delete orders for.

        Example:
            >>> await client.sales_orders.delete_for_product("123")
        """
        await self.delete(product_id=product_id)
