"""Purchase order operations."""

from __future__ import annotations

from typing import Any, cast

from stocktrim_public_api_client.generated.api.purchase_orders import (
    delete_api_purchase_orders,
    get_api_purchase_orders,
    post_api_purchase_orders,
)
from stocktrim_public_api_client.generated.models.purchase_order_request_dto import (
    PurchaseOrderRequestDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_response_dto import (
    PurchaseOrderResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class PurchaseOrders(Base):
    """Purchase order management."""

    async def list(self, **filters: Any) -> list[PurchaseOrderResponseDto]:
        """List all purchase orders.

        Args:
            **filters: Optional filtering parameters.

        Returns:
            List of PurchaseOrderResponseDto objects.

        Example:
            >>> purchase_orders = await client.purchase_orders.list()
        """
        response = await get_api_purchase_orders.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def get(self, reference_number: str) -> PurchaseOrderResponseDto:
        """Get a specific purchase order.

        Args:
            reference_number: The purchase order reference number.

        Returns:
            PurchaseOrderResponseDto object.

        Example:
            >>> order = await client.purchase_orders.get("PO-001")
        """
        response = await get_api_purchase_orders.asyncio_detailed(
            client=self._client,
            reference_number=reference_number,
        )
        result = unwrap(response)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return cast(PurchaseOrderResponseDto, result)

    async def create(
        self, order_data: PurchaseOrderRequestDto
    ) -> PurchaseOrderResponseDto:
        """Create a new purchase order.

        Args:
            order_data: PurchaseOrderRequestDto model with order details.

        Returns:
            PurchaseOrderResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     PurchaseOrderRequestDto,
            ... )
            >>> order = await client.purchase_orders.create(
            ...     PurchaseOrderRequestDto(reference_number="PO-001", ...)
            ... )
        """
        response = await post_api_purchase_orders.asyncio_detailed(
            client=self._client,
            body=order_data,
        )
        return cast(PurchaseOrderResponseDto, unwrap(response))

    async def delete(self, reference_number: str) -> None:
        """Delete a purchase order.

        Args:
            reference_number: The purchase order reference number to delete.

        Example:
            >>> await client.purchase_orders.delete("PO-001")
        """
        await delete_api_purchase_orders.asyncio_detailed(
            client=self._client,
            reference_number=reference_number,
        )
