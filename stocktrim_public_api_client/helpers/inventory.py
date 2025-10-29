"""Inventory operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.inventory import post_api_inventory
from stocktrim_public_api_client.generated.models.inventory import (
    Inventory as InventoryItem,
)
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

    # Convenience methods

    async def set_for_product(
        self,
        product_id: str,
        stock_on_hand: float | Unset = UNSET,
        stock_on_order: float | Unset = UNSET,
        location_code: str | None | Unset = UNSET,
        location_name: str | None | Unset = UNSET,
    ) -> PurchaseOrderResponseDto:
        """Set inventory levels for a single product.

        This is a convenience method that simplifies setting inventory for
        a single product by automatically creating the required request structure.

        Args:
            product_id: The product ID to set inventory for.
            stock_on_hand: Stock on hand quantity.
            stock_on_order: Stock on order quantity.
            location_code: Optional location code.
            location_name: Optional location name.

        Returns:
            PurchaseOrderResponseDto object (API inconsistency).

        Example:
            >>> result = await client.inventory.set_for_product(
            ...     product_id="123",
            ...     stock_on_hand=50.0,
            ...     stock_on_order=100.0,
            ...     location_code="WAREHOUSE-A",
            ... )
        """
        inventory_item = InventoryItem(
            product_id=product_id,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
            location_code=location_code,
            location_name=location_name,
        )

        request = SetInventoryRequest(inventory=[inventory_item])
        return await self.set(request)
