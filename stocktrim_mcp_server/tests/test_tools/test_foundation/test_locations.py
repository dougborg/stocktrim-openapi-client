"""Tests for location foundation tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.foundation.locations import (
    create_location,
    list_locations,
)
from stocktrim_public_api_client.generated.models.location_response_dto import (
    LocationResponseDto,
)


@pytest.fixture
def sample_location():
    """Create a sample location for testing."""
    return LocationResponseDto(
        location_code="WH-01",
        location_name="Main Warehouse",
    )


@pytest.fixture
def mock_location_context(mock_context):
    """Extend mock_context with mock locations service."""
    services = mock_context.request_context.lifespan_context
    services.locations = AsyncMock()
    return mock_context


# ============================================================================
# Test list_locations
# ============================================================================


@pytest.mark.asyncio
async def test_list_locations_success(mock_location_context, sample_location):
    """Test successfully listing locations."""
    # Setup
    location2 = LocationResponseDto(
        location_code="WH-02",
        location_name="Secondary Warehouse",
    )
    services = mock_location_context.request_context.lifespan_context
    services.locations.list_all.return_value = [sample_location, location2]

    # Execute
    response = await list_locations(context=mock_location_context)

    # Verify
    assert response.total_count == 2
    assert len(response.locations) == 2
    assert response.locations[0].code == "WH-01"
    assert response.locations[0].name == "Main Warehouse"
    assert response.locations[1].code == "WH-02"
    assert response.locations[1].name == "Secondary Warehouse"

    services.locations.list_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_locations_empty(mock_location_context):
    """Test listing locations when none exist."""
    # Setup
    services = mock_location_context.request_context.lifespan_context
    services.locations.list_all.return_value = []

    # Execute
    response = await list_locations(context=mock_location_context)

    # Verify
    assert response.total_count == 0
    assert len(response.locations) == 0

    services.locations.list_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_locations_with_none_name(mock_location_context):
    """Test listing locations with None name."""
    # Setup
    location = LocationResponseDto(
        location_code="WH-03",
        location_name=None,
    )
    services = mock_location_context.request_context.lifespan_context
    services.locations.list_all.return_value = [location]

    # Execute
    response = await list_locations(context=mock_location_context)

    # Verify
    assert response.total_count == 1
    assert response.locations[0].code == "WH-03"
    assert response.locations[0].name is None


# ============================================================================
# Test create_location
# ============================================================================


@pytest.mark.asyncio
async def test_create_location_success(mock_location_context, sample_location):
    """Test successfully creating a location."""
    # Setup
    services = mock_location_context.request_context.lifespan_context
    services.locations.create.return_value = sample_location

    # Execute
    response = await create_location(
        code="WH-01", name="Main Warehouse", context=mock_location_context
    )

    # Verify
    assert response.code == "WH-01"
    assert response.name == "Main Warehouse"

    services.locations.create.assert_called_once_with(
        code="WH-01",
        name="Main Warehouse",
    )


@pytest.mark.asyncio
async def test_create_location_validation_error(mock_location_context):
    """Test creating a location when service raises validation error."""
    # Setup
    services = mock_location_context.request_context.lifespan_context
    services.locations.create.side_effect = ValueError("Location code cannot be empty")

    # Execute & Verify
    with pytest.raises(ValueError, match="Location code cannot be empty"):
        await create_location(
            code="", name="Empty Code Location", context=mock_location_context
        )


@pytest.mark.asyncio
async def test_create_location_with_special_characters(mock_location_context):
    """Test creating a location with special characters."""
    # Setup
    location = LocationResponseDto(
        location_code="WH-MAIN-01",
        location_name="Main Warehouse - Building A (North)",
    )
    services = mock_location_context.request_context.lifespan_context
    services.locations.create.return_value = location

    # Execute
    response = await create_location(
        code="WH-MAIN-01",
        name="Main Warehouse - Building A (North)",
        context=mock_location_context,
    )

    # Verify
    assert response.code == "WH-MAIN-01"
    assert response.name == "Main Warehouse - Building A (North)"


@pytest.mark.asyncio
async def test_create_location_duplicate_error(mock_location_context):
    """Test creating a location with duplicate code."""
    # Setup
    services = mock_location_context.request_context.lifespan_context
    services.locations.create.side_effect = Exception(
        "Location with code WH-01 already exists"
    )

    # Execute & Verify
    with pytest.raises(Exception, match="already exists"):
        await create_location(
            code="WH-01", name="Duplicate Warehouse", context=mock_location_context
        )
