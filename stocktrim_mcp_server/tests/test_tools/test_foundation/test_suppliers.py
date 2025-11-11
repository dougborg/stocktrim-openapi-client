"""Tests for supplier foundation tools."""

from unittest.mock import AsyncMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from stocktrim_mcp_server.tools.foundation.suppliers import (
    create_supplier,
    delete_supplier,
    get_supplier,
    list_suppliers,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)


@pytest.fixture
def sample_supplier():
    """Create a sample supplier for testing."""
    return SupplierResponseDto(
        supplier_code="SUP-001",
        supplier_name="Acme Supplies",
        email_address="contact@acme.com",
        primary_contact_name="John Doe",
    )


@pytest.fixture
def mock_supplier_context(mock_context):
    """Extend mock_context with mock suppliers service."""
    services = mock_context.request_context.lifespan_context
    services.suppliers = AsyncMock()
    return mock_context


# ============================================================================
# Test get_supplier
# ============================================================================


@pytest.mark.asyncio
async def test_get_supplier_success(mock_supplier_context, sample_supplier):
    """Test successfully getting a supplier."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = sample_supplier

    # Execute
    response = await get_supplier(code="SUP-001", context=mock_supplier_context)

    # Verify
    assert response is not None
    assert response.code == "SUP-001"
    assert response.name == "Acme Supplies"
    assert response.email == "contact@acme.com"
    assert response.primary_contact == "John Doe"

    services.suppliers.get_by_code.assert_called_once_with("SUP-001")


@pytest.mark.asyncio
async def test_get_supplier_not_found(mock_supplier_context):
    """Test getting a supplier that doesn't exist."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = None

    # Execute
    response = await get_supplier(code="MISSING", context=mock_supplier_context)

    # Verify
    assert response is None
    services.suppliers.get_by_code.assert_called_once_with("MISSING")


@pytest.mark.asyncio
async def test_get_supplier_minimal_fields(mock_supplier_context):
    """Test getting a supplier with minimal fields."""
    # Setup
    supplier = SupplierResponseDto(
        supplier_code="SUP-002",
        supplier_name="Minimal Supplier",
        email_address=None,
        primary_contact_name=None,
    )
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = supplier

    # Execute
    response = await get_supplier(code="SUP-002", context=mock_supplier_context)

    # Verify
    assert response is not None
    assert response.code == "SUP-002"
    assert response.name == "Minimal Supplier"
    assert response.email is None
    assert response.primary_contact is None


# ============================================================================
# Test list_suppliers
# ============================================================================


@pytest.mark.asyncio
async def test_list_suppliers_all(mock_supplier_context, sample_supplier):
    """Test listing all suppliers."""
    # Setup
    supplier2 = SupplierResponseDto(
        supplier_code="SUP-002",
        supplier_name="Beta Corp",
        email_address="sales@beta.com",
        primary_contact_name="Jane Smith",
    )
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.list_all.return_value = [sample_supplier, supplier2]

    # Execute
    response = await list_suppliers(active_only=False, context=mock_supplier_context)

    # Verify
    assert response.total_count == 2
    assert len(response.suppliers) == 2
    assert response.suppliers[0].code == "SUP-001"
    assert response.suppliers[1].code == "SUP-002"

    services.suppliers.list_all.assert_called_once_with(False)


@pytest.mark.asyncio
async def test_list_suppliers_active_only(mock_supplier_context, sample_supplier):
    """Test listing only active suppliers."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.list_all.return_value = [sample_supplier]

    # Execute
    response = await list_suppliers(active_only=True, context=mock_supplier_context)

    # Verify
    assert response.total_count == 1
    assert len(response.suppliers) == 1

    services.suppliers.list_all.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_list_suppliers_empty(mock_supplier_context):
    """Test listing suppliers when none exist."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.list_all.return_value = []

    # Execute
    response = await list_suppliers(context=mock_supplier_context)

    # Verify
    assert response.total_count == 0
    assert len(response.suppliers) == 0


# ============================================================================
# Test create_supplier
# ============================================================================


@pytest.mark.asyncio
async def test_create_supplier_success(mock_supplier_context, sample_supplier):
    """Test successfully creating a supplier."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.create.return_value = sample_supplier

    # Execute
    response = await create_supplier(
        code="SUP-001",
        name="Acme Supplies",
        email="contact@acme.com",
        primary_contact="John Doe",
        context=mock_supplier_context,
    )

    # Verify
    assert response.code == "SUP-001"
    assert response.name == "Acme Supplies"
    assert response.email == "contact@acme.com"
    assert response.primary_contact == "John Doe"

    services.suppliers.create.assert_called_once_with(
        code="SUP-001",
        name="Acme Supplies",
        email="contact@acme.com",
        primary_contact="John Doe",
    )


@pytest.mark.asyncio
async def test_create_supplier_minimal(mock_supplier_context):
    """Test creating a supplier with minimal fields."""
    # Setup
    supplier = SupplierResponseDto(
        supplier_code="SUP-003",
        supplier_name="Minimal Supplier",
        email_address=None,
        primary_contact_name=None,
    )
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.create.return_value = supplier

    # Execute
    response = await create_supplier(
        code="SUP-003", name="Minimal Supplier", context=mock_supplier_context
    )

    # Verify
    assert response.code == "SUP-003"
    assert response.name == "Minimal Supplier"
    assert response.email is None
    assert response.primary_contact is None


@pytest.mark.asyncio
async def test_create_supplier_validation_error(mock_supplier_context):
    """Test creating a supplier when service raises validation error."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.create.side_effect = ValueError("Supplier code cannot be empty")

    # Execute & Verify
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await create_supplier(code="", name="Test", context=mock_supplier_context)


# ============================================================================
# Test delete_supplier (with elicitation)
# ============================================================================


@pytest.mark.asyncio
async def test_delete_supplier_not_found(mock_supplier_context):
    """Test deleting a supplier that doesn't exist."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = None

    # Execute
    response = await delete_supplier(code="MISSING", context=mock_supplier_context)

    # Verify
    assert response.success is False
    assert "not found" in response.message
    assert "MISSING" in response.message


@pytest.mark.asyncio
async def test_delete_supplier_accepted(mock_supplier_context, sample_supplier):
    """Test deleting a supplier when user accepts confirmation."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = sample_supplier
    services.suppliers.delete.return_value = (
        True,
        "Supplier SUP-001 deleted successfully",
    )
    mock_supplier_context.elicit = AsyncMock(
        return_value=AcceptedElicitation(data=None)
    )

    # Execute
    response = await delete_supplier(code="SUP-001", context=mock_supplier_context)

    # Verify
    assert response.success is True
    assert "✅" in response.message
    assert "deleted successfully" in response.message

    # Verify elicitation was called with preview
    mock_supplier_context.elicit.assert_called_once()
    elicit_args = mock_supplier_context.elicit.call_args
    assert "⚠️ Delete supplier" in elicit_args[1]["message"]
    assert "Acme Supplies" in elicit_args[1]["message"]
    assert "John Doe" in elicit_args[1]["message"]

    # Verify deletion was called
    services.suppliers.delete.assert_called_once_with("SUP-001")


@pytest.mark.asyncio
async def test_delete_supplier_declined(mock_supplier_context, sample_supplier):
    """Test deleting a supplier when user declines confirmation."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = sample_supplier
    mock_supplier_context.elicit = AsyncMock(
        return_value=DeclinedElicitation(data=None)
    )

    # Execute
    response = await delete_supplier(code="SUP-001", context=mock_supplier_context)

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "declined" in response.message
    assert "SUP-001" in response.message

    # Verify deletion was NOT called
    services.suppliers.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_supplier_cancelled(mock_supplier_context, sample_supplier):
    """Test deleting a supplier when user cancels confirmation."""
    # Setup
    services = mock_supplier_context.request_context.lifespan_context
    services.suppliers.get_by_code.return_value = sample_supplier
    mock_supplier_context.elicit = AsyncMock(
        return_value=CancelledElicitation(data=None)
    )

    # Execute
    response = await delete_supplier(code="SUP-001", context=mock_supplier_context)

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "cancelled" in response.message
    assert "SUP-001" in response.message

    # Verify deletion was NOT called
    services.suppliers.delete.assert_not_called()
