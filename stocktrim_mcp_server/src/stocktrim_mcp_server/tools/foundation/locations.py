"""Location management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services

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
    services = get_services(context)
    locations = await services.locations.list_all(active_only=request.active_only)

    # Build response
    location_infos = [
        LocationInfo(
            code=loc.code or "",
            name=loc.name,
            is_active=loc.is_active or False,
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
    is_active: bool = Field(default=True, description="Whether location is active")


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
    services = get_services(context)
    created_location = await services.locations.create(
        code=request.code,
        name=request.name,
        is_active=request.is_active,
    )

    # Build LocationInfo from response
    return LocationInfo(
        code=created_location.code or "",
        name=created_location.name,
        is_active=created_location.is_active or False,
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
