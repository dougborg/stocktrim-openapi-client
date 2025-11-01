"""Tests for purchase order foundation tools."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.foundation.purchase_orders import (
    CreatePurchaseOrderRequest,
    DeletePurchaseOrderRequest,
    GetPurchaseOrderRequest,
    LineItemRequest,
    ListPurchaseOrdersRequest,
    create_purchase_order,
    delete_purchase_order,
    get_purchase_order,
    list_purchase_orders,
)
from stocktrim_public_api_client.generated.models.purchase_order_line_item import (
    PurchaseOrderLineItem,
)
from stocktrim_public_api_client.generated.models.purchase_order_location import (
    PurchaseOrderLocation,
)
from stocktrim_public_api_client.generated.models.purchase_order_response_dto import (
    PurchaseOrderResponseDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_status_dto import (
    PurchaseOrderStatusDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_supplier import (
    PurchaseOrderSupplier,
)


@pytest.fixture
def sample_purchase_order():
    """Create a sample purchase order for testing."""
    return PurchaseOrderResponseDto(
        reference_number="PO-2024-001",
        order_date=datetime(2024, 1, 15),
        supplier=PurchaseOrderSupplier(
            supplier_code="SUP-001",
            supplier_name="Test Supplier",
        ),
        location=PurchaseOrderLocation(
            location_code="WH-001",
            location_name="Main Warehouse",
        ),
        purchase_order_line_items=[
            PurchaseOrderLineItem(
                product_id="WIDGET-001",
                quantity=100.0,
                unit_price=15.50,
            ),
            PurchaseOrderLineItem(
                product_id="GADGET-001",
                quantity=50.0,
                unit_price=25.00,
            ),
        ],
        status=PurchaseOrderStatusDto.DRAFT,
    )


@pytest.fixture
def mock_po_context(mock_context):
    """Extend mock_context with purchase_orders helper."""
    mock_context.request_context.lifespan_context.client.purchase_orders = AsyncMock()
    return mock_context


# ============================================================================
# Test get_purchase_order
# ============================================================================


@pytest.mark.asyncio
async def test_get_purchase_order_success(mock_po_context, sample_purchase_order):
    """Test successfully getting a purchase order."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.find_by_reference.return_value = sample_purchase_order

    # Execute
    request = GetPurchaseOrderRequest(reference_number="PO-2024-001")
    response = await get_purchase_order(request, mock_po_context)

    # Verify
    assert response is not None
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    assert response.supplier_name == "Test Supplier"
    assert response.status == "Draft"
    assert response.total_cost == 2800.0
    assert response.line_items_count == 2

    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-2024-001")


@pytest.mark.asyncio
async def test_get_purchase_order_not_found(mock_po_context):
    """Test getting a purchase order that doesn't exist."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.find_by_reference.return_value = None

    # Execute
    request = GetPurchaseOrderRequest(reference_number="PO-MISSING")
    response = await get_purchase_order(request, mock_po_context)

    # Verify
    assert response is None
    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-MISSING")


@pytest.mark.asyncio
async def test_get_purchase_order_empty_reference(mock_po_context):
    """Test getting a purchase order with empty reference number."""
    # Execute & Verify
    request = GetPurchaseOrderRequest(reference_number="")
    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await get_purchase_order(request, mock_po_context)


# ============================================================================
# Test list_purchase_orders
# ============================================================================


@pytest.mark.asyncio
async def test_list_purchase_orders_success(mock_po_context, sample_purchase_order):
    """Test successfully listing purchase orders."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.get_all.return_value = [sample_purchase_order]

    # Execute
    request = ListPurchaseOrdersRequest()
    response = await list_purchase_orders(request, mock_po_context)

    # Verify
    assert response.total_count == 1
    assert len(response.purchase_orders) == 1
    assert response.purchase_orders[0].reference_number == "PO-2024-001"
    assert response.purchase_orders[0].supplier_code == "SUP-001"


