"""Inventory operations."""

from __future__ import annotations

from stocktrim_public_api_client.generated.api.inventory import (
    post_api_inventory,
)
from stocktrim_public_api_client.generated.models.set_inventory_request_dto import (
    SetInventoryRequestDto,
)
from stocktrim_public_api_client.generated.models.set_inventory_response_dto import (
    SetInventoryResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Inventory(Base):
    """Inventory management."""

    async def set(
        self, inventory_data: list[SetInventoryRequestDto]
    ) -> list[SetInventoryResponseDto]:
        """Set inventory levels.

        Args:
            inventory_data: List of SetInventoryRequestDto models with inventory levels.

        Returns:
            List of SetInventoryResponseDto objects.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SetInventoryRequestDto,
            ... )
            >>> response = await client.inventory.set(
            ...     [SetInventoryRequestDto(product_code="PROD-001", quantity=100)]
            ... )
        """
        response = await post_api_inventory.asyncio_detailed(
            client=self._client,
            body=inventory_data,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []
