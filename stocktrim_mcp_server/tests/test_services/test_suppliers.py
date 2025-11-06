"""Tests for SupplierService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.suppliers import SupplierService
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.suppliers = MagicMock()
    client.suppliers.find_by_code = AsyncMock()
    client.suppliers.get_all = AsyncMock()
    client.suppliers.create_one = AsyncMock()
    client.suppliers.delete = AsyncMock()
    return client


@pytest.fixture
def supplier_service(mock_client):
    """Create a SupplierService with mock client."""
    return SupplierService(mock_client)


@pytest.fixture
def sample_supplier():
    """Create a sample supplier for testing."""
    return SupplierResponseDto(
        id=456,
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        email_address="test@supplier.com",
        primary_contact_name="John Doe",
    )


# ============================================================================
# Test get_by_code
# ============================================================================


@pytest.mark.asyncio
async def test_get_by_code_success(supplier_service, mock_client, sample_supplier):
    """Test successfully getting a supplier by code."""
    mock_client.suppliers.find_by_code.return_value = sample_supplier

    result = await supplier_service.get_by_code("SUP-001")

    assert result == sample_supplier
    mock_client.suppliers.find_by_code.assert_called_once_with("SUP-001")


@pytest.mark.asyncio
async def test_get_by_code_not_found(supplier_service, mock_client):
    """Test getting a supplier that doesn't exist."""
    mock_client.suppliers.find_by_code.return_value = None

    result = await supplier_service.get_by_code("NONEXISTENT")

    assert result is None
    mock_client.suppliers.find_by_code.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_by_code_empty_code(supplier_service):
    """Test error when code is empty."""
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await supplier_service.get_by_code("")

    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await supplier_service.get_by_code("   ")


@pytest.mark.asyncio
async def test_get_by_code_api_error(supplier_service, mock_client):
    """Test handling of API errors."""
    mock_client.suppliers.find_by_code.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await supplier_service.get_by_code("SUP-001")


# ============================================================================
# Test list_suppliers
# ============================================================================


@pytest.mark.asyncio
async def test_list_suppliers_returns_list(supplier_service, mock_client):
    """Test listing suppliers when API returns a list."""
    supplier1 = SupplierResponseDto(
        id=1,
        supplier_code="SUP-001",
        supplier_name="Supplier 1",
    )
    supplier2 = SupplierResponseDto(
        id=2,
        supplier_code="SUP-002",
        supplier_name="Supplier 2",
    )
    mock_client.suppliers.get_all.return_value = [supplier1, supplier2]

    result = await supplier_service.list_all()

    assert len(result) == 2
    assert result[0].supplier_code == "SUP-001"
    assert result[1].supplier_code == "SUP-002"
    mock_client.suppliers.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_suppliers_single_object_response(supplier_service, mock_client):
    """Test handling when API returns a single object instead of list."""
    single_supplier = SupplierResponseDto(
        id=1,
        supplier_code="SUP-001",
        supplier_name="Single Supplier",
    )
    mock_client.suppliers.get_all.return_value = single_supplier

    result = await supplier_service.list_all()

    assert len(result) == 1
    assert result[0].supplier_code == "SUP-001"


@pytest.mark.asyncio
async def test_list_suppliers_empty_list(supplier_service, mock_client):
    """Test listing when no suppliers exist."""
    mock_client.suppliers.get_all.return_value = []

    result = await supplier_service.list_all()

    assert len(result) == 0


@pytest.mark.asyncio
async def test_list_suppliers_active_only_parameter(supplier_service, mock_client):
    """Test that active_only parameter is accepted but currently unused.

    Note: The StockTrim API does not provide an is_active field for suppliers,
    so this parameter is reserved for future use and currently has no effect.
    """
    supplier1 = SupplierResponseDto(
        id=1,
        supplier_code="SUP-001",
        supplier_name="Supplier 1",
    )
    supplier2 = SupplierResponseDto(
        id=2,
        supplier_code="SUP-002",
        supplier_name="Supplier 2",
    )
    mock_client.suppliers.get_all.return_value = [supplier1, supplier2]

    # Test with active_only=True
    result_true = await supplier_service.list_all(active_only=True)
    assert len(result_true) == 2  # No filtering occurs

    # Test with active_only=False
    result_false = await supplier_service.list_all(active_only=False)
    assert len(result_false) == 2  # No filtering occurs

    # Verify both return the same results since filtering is not implemented
    assert result_true == result_false


