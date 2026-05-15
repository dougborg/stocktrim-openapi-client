"""Location management tools for StockTrim MCP Server."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.tools.tool_result_utils import make_json_result
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
) -> ToolResult:
    """List all locations.

    This tool retrieves all warehouse/store locations from StockTrim.

    Args:
        request: Request (no parameters needed)
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, ListLocationsResponse)``.
    """
    services = get_services(context)
    locations = await services.locations.list_all()

    location_infos = [
        LocationInfo(code=loc.location_code or "", name=loc.location_name)
        for loc in locations
    ]
    return make_json_result(
        ListLocationsResponse(
            locations=location_infos,
            total_count=len(location_infos),
        )
    )


# ============================================================================
# Tool 2: create_location
# ============================================================================


class CreateLocationRequest(BaseModel):
    """Request model for creating a location."""

    code: str = Field(..., description="Unique location code")
    name: str = Field(..., description="Location name")


class CreateLocationResponse(BaseModel):
    """Response wrapper so a single ``LocationInfo`` serializes through
    ``make_json_result``."""

    location: LocationInfo


@unpack_pydantic_params
async def create_location(
    request: Annotated[CreateLocationRequest, Unpack()], context: Context
) -> ToolResult:
    """Create a new location.

    This tool creates a new warehouse/store location in StockTrim.

    Args:
        request: Request containing location details
        context: Server context with StockTrimClient

    Returns:
        A :class:`fastmcp.tools.ToolResult` per SEP-1865; use
        ``unwrap_tool_result(result, CreateLocationResponse)`` and read
        ``response.location``.
    """
    services = get_services(context)
    created_location = await services.locations.create(
        code=request.code,
        name=request.name,
    )

    location = LocationInfo(
        code=created_location.location_code or "",
        name=created_location.location_name,
    )
    return make_json_result(CreateLocationResponse(location=location))


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
