"""Location management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: list_locations
# ============================================================================


class ListLocationsRequest(BaseModel):
    """Request model for listing locations."""

    active_only: bool = Field(
        default=True, description="Only return active locations (default: true)"
    )


class LocationInfo(BaseModel):
    """Location information."""

    code: str
    name: str | None
    is_active: bool


class ListLocationsResponse(BaseModel):
    """Response containing locations."""

    locations: list[LocationInfo]
    total_count: int


async def _list_locations_impl(
    request: ListLocationsRequest, context: Context
) -> ListLocationsResponse:
    """Implementation of list_locations tool.

    Args:
        request: Request with filter options
        context: Server context with StockTrimClient

    Returns:
        ListLocationsResponse with locations

    Raises:
        Exception: If API call fails
    """
    logger.info(f"Listing locations (active_only={request.active_only})")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Get all locations
        locations = await client.locations.get_all()

        # Filter by active status if requested
        if request.active_only:
            locations = [loc for loc in locations if loc.is_active]

        # Build response
        location_infos = [
            LocationInfo(
                code=loc.code or "",
                name=loc.name,
                is_active=loc.is_active or False,
            )
            for loc in locations
        ]

        response = ListLocationsResponse(
            locations=location_infos,
            total_count=len(location_infos),
        )

        logger.info(f"Found {response.total_count} locations")
        return response

    except Exception as e:
        logger.error(f"Failed to list locations: {e}")
        raise


async def list_locations(
    request: ListLocationsRequest, context: Context
) -> ListLocationsResponse:
    """List all locations.

    This tool retrieves all warehouse/store locations from StockTrim,
    optionally filtered by active status.

    Args:
        request: Request with filter options
        context: Server context with StockTrimClient

    Returns:
        ListLocationsResponse with locations

    Example:
        Request: {"active_only": true}
        Returns: {"locations": [...], "total_count": 5}
    """
    return await _list_locations_impl(request, context)


# ============================================================================
# Tool 2: create_location
# ============================================================================


class CreateLocationRequest(BaseModel):
    """Request model for creating a location."""

    code: str = Field(..., description="Unique location code")
    name: str = Field(..., description="Location name")
    is_active: bool = Field(default=True, description="Whether location is active")


async def _create_location_impl(
    request: CreateLocationRequest, context: Context
) -> LocationInfo:
    """Implementation of create_location tool.

    Args:
        request: Request containing location details
        context: Server context with StockTrimClient

    Returns:
        LocationInfo for the created location

    Raises:
        ValueError: If required fields are missing
        Exception: If API call fails
    """
    if not request.code or not request.code.strip():
        raise ValueError("Location code cannot be empty")
    if not request.name or not request.name.strip():
        raise ValueError("Location name cannot be empty")

    logger.info(f"Creating location: {request.code}")

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Import LocationRequestDto from generated models
        from stocktrim_public_api_client.generated.models import LocationRequestDto

        # Create location DTO
        location_dto = LocationRequestDto(
            location_code=request.code,
            location_name=request.name,
        )

        # Create location (API accepts single object, not list)
        created_location = await client.locations.create(location_dto)

        if not created_location:
            raise Exception(f"Failed to create location {request.code}")

        # Build LocationInfo from response
        location_info = LocationInfo(
            code=created_location.code or "",
            name=created_location.name,
            is_active=created_location.is_active or False,
        )

        logger.info(f"Location created: {request.code}")
        return location_info

    except Exception as e:
        logger.error(f"Failed to create location {request.code}: {e}")
        raise


async def create_location(
    request: CreateLocationRequest, context: Context
) -> LocationInfo:
    """Create a new location.

    This tool creates a new warehouse/store location in StockTrim.

    Args:
        request: Request containing location details
        context: Server context with StockTrimClient

    Returns:
        LocationInfo for the created location

    Example:
        Request: {"code": "WH-01", "name": "Main Warehouse"}
        Returns: {"code": "WH-01", "name": "Main Warehouse", "is_active": true}
    """
    return await _create_location_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register location tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(list_locations)
    mcp.tool()(create_location)
