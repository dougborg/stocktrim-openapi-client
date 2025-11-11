"""Location management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: list_locations
# ============================================================================


class ListLocationsRequest(BaseModel):
    """Request model for listing locations."""

    pass  # No parameters needed for listing all locations


class LocationInfo(BaseModel):
    """Location information."""

    code: str
    name: str | None


class ListLocationsResponse(BaseModel):
    """Response containing locations."""

    locations: list[LocationInfo]
    total_count: int


@unpack_pydantic_params
async def list_locations(
    request: Annotated[ListLocationsRequest, Unpack()], context: Context
) -> ListLocationsResponse:
    """List all locations.

    This tool retrieves all warehouse/store locations from StockTrim.

    Args:
        request: Request (no parameters needed)
        context: Server context with StockTrimClient

    Returns:
        ListLocationsResponse with locations

    Example:
        Request: {}
        Returns: {"locations": [...], "total_count": 5}
    """
    services = get_services(context)
    locations = await services.locations.list_all()

    # Build response - map DTO fields to tool response
    location_infos = [
        LocationInfo(
            code=loc.location_code or "",
            name=loc.location_name,
        )
        for loc in locations
    ]

    return ListLocationsResponse(
        locations=location_infos,
        total_count=len(location_infos),
    )


# ============================================================================
# Tool 2: create_location
# ============================================================================


class CreateLocationRequest(BaseModel):
    """Request model for creating a location."""

    code: str = Field(..., description="Unique location code")
    name: str = Field(..., description="Location name")


@unpack_pydantic_params
async def create_location(
    request: Annotated[CreateLocationRequest, Unpack()], context: Context
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
        Returns: {"code": "WH-01", "name": "Main Warehouse"}
    """
    services = get_services(context)
    created_location = await services.locations.create(
        code=request.code,
        name=request.name,
    )

    # Build LocationInfo from response - map DTO fields to tool response
    return LocationInfo(
        code=created_location.location_code or "",
        name=created_location.location_name,
    )


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
