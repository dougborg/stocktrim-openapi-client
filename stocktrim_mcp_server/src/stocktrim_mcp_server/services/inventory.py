"""Inventory management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.models import PurchaseOrderResponseDto

logger = logging.getLogger(__name__)


class InventoryService(BaseService):
    """Service for inventory management operations."""

    async def set_for_product(
        self,
        product_id: str,
        stock_on_hand: float | None = None,
        stock_on_order: float | None = None,
        location_code: str | None = None,
        location_name: str | None = None,
    ) -> PurchaseOrderResponseDto:
        """Set inventory levels for a product.

        Args:
            product_id: Product ID to set inventory for
            stock_on_hand: Current stock on hand quantity (optional)
            stock_on_order: Stock on order quantity (optional)
            location_code: Location code (optional)
            location_name: Location name (optional)

        Returns:
            PurchaseOrderResponseDto object (API inconsistency - API returns this
            type for inventory operations)

        Raises:
            ValueError: If product_id is empty
            Exception: If API call fails
        """
        self.validate_not_empty(product_id, "Product ID")
        logger.info(f"Setting inventory for product: {product_id}")

        # Convert None to UNSET for optional parameters
        stock_on_hand_param: float | Unset = (
            stock_on_hand if stock_on_hand is not None else UNSET
        )
        stock_on_order_param: float | Unset = (
            stock_on_order if stock_on_order is not None else UNSET
        )
        location_code_param: str | None | Unset = (
            location_code if location_code is not None else UNSET
        )
        location_name_param: str | None | Unset = (
            location_name if location_name is not None else UNSET
        )

        result = await self._client.inventory.set_for_product(
            product_id=product_id,
            stock_on_hand=stock_on_hand_param,
            stock_on_order=stock_on_order_param,
            location_code=location_code_param,
            location_name=location_name_param,
        )

        logger.info(f"Inventory set successfully for product: {product_id}")
        return result
