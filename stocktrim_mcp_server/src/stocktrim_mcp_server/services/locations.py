"""Location management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import LocationsResponseDto

logger = logging.getLogger(__name__)


class LocationService(BaseService):
    """Service for location management operations."""

    async def list_all(self, active_only: bool = True) -> list[LocationsResponseDto]:
        """List all locations with optional filtering by active status.

        Args:
            active_only: Only return active locations (default: True)

        Returns:
            List of locations

        Raises:
            Exception: If API call fails
        """
        logger.info(f"Listing locations (active_only={active_only})")

        # Get all locations
        locations = await self._client.locations.get_all()

        # Filter by active status if requested
        if active_only:
            locations = [loc for loc in locations if loc.is_active]

        logger.info(f"Found {len(locations)} locations")
        return locations

    async def create(self, code: str, name: str) -> LocationsResponseDto:
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

        # Import LocationRequestDto from generated models
        from stocktrim_public_api_client.generated.models import LocationRequestDto

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