@pytest.mark.asyncio
async def test_list_purchase_orders_empty(mock_po_context):
    """Test listing purchase orders when none exist."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.get_all.return_value = []

    # Execute
    request = ListPurchaseOrdersRequest()
    response = await list_purchase_orders(request, mock_po_context)

    # Verify
    assert response.total_count == 0
    assert len(response.purchase_orders) == 0


@pytest.mark.asyncio
async def test_list_purchase_orders_api_returns_single_object(
    mock_po_context, sample_purchase_order
):
    """Test listing when API returns single object instead of list."""
    # Setup - API inconsistency where it returns single object
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.get_all.return_value = sample_purchase_order

    # Execute
    request = ListPurchaseOrdersRequest()
    response = await list_purchase_orders(request, mock_po_context)

    # Verify - should handle single object and convert to list
    assert response.total_count == 1
    assert len(response.purchase_orders) == 1
    assert response.purchase_orders[0].reference_number == "PO-2024-001"


# ============================================================================
# Test create_purchase_order
# ============================================================================


@pytest.mark.asyncio
async def test_create_purchase_order_success(mock_po_context, sample_purchase_order):
    """Test successfully creating a purchase order."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    request = CreatePurchaseOrderRequest(
        supplier_code="SUP-001",
        supplier_name="Test Supplier",
        line_items=[
            LineItemRequest(
                product_code="WIDGET-001",
                quantity=100.0,
                unit_price=15.50,
            ),
            LineItemRequest(
                product_code="GADGET-001",
                quantity=50.0,
                unit_price=25.00,
            ),
        ],
        location_code="WH-001",
        location_name="Main Warehouse",
        status="Draft",
    )
    response = await create_purchase_order(request, mock_po_context)

    # Verify
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    assert response.supplier_name == "Test Supplier"
    assert response.status == "Draft"
    assert response.total_cost == 2800.0
    assert response.line_items_count == 2
    assert "created successfully" in response.message

    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_minimal_fields(
    mock_po_context, sample_purchase_order
):
    """Test creating a purchase order with minimal required fields."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    request = CreatePurchaseOrderRequest(
        supplier_code="SUP-001",
        line_items=[
            LineItemRequest(product_code="WIDGET-001", quantity=10.0),
        ],
    )
    response = await create_purchase_order(request, mock_po_context)

    # Verify
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_empty_supplier_code(mock_po_context):
    """Test creating a purchase order with empty supplier code."""
    # Execute & Verify
    request = CreatePurchaseOrderRequest(
        supplier_code="",
        line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
    )
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await create_purchase_order(request, mock_po_context)


@pytest.mark.asyncio
async def test_create_purchase_order_no_line_items(mock_po_context):
    """Test creating a purchase order with no line items.

    Pydantic validation should reject this at the request level.
    """
    # Execute & Verify - Pydantic will validate min_length=1
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CreatePurchaseOrderRequest(
            supplier_code="SUP-001",
            line_items=[],
        )


@pytest.mark.asyncio
async def test_create_purchase_order_with_custom_date(
    mock_po_context, sample_purchase_order
):
    """Test creating a purchase order with a custom order date."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    request = CreatePurchaseOrderRequest(
        supplier_code="SUP-001",
        line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
        order_date="2024-01-15",
    )
    response = await create_purchase_order(request, mock_po_context)

    # Verify
    assert response.reference_number == "PO-2024-001"
    mock_client.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_with_different_statuses(
    mock_po_context, sample_purchase_order
):
    """Test creating a purchase order with different valid statuses."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.create.return_value = sample_purchase_order

    # Test each valid status
    for status in ["Draft", "Approved", "Sent", "Received"]:
        request = CreatePurchaseOrderRequest(
            supplier_code="SUP-001",
            line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
            status=status,
        )
        response = await create_purchase_order(request, mock_po_context)
        assert response.reference_number == "PO-2024-001"

    # Verify create was called for each status
    assert mock_client.purchase_orders.create.call_count == 4


# ============================================================================
# Test delete_purchase_order
# ============================================================================


@pytest.mark.asyncio
async def test_delete_purchase_order_success(mock_po_context, sample_purchase_order):
    """Test successfully deleting a purchase order."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.find_by_reference.return_value = sample_purchase_order
    mock_client.purchase_orders.delete.return_value = sample_purchase_order

    # Execute
    request = DeletePurchaseOrderRequest(reference_number="PO-2024-001")
    response = await delete_purchase_order(request, mock_po_context)

    # Verify
    assert response.success is True
    assert "deleted successfully" in response.message
    assert "PO-2024-001" in response.message

    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-2024-001")
    mock_client.purchase_orders.delete.assert_called_once_with(
        reference_number="PO-2024-001"
    )


@pytest.mark.asyncio
async def test_delete_purchase_order_not_found(mock_po_context):
    """Test deleting a purchase order that doesn't exist."""
    # Setup
    mock_client = mock_po_context.request_context.lifespan_context.client
    mock_client.purchase_orders.find_by_reference.return_value = None

    # Execute
    request = DeletePurchaseOrderRequest(reference_number="PO-MISSING")
    response = await delete_purchase_order(request, mock_po_context)

    # Verify
    assert response.success is False
    assert "not found" in response.message
    assert "PO-MISSING" in response.message

    mock_client.purchase_orders.find_by_reference.assert_called_once_with("PO-MISSING")
    mock_client.purchase_orders.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_purchase_order_empty_reference(mock_po_context):
    """Test deleting a purchase order with empty reference number."""
    # Execute & Verify
    request = DeletePurchaseOrderRequest(reference_number="")
    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await delete_purchase_order(request, mock_po_context)
