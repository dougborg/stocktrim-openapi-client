"""Purchase order operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
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
    """Purchase order management.

    Provides operations for managing purchase orders in StockTrim.
    """

    async def get_all(
        self,
        reference_number: str | Unset = UNSET,
    ) -> PurchaseOrderResponseDto | list[PurchaseOrderResponseDto]:
        """Get purchase orders, optionally filtered by reference number.

        Note: The API returns a single object when filtered by reference number,
        but this is inconsistent with other endpoints. We preserve the API's
        behavior here.

        Args:
            reference_number: Optional reference number filter.

        Returns:
            PurchaseOrderResponseDto or list of PurchaseOrderResponseDto objects.

        Example:
            >>> orders = await client.purchase_orders.get_all()
            >>> order = await client.purchase_orders.get_all(reference_number="PO-001")
        """
        response = await get_api_purchase_orders.asyncio_detailed(
            client=self._client,
            reference_number=reference_number,
        )
        return cast(
            PurchaseOrderResponseDto | list[PurchaseOrderResponseDto],
            unwrap(response),
        )

    async def create(self, order: PurchaseOrderRequestDto) -> PurchaseOrderResponseDto:
        """Create a new purchase order.

        Args:
            order: Purchase order data to create.

        Returns:
            Created PurchaseOrderResponseDto object.

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
            body=order,
        )
        return cast(PurchaseOrderResponseDto, unwrap(response))

    async def delete(
        self, reference_number: str | Unset = UNSET
    ) -> PurchaseOrderResponseDto | None:
        """Delete purchase order(s).

        Note: The API returns the deleted PurchaseOrderResponseDto object.

        Args:
            reference_number: Reference number to delete.

        Returns:
            Deleted PurchaseOrderResponseDto object or None.

        Example:
            >>> deleted = await client.purchase_orders.delete(reference_number="PO-001")
        """
        response = await delete_api_purchase_orders.asyncio_detailed(
            client=self._client,
            reference_number=reference_number,
        )
        result = unwrap(response)
        return cast(PurchaseOrderResponseDto, result) if result else None

    # Convenience methods

    async def find_by_reference(
        self, reference_number: str
    ) -> PurchaseOrderResponseDto | None:
        """Find a single purchase order by reference number.

        This method handles the API's inconsistent return type (single vs list)
        and always returns a single object or None.

        Args:
            reference_number: The purchase order reference number.

        Returns:
            PurchaseOrderResponseDto if found, None otherwise.

        Example:
            >>> order = await client.purchase_orders.find_by_reference("PO-001")
            >>> if order:
            ...     print(f"Found order: {order.reference_number}")
        """
        result = await self.get_all(reference_number=reference_number)
        # Handle API returning either single object or list
        if isinstance(result, list):
            return result[0] if result else None
        return result

    async def exists(self, reference_number: str) -> bool:
        """Check if a purchase order with given reference number exists.

        Args:
            reference_number: The reference number to check.

        Returns:
            True if order exists, False otherwise.

        Example:
            >>> if await client.purchase_orders.exists("PO-001"):
            ...     print("Purchase order exists")
        """
        order = await self.find_by_reference(reference_number)
        return order is not None
