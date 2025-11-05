"""Tests for PurchaseOrderService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from stocktrim_mcp_server.services.purchase_orders import PurchaseOrderService
from stocktrim_public_api_client.generated.models import (
    PurchaseOrderLineItem,
    PurchaseOrderResponseDto,
    PurchaseOrderStatusDto,
    PurchaseOrderSupplier,
)


@pytest.fixture
def mock_client():
    """Create a mock StockTrimClient."""
    client = MagicMock()
    client.purchase_orders = MagicMock()
    client.purchase_orders.find_by_reference = AsyncMock()
    client.purchase_orders.get_all = AsyncMock()
    client.purchase_orders.create = AsyncMock()
    client.purchase_orders.delete = AsyncMock()
    return client


@pytest.fixture
def purchase_order_service(mock_client):
    """Create a PurchaseOrderService with mock client."""
    return PurchaseOrderService(mock_client)


@pytest.fixture
def sample_purchase_order():
    """Create a sample purchase order for testing."""
    supplier = PurchaseOrderSupplier(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
    )
    line_items = [
        PurchaseOrderLineItem(
            product_id="WIDGET-001",
            quantity=10.0,
            unit_price=5.0,
        )
    ]
    return PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.DRAFT,
    )


# ============================================================================
# Test get_by_reference
# ============================================================================


@pytest.mark.asyncio
async def test_get_by_reference_success(
    purchase_order_service, mock_client, sample_purchase_order
):
    """Test successfully getting a purchase order by reference."""
    mock_client.purchase_orders.find_by_reference.return_value = sample_purchase_order

    result = await purchase_order_service.get_by_reference("PO-001")

    assert result == sample_purchase_order
    assert result.reference_number == "PO-001"
    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-001")


@pytest.mark.asyncio
async def test_get_by_reference_not_found(purchase_order_service, mock_client):
    """Test getting a purchase order that doesn't exist."""
    mock_client.purchase_orders.find_by_reference.return_value = None

    result = await purchase_order_service.get_by_reference("NONEXISTENT")

    assert result is None
    mock_client.purchase_orders.find_by_reference.assert_called_once_with("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_by_reference_empty_reference(purchase_order_service):
    """Test error when reference number is empty."""
    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await purchase_order_service.get_by_reference("")

    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await purchase_order_service.get_by_reference("   ")


@pytest.mark.asyncio
async def test_get_by_reference_api_error(purchase_order_service, mock_client):
    """Test handling of API errors."""
    mock_client.purchase_orders.find_by_reference.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await purchase_order_service.get_by_reference("PO-001")


# ============================================================================
# Test list_all
# ============================================================================


@pytest.mark.asyncio
async def test_list_all_returns_list(purchase_order_service, mock_client):
    """Test listing purchase orders when API returns a list."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    po1 = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=1,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
    )
    po2 = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=2,
        reference_number="PO-002",
        order_date=datetime(2025, 1, 16),
    )
    mock_client.purchase_orders.get_all.return_value = [po1, po2]

    result = await purchase_order_service.list_all()

    assert len(result) == 2
    assert result[0].reference_number == "PO-001"
    assert result[1].reference_number == "PO-002"
    mock_client.purchase_orders.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_list_all_single_object_response(purchase_order_service, mock_client):
    """Test handling when API returns a single object instead of list."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    single_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=1,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
    )
    mock_client.purchase_orders.get_all.return_value = single_po

    result = await purchase_order_service.list_all()

    assert len(result) == 1
    assert result[0].reference_number == "PO-001"


@pytest.mark.asyncio
async def test_list_all_empty_list(purchase_order_service, mock_client):
    """Test listing when no purchase orders exist."""
    mock_client.purchase_orders.get_all.return_value = []

    result = await purchase_order_service.list_all()

    assert len(result) == 0


@pytest.mark.asyncio
async def test_list_all_none_response(purchase_order_service, mock_client):
    """Test listing when API returns None."""
    mock_client.purchase_orders.get_all.return_value = None

    result = await purchase_order_service.list_all()

    assert len(result) == 0


# ============================================================================
# Test create
# ============================================================================


@pytest.mark.asyncio
async def test_create_success(purchase_order_service, mock_client):
    """Test successfully creating a purchase order."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    created_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-NEW",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client.purchase_orders.create.return_value = created_po

    result = await purchase_order_service.create(
        supplier_code="SUP-001",
        line_items=[{"product_code": "WIDGET-001", "quantity": 10, "unit_price": 5.0}],
    )

    assert result.reference_number == "PO-NEW"
    assert result.status == PurchaseOrderStatusDto.DRAFT
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_with_all_params(purchase_order_service, mock_client):
    """Test creating a purchase order with all optional parameters."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    created_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-FULL",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.APPROVED,
    )
    mock_client.purchase_orders.create.return_value = created_po
    order_date = datetime(2025, 1, 15)

    result = await purchase_order_service.create(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        order_date=order_date,
        location_code="LOC-001",
        location_name="Warehouse 1",
        reference_number="PO-FULL",
        client_reference_number="CLIENT-REF",
        status="APPROVED",
    )

    assert result.reference_number == "PO-FULL"
    assert result.status == PurchaseOrderStatusDto.APPROVED
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_empty_supplier_code(purchase_order_service):
    """Test error when supplier code is empty."""
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await purchase_order_service.create(
            supplier_code="",
            line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        )

    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await purchase_order_service.create(
            supplier_code="   ",
            line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        )


