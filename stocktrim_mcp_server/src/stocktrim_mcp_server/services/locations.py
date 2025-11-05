"""Location management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import (
    LocationRequestDto,
    LocationResponseDto,
)

logger = logging.getLogger(__name__)


class LocationService(BaseService):
    """Service for location management operations."""

    async def list_all(self) -> list[LocationResponseDto]:
        """List all locations.

        Returns:
            List of locations

        Raises:
            Exception: If API call fails
        """
        logger.info("Listing locations")

        # Get all locations
        locations_result = await self._client.locations.get_all()

        # Handle API returning single object or list
        if isinstance(locations_result, list):
            locations = locations_result
        else:
            locations = [locations_result]

        logger.info(f"Found {len(locations)} locations")
        return locations

    async def create(
        self,
        code: str,
        name: str,
    ) -> LocationResponseDto:
        """Create a new location.

        Args:
            code: Unique location code
            name: Location name

        Returns:
            Created location details

        Raises:
            ValueError: If required fields are empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Location code")
        self.validate_not_empty(name, "Location name")

        logger.info(f"Creating location: {code}")

        # Create location DTO
        location_dto = LocationRequestDto(
            location_code=code,
            location_name=name,
        )

        # Create location
        created_location = await self._client.locations.create(location_dto)

        if not created_location:
            raise Exception(f"Failed to create location {code}")

        logger.info(f"Location created: {code}")
        return created_location
