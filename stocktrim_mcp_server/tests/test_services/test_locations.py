"""Tests for LocationService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.locations import LocationService
from stocktrim_public_api_client.generated.models import (
    LocationRequestDto,
    LocationResponseDto,
)


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.locations = MagicMock()
    return client


@pytest.fixture
def location_service(mock_client):
    """Create a LocationService instance with mock client."""
    return LocationService(mock_client)


@pytest.fixture
def sample_location():
    """Create a sample location for testing."""
    return LocationResponseDto(
        location_code="WH-01",
        id=1,
        location_name="Main Warehouse",
    )


@pytest.fixture
def second_location():
    """Create a second location for testing."""
    return LocationResponseDto(
        location_code="WH-02",
        id=2,
        location_name="Secondary Warehouse",
    )


@pytest.mark.asyncio
async def test_list_all_returns_locations(
    location_service, mock_client, sample_location
):
    """Test list_all returns all locations."""
    # Setup
    mock_client.locations.get_all = AsyncMock(return_value=[sample_location])

    # Execute
    locations = await location_service.list_all()

    # Verify
    assert len(locations) == 1
    assert locations[0].location_code == "WH-01"
    mock_client.locations.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_returns_multiple_locations(
    location_service, mock_client, sample_location, second_location
):
    """Test list_all returns multiple locations."""
    # Setup
    mock_client.locations.get_all = AsyncMock(
        return_value=[sample_location, second_location]
    )

    # Execute
    locations = await location_service.list_all()

    # Verify
    assert len(locations) == 2
    assert any(loc.location_code == "WH-01" for loc in locations)
    assert any(loc.location_code == "WH-02" for loc in locations)


@pytest.mark.asyncio
async def test_list_all_handles_single_location_response(
    location_service, mock_client, sample_location
):
    """Test list_all handles API returning a single location instead of list."""
    # Setup - API sometimes returns single object instead of list
    mock_client.locations.get_all = AsyncMock(return_value=sample_location)

    # Execute
    locations = await location_service.list_all()

    # Verify
    assert len(locations) == 1
    assert locations[0].location_code == "WH-01"


@pytest.mark.asyncio
async def test_create_success(location_service, mock_client, sample_location):
    """Test successful location creation."""
    # Setup
    mock_client.locations.create = AsyncMock(return_value=sample_location)

    # Execute
    created_location = await location_service.create(
        code="WH-01", name="Main Warehouse"
    )

    # Verify
    assert created_location.location_code == "WH-01"
    assert created_location.location_name == "Main Warehouse"

    # Verify create was called with correct DTO
    mock_client.locations.create.assert_called_once()
    call_args = mock_client.locations.create.call_args
    location_dto = call_args[0][0]
    assert isinstance(location_dto, LocationRequestDto)
    assert location_dto.location_code == "WH-01"
    assert location_dto.location_name == "Main Warehouse"


@pytest.mark.asyncio
async def test_create_validates_empty_code(location_service):
    """Test create raises ValueError for empty code."""
    with pytest.raises(ValueError, match="Location code cannot be empty"):
        await location_service.create(code="", name="Test")


@pytest.mark.asyncio
async def test_create_validates_empty_name(location_service):
    """Test create raises ValueError for empty name."""
    with pytest.raises(ValueError, match="Location name cannot be empty"):
        await location_service.create(code="WH-01", name="")


@pytest.mark.asyncio
async def test_create_validates_whitespace_code(location_service):
    """Test create raises ValueError for whitespace-only code."""
    with pytest.raises(ValueError, match="Location code cannot be empty"):
        await location_service.create(code="   ", name="Test")


@pytest.mark.asyncio
async def test_create_validates_whitespace_name(location_service):
    """Test create raises ValueError for whitespace-only name."""
    with pytest.raises(ValueError, match="Location name cannot be empty"):
        await location_service.create(code="WH-01", name="   ")


@pytest.mark.asyncio
async def test_create_raises_exception_on_api_failure(location_service, mock_client):
    """Test create raises exception when API returns None."""
    # Setup
    mock_client.locations.create = AsyncMock(return_value=None)

    # Execute & Verify
    with pytest.raises(Exception, match="Failed to create location WH-01"):
        await location_service.create(code="WH-01", name="Main Warehouse")