# ============================================================================
# Test create
# ============================================================================


@pytest.mark.asyncio
async def test_create_success(supplier_service, mock_client):
    """Test successfully creating a supplier."""
    created_supplier = SupplierResponseDto(
        id=123,
        supplier_code="SUP-NEW",
        supplier_name="New Supplier",
        email_address="new@supplier.com",
    )
    mock_client.suppliers.create_one.return_value = created_supplier

    result = await supplier_service.create(
        code="SUP-NEW",
        name="New Supplier",
        email="new@supplier.com",
    )

    assert result.supplier_code == "SUP-NEW"
    assert result.supplier_name == "New Supplier"
    mock_client.suppliers.create_one.assert_called_once()


@pytest.mark.asyncio
async def test_create_with_primary_contact(supplier_service, mock_client):
    """Test creating a supplier with primary contact."""
    created_supplier = SupplierResponseDto(
        id=123,
        supplier_code="SUP-NEW",
        supplier_name="New Supplier",
        primary_contact_name="Jane Smith",
    )
    mock_client.suppliers.create_one.return_value = created_supplier

    result = await supplier_service.create(
        code="SUP-NEW",
        name="New Supplier",
        primary_contact="Jane Smith",
    )

    assert result.primary_contact_name == "Jane Smith"


@pytest.mark.asyncio
async def test_create_empty_code(supplier_service):
    """Test error when code is empty."""
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await supplier_service.create(code="", name="Test Supplier")


@pytest.mark.asyncio
async def test_create_empty_name(supplier_service):
    """Test error when name is empty."""
    with pytest.raises(ValueError, match="Supplier name cannot be empty"):
        await supplier_service.create(code="SUP-001", name="")


@pytest.mark.asyncio
async def test_create_api_returns_none(supplier_service, mock_client):
    """Test error when API returns None."""
    mock_client.suppliers.create_one.return_value = None

    with pytest.raises(Exception, match="Failed to create supplier"):
        await supplier_service.create(code="SUP-001", name="Test Supplier")


@pytest.mark.asyncio
async def test_create_api_error(supplier_service, mock_client):
    """Test handling of API errors during creation."""
    mock_client.suppliers.create_one.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await supplier_service.create(code="SUP-001", name="Test Supplier")


# ============================================================================
# Test delete
# ============================================================================


@pytest.mark.asyncio
async def test_delete_success(supplier_service, mock_client, sample_supplier):
    """Test successfully deleting a supplier."""
    mock_client.suppliers.find_by_code.return_value = sample_supplier

    success, message = await supplier_service.delete("SUP-001")

    assert success is True
    assert "deleted successfully" in message
    mock_client.suppliers.find_by_code.assert_called_once_with("SUP-001")
    mock_client.suppliers.delete.assert_called_once_with("SUP-001")


@pytest.mark.asyncio
async def test_delete_not_found(supplier_service, mock_client):
    """Test deleting a supplier that doesn't exist."""
    mock_client.suppliers.find_by_code.return_value = None

    success, message = await supplier_service.delete("NONEXISTENT")

    assert success is False
    assert "not found" in message
    mock_client.suppliers.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_empty_code(supplier_service):
    """Test error when code is empty."""
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await supplier_service.delete("")


@pytest.mark.asyncio
async def test_delete_api_error(supplier_service, mock_client, sample_supplier):
    """Test handling of API errors during deletion."""
    mock_client.suppliers.find_by_code.return_value = sample_supplier
    mock_client.suppliers.delete.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await supplier_service.delete("SUP-001")
