"""Location operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
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
    """Location management.

    Provides operations for managing locations in StockTrim.
    """

    async def get_all(
        self,
        code: str | Unset = UNSET,
    ) -> LocationResponseDto | list[LocationResponseDto]:
        """Get locations, optionally filtered by code.

        Note: The API returns a single object when filtered by code,
        but this is inconsistent with other endpoints. We preserve
        the API's behavior here.

        Args:
            code: Optional location code filter.

        Returns:
            LocationResponseDto or list of LocationResponseDto objects.

        Example:
            >>> locations = await client.locations.get_all()
            >>> location = await client.locations.get_all(code="LOC-001")
        """
        response = await get_api_locations.asyncio_detailed(
            client=self._client,
            code=code,
        )
        return cast(
            LocationResponseDto | list[LocationResponseDto],
            unwrap(response),
        )

    async def create(self, location: LocationRequestDto) -> LocationResponseDto:
        """Create a new location.

        Note: The API returns a single object but it's unclear if it accepts
        a single object or array. We preserve the API's behavior here.

        Args:
            location: Location data to create.

        Returns:
            Created LocationResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     LocationRequestDto,
            ... )
            >>> location = await client.locations.create(
            ...     LocationRequestDto(code="LOC-001", name="Warehouse A")
            ... )
        """
        response = await post_api_locations.asyncio_detailed(
            client=self._client,
            body=location,
        )
        return cast(LocationResponseDto, unwrap(response))
