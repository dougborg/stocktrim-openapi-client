"""Location operations."""

from __future__ import annotations

from typing import Any

from stocktrim_public_api_client.generated.api.locations import (
    get_api_locations,
    post_api_locations,
)
from stocktrim_public_api_client.generated.models.location_request_dto import (
    LocationRequestDto,
)
from stocktrim_public_api_client.generated.models.location_response_dto import (
    LocationResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Locations(Base):
    """Location management."""

    async def list(self, **filters: Any) -> list[LocationResponseDto]:
        """List all locations.

        Args:
            **filters: Optional filtering parameters.

        Returns:
            List of LocationResponseDto objects.

        Example:
            >>> locations = await client.locations.list()
        """
        response = await get_api_locations.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def create(
        self, location_data: list[LocationRequestDto]
    ) -> list[LocationResponseDto]:
        """Create new locations.

        Args:
            location_data: List of LocationRequestDto models with location details.

        Returns:
            List of LocationResponseDto objects.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     LocationRequestDto,
            ... )
            >>> locations = await client.locations.create(
            ...     [LocationRequestDto(code="LOC-001", name="Warehouse A")]
            ... )
        """
        response = await post_api_locations.asyncio_detailed(
            client=self._client,
            body=location_data,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []
