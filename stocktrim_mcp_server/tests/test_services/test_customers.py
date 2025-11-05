"""Tests for customer management service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.customers import CustomerService
from stocktrim_public_api_client.generated.models.customer_dto import CustomerDto
from stocktrim_public_api_client.utils import NotFoundError


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.customers = MagicMock()
    return client


@pytest.fixture
def customer_service(mock_client):
    """Create a CustomerService instance with mock client."""
    return CustomerService(mock_client)


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing."""
    return CustomerDto(
        code="CUST-001",
        name="Test Customer",
        email_address="customer@example.com",
        phone="555-1234",
        street_address="123 Main St",
    )


@pytest.fixture
def sample_customers():
    """Create a list of sample customers for testing."""
    return [
        CustomerDto(
            code="CUST-001",
            name="Customer One",
            email_address="customer1@example.com",
        ),
        CustomerDto(
            code="CUST-002",
            name="Customer Two",
            email_address="customer2@example.com",
        ),
        CustomerDto(
            code="CUST-003",
            name="Customer Three",
            email_address="customer3@example.com",
        ),
    ]


# ============================================================================
# Tests for get_by_code
# ============================================================================


@pytest.mark.asyncio
async def test_get_by_code_success(customer_service, mock_client, sample_customer):
    """Test successfully getting a customer by code."""
    # Setup
    mock_client.customers.get = AsyncMock(return_value=sample_customer)

    # Execute
    result = await customer_service.get_by_code("CUST-001")

    # Verify
    assert result == sample_customer
    assert result.code == "CUST-001"
    assert result.name == "Test Customer"
    mock_client.customers.get.assert_called_once_with("CUST-001")


@pytest.mark.asyncio
async def test_get_by_code_not_found(customer_service, mock_client):
    """Test getting a customer that doesn't exist returns None."""
    # Setup - simulate 404 error
    mock_client.customers.get = AsyncMock(
        side_effect=NotFoundError("Customer not found", 404)
    )

    # Execute
    result = await customer_service.get_by_code("NONEXISTENT")

    # Verify
    assert result is None
    mock_client.customers.get.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_by_code_empty_code(customer_service):
    """Test that empty code raises ValueError."""
    # Execute & Verify
    with pytest.raises(ValueError, match="Customer code cannot be empty"):
        await customer_service.get_by_code("")

    with pytest.raises(ValueError, match="Customer code cannot be empty"):
        await customer_service.get_by_code("  ")


@pytest.mark.asyncio
async def test_get_by_code_api_error(customer_service, mock_client):
    """Test handling of API errors (non-404)."""
    # Setup
    mock_client.customers.get = AsyncMock(side_effect=Exception("Server error"))

    # Execute & Verify
    with pytest.raises(Exception, match="Server error"):
        await customer_service.get_by_code("CUST-001")


# ============================================================================
# Tests for list_all
# ============================================================================


@pytest.mark.asyncio
async def test_list_all_success(customer_service, mock_client, sample_customers):
    """Test successfully listing all customers."""
    # Setup
    mock_client.customers.get_all = AsyncMock(return_value=sample_customers)

    # Execute
    result = await customer_service.list_all()

    # Verify
    assert len(result) == 3
    assert result[0].code == "CUST-001"
    assert result[1].code == "CUST-002"
    assert result[2].code == "CUST-003"
    mock_client.customers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_with_limit(customer_service, mock_client, sample_customers):
    """Test listing customers with a limit."""
    # Setup
    mock_client.customers.get_all = AsyncMock(return_value=sample_customers)

    # Execute
    result = await customer_service.list_all(limit=2)

    # Verify
    assert len(result) == 2
    assert result[0].code == "CUST-001"
    assert result[1].code == "CUST-002"
    mock_client.customers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_empty(customer_service, mock_client):
    """Test listing customers when none exist."""
    # Setup
    mock_client.customers.get_all = AsyncMock(return_value=[])

    # Execute
    result = await customer_service.list_all()

    # Verify
    assert len(result) == 0
    assert result == []
    mock_client.customers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_limit_zero(customer_service, mock_client, sample_customers):
    """Test listing customers with limit of zero."""
    # Setup
    mock_client.customers.get_all = AsyncMock(return_value=sample_customers)

    # Execute
    result = await customer_service.list_all(limit=0)

    # Verify
    assert len(result) == 0
    assert result == []
    mock_client.customers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_limit_exceeds_count(
    customer_service, mock_client, sample_customers
):
    """Test listing customers when limit exceeds available count."""
    # Setup
    mock_client.customers.get_all = AsyncMock(return_value=sample_customers)

    # Execute
    result = await customer_service.list_all(limit=100)

    # Verify - should return all 3 customers
    assert len(result) == 3
    assert result[0].code == "CUST-001"
    assert result[1].code == "CUST-002"
    assert result[2].code == "CUST-003"
    mock_client.customers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_api_error(customer_service, mock_client):
    """Test handling of API errors when listing customers."""
    # Setup
    mock_client.customers.get_all = AsyncMock(side_effect=Exception("API Error"))

    # Execute & Verify
    with pytest.raises(Exception, match="API Error"):
        await customer_service.list_all()
