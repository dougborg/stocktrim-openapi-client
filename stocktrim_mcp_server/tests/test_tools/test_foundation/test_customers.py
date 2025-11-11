"""Tests for customer foundation tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.foundation.customers import (
    get_customer,
    list_customers,
)
from stocktrim_public_api_client.generated.models.customer_dto import CustomerDto


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing."""
    return CustomerDto(
        code="CUST-001",
        name="Test Customer",
        email_address="test@example.com",
        phone="+1-555-0100",
        street_address="123 Main St",
    )


@pytest.fixture
def mock_customer_context(mock_context):
    """Extend mock_context with mock customers service."""
    services = mock_context.request_context.lifespan_context
    services.customers = AsyncMock()
    return mock_context


# ============================================================================
# Test get_customer
# ============================================================================


@pytest.mark.asyncio
async def test_get_customer_success(mock_customer_context, sample_customer):
    """Test successfully getting a customer."""
    # Setup
    services = mock_customer_context.request_context.lifespan_context
    services.customers.get_by_code.return_value = sample_customer

    # Execute
    response = await get_customer(code="CUST-001", context=mock_customer_context)

    # Verify
    assert response is not None
    assert response.code == "CUST-001"
    assert response.name == "Test Customer"
    assert response.email == "test@example.com"
    assert response.phone == "+1-555-0100"
    assert response.address == "123 Main St"

    services.customers.get_by_code.assert_called_once_with("CUST-001")


@pytest.mark.asyncio
async def test_get_customer_not_found(mock_customer_context):
    """Test getting a customer that doesn't exist."""
    # Setup
    services = mock_customer_context.request_context.lifespan_context
    services.customers.get_by_code.return_value = None

    # Execute
    response = await get_customer(code="CUST-MISSING", context=mock_customer_context)

    # Verify
    assert response is None
    services.customers.get_by_code.assert_called_once_with("CUST-MISSING")


@pytest.mark.asyncio
async def test_get_customer_with_none_fields(mock_customer_context):
    """Test getting a customer with None optional fields."""
    # Setup
    customer = CustomerDto(
        code="CUST-002",
        name="Minimal Customer",
        email_address=None,
        phone=None,
        street_address=None,
    )
    services = mock_customer_context.request_context.lifespan_context
    services.customers.get_by_code.return_value = customer

    # Execute
    response = await get_customer(code="CUST-002", context=mock_customer_context)

    # Verify
    assert response is not None
    assert response.code == "CUST-002"
    assert response.name == "Minimal Customer"
    assert response.email is None
    assert response.phone is None
    assert response.address is None


# ============================================================================
# Test list_customers
# ============================================================================


@pytest.mark.asyncio
async def test_list_customers_success(mock_customer_context, sample_customer):
    """Test successfully listing customers."""
    # Setup
    customer2 = CustomerDto(
        code="CUST-002",
        name="Another Customer",
        email_address="another@example.com",
        phone="+1-555-0200",
        street_address="456 Oak Ave",
    )
    services = mock_customer_context.request_context.lifespan_context
    services.customers.list_all.return_value = [sample_customer, customer2]

    # Execute
    response = await list_customers(limit=50, context=mock_customer_context)

    # Verify
    assert response.total_count == 2
    assert len(response.customers) == 2
    assert response.customers[0].code == "CUST-001"
    assert response.customers[0].name == "Test Customer"
    assert response.customers[1].code == "CUST-002"
    assert response.customers[1].name == "Another Customer"

    services.customers.list_all.assert_called_once_with(limit=50)


@pytest.mark.asyncio
async def test_list_customers_empty(mock_customer_context):
    """Test listing customers when none exist."""
    # Setup
    services = mock_customer_context.request_context.lifespan_context
    services.customers.list_all.return_value = []

    # Execute
    response = await list_customers(context=mock_customer_context)

    # Verify
    assert response.total_count == 0
    assert len(response.customers) == 0

    services.customers.list_all.assert_called_once_with(limit=50)


@pytest.mark.asyncio
async def test_list_customers_with_custom_limit(mock_customer_context, sample_customer):
    """Test listing customers with a custom limit."""
    # Setup
    services = mock_customer_context.request_context.lifespan_context
    services.customers.list_all.return_value = [sample_customer]

    # Execute
    response = await list_customers(limit=10, context=mock_customer_context)

    # Verify
    assert response.total_count == 1
    assert len(response.customers) == 1

    services.customers.list_all.assert_called_once_with(limit=10)


@pytest.mark.asyncio
async def test_list_customers_with_minimal_data(mock_customer_context):
    """Test listing customers with minimal data fields."""
    # Setup
    minimal_customer = CustomerDto(
        code="CUST-MIN",
        name=None,
        email_address=None,
        phone=None,
        street_address=None,
    )
    services = mock_customer_context.request_context.lifespan_context
    services.customers.list_all.return_value = [minimal_customer]

    # Execute
    response = await list_customers(context=mock_customer_context)

    # Verify
    assert response.total_count == 1
    assert response.customers[0].code == "CUST-MIN"
    assert response.customers[0].name is None
    assert response.customers[0].email is None