@pytest.mark.asyncio
async def test_create_empty_line_items(purchase_order_service):
    """Test error when line items are empty."""
    with pytest.raises(ValueError, match="At least one line item is required"):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[],
        )


@pytest.mark.asyncio
async def test_create_line_item_missing_product_code(purchase_order_service):
    """Test error when line item is missing product_code."""
    with pytest.raises(
        ValueError, match="Each line item must have product_code and quantity"
    ):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"quantity": 10}],
        )


@pytest.mark.asyncio
async def test_create_line_item_missing_quantity(purchase_order_service):
    """Test error when line item is missing quantity."""
    with pytest.raises(
        ValueError, match="Each line item must have product_code and quantity"
    ):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"product_code": "WIDGET-001"}],
        )


@pytest.mark.asyncio
async def test_create_line_item_invalid_quantity(purchase_order_service):
    """Test error when line item has invalid quantity."""
    with pytest.raises(ValueError, match="Line item quantity must be greater than 0"):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"product_code": "WIDGET-001", "quantity": 0}],
        )

    with pytest.raises(ValueError, match="Line item quantity must be greater than 0"):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"product_code": "WIDGET-001", "quantity": -5}],
        )


@pytest.mark.asyncio
async def test_create_status_parsing_draft(purchase_order_service, mock_client):
    """Test status parsing for DRAFT status."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    created_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client.purchase_orders.create.return_value = created_po

    result = await purchase_order_service.create(
        supplier_code="SUP-001",
        line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        status="Draft",
    )

    assert result is not None
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_status_parsing_approved(purchase_order_service, mock_client):
    """Test status parsing for APPROVED status."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    created_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.APPROVED,
    )
    mock_client.purchase_orders.create.return_value = created_po

    result = await purchase_order_service.create(
        supplier_code="SUP-001",
        line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        status="APPROVED",
    )

    assert result is not None
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_invalid_status_defaults_to_draft(
    purchase_order_service, mock_client
):
    """Test that invalid status defaults to DRAFT."""
    supplier = PurchaseOrderSupplier(supplier_code="SUP-001")
    line_items = [PurchaseOrderLineItem(product_id="WIDGET-001", quantity=10.0)]

    created_po = PurchaseOrderResponseDto(
        supplier=supplier,
        purchase_order_line_items=line_items,
        id=123,
        reference_number="PO-001",
        order_date=datetime(2025, 1, 15),
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client.purchase_orders.create.return_value = created_po

    result = await purchase_order_service.create(
        supplier_code="SUP-001",
        line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        status="INVALID_STATUS",
    )

    assert result is not None
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_api_returns_none(purchase_order_service, mock_client):
    """Test error when API returns None."""
    mock_client.purchase_orders.create.return_value = None

    with pytest.raises(Exception, match="Failed to create purchase order"):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        )


@pytest.mark.asyncio
async def test_create_api_error(purchase_order_service, mock_client):
    """Test handling of API errors during creation."""
    mock_client.purchase_orders.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await purchase_order_service.create(
            supplier_code="SUP-001",
            line_items=[{"product_code": "WIDGET-001", "quantity": 10}],
        )


# ============================================================================
# Test delete
# ============================================================================


@pytest.mark.asyncio
async def test_delete_success(
    purchase_order_service, mock_client, sample_purchase_order
):
    """Test successfully deleting a purchase order."""
    mock_client.purchase_orders.find_by_reference.return_value = sample_purchase_order

    success, message = await purchase_order_service.delete("PO-001")

    assert success is True
    assert "deleted successfully" in message
    assert "PO-001" in message
    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-001")
    mock_client.purchase_orders.delete.assert_called_once_with(
        reference_number="PO-001"
    )


@pytest.mark.asyncio
async def test_delete_not_found(purchase_order_service, mock_client):
    """Test deleting a purchase order that doesn't exist."""
    mock_client.purchase_orders.find_by_reference.return_value = None

    success, message = await purchase_order_service.delete("NONEXISTENT")

    assert success is False
    assert "not found" in message
    assert "NONEXISTENT" in message
    mock_client.purchase_orders.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_empty_reference(purchase_order_service):
    """Test error when reference number is empty."""
    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await purchase_order_service.delete("")

    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await purchase_order_service.delete("   ")


@pytest.mark.asyncio
async def test_delete_api_error(
    purchase_order_service, mock_client, sample_purchase_order
):
    """Test handling of API errors during deletion."""
    mock_client.purchase_orders.find_by_reference.return_value = sample_purchase_order
    mock_client.purchase_orders.delete.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        await purchase_order_service.delete("PO-001")
