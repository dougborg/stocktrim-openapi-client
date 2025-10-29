"""Inventory operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.generated.api.inventory import post_api_inventory
from stocktrim_public_api_client.generated.models.purchase_order_response_dto import (
    PurchaseOrderResponseDto,
)
from stocktrim_public_api_client.generated.models.set_inventory_request import (
    SetInventoryRequest,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Inventory(Base):
    """Inventory management.

    Provides operations for managing inventory levels in StockTrim.
    """

    async def set(self, inventory: SetInventoryRequest) -> PurchaseOrderResponseDto:
        """Set stock on hand and stock on order for products.

        Note: The API returns PurchaseOrderResponseDto which seems incorrect
        for an inventory operation, but we preserve the API's behavior here.

        Args:
            inventory: Inventory data to set.

        Returns:
            PurchaseOrderResponseDto object (API inconsistency).

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SetInventoryRequest,
            ... )
            >>> result = await client.inventory.set(
            ...     SetInventoryRequest(product_code="WIDGET-001", quantity=100)
            ... )
        """
        response = await post_api_inventory.asyncio_detailed(
            client=self._client,
            body=inventory,
        )
        return cast(PurchaseOrderResponseDto, unwrap(response))
