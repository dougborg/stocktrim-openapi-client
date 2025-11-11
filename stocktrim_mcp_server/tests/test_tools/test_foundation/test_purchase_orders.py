"""Tests for purchase order foundation tools."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from stocktrim_mcp_server.tools.foundation.purchase_orders import (
    CreatePurchaseOrderRequest,
    LineItemRequest,
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
    """Extend mock_context with purchase_orders service."""
    services = mock_context.request_context.lifespan_context
    services.purchase_orders = AsyncMock()
    return mock_context


# ============================================================================
# Test get_purchase_order
# ============================================================================


@pytest.mark.asyncio
async def test_get_purchase_order_success(mock_po_context, sample_purchase_order):
    """Test successfully getting a purchase order."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = sample_purchase_order

    # Execute
    response = await get_purchase_order(
        reference_number="PO-2024-001", context=mock_po_context
    )

    # Verify
    assert response is not None
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    assert response.supplier_name == "Test Supplier"
    assert response.status == "Draft"
    assert response.total_cost == 2800.0
    assert response.line_items_count == 2

    services.purchase_orders.get_by_reference.assert_called_once_with("PO-2024-001")


@pytest.mark.asyncio
async def test_get_purchase_order_not_found(mock_po_context):
    """Test getting a purchase order that doesn't exist."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = None

    # Execute
    response = await get_purchase_order(
        reference_number="PO-MISSING", context=mock_po_context
    )

    # Verify
    assert response is None
    services.purchase_orders.get_by_reference.assert_called_once_with("PO-MISSING")


@pytest.mark.asyncio
async def test_get_purchase_order_empty_reference(mock_po_context):
    """Test getting a purchase order with empty reference number."""
    # Setup - mock service to raise ValueError for empty reference
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.side_effect = ValueError(
        "Reference number cannot be empty"
    )

    # Execute & Verify
    with pytest.raises(ValueError, match="Reference number cannot be empty"):
        await get_purchase_order(reference_number="", context=mock_po_context)


# ============================================================================
# Test list_purchase_orders
# ============================================================================


@pytest.mark.asyncio
async def test_list_purchase_orders_success(mock_po_context, sample_purchase_order):
    """Test successfully listing purchase orders."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.list_all.return_value = [sample_purchase_order]

    # Execute
    response = await list_purchase_orders(context=mock_po_context)

    # Verify
    assert response.total_count == 1
    assert len(response.purchase_orders) == 1
    assert response.purchase_orders[0].reference_number == "PO-2024-001"
    assert response.purchase_orders[0].supplier_code == "SUP-001"


@pytest.mark.asyncio
async def test_list_purchase_orders_empty(mock_po_context):
    """Test listing purchase orders when none exist."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.list_all.return_value = []

    # Execute
    response = await list_purchase_orders(context=mock_po_context)

    # Verify
    assert response.total_count == 0
    assert len(response.purchase_orders) == 0


@pytest.mark.asyncio
async def test_list_purchase_orders_api_returns_single_object(
    mock_po_context, sample_purchase_order
):
    """Test listing when API returns single object instead of list."""
    # Setup - API inconsistency where it returns single object
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.list_all.return_value = sample_purchase_order

    # Execute
    response = await list_purchase_orders(context=mock_po_context)

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
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    response = await create_purchase_order(
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
        context=mock_po_context,
    )

    # Verify
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    assert response.supplier_name == "Test Supplier"
    assert response.status == "Draft"
    assert response.total_cost == 2800.0
    assert response.line_items_count == 2
    services.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_minimal_fields(
    mock_po_context, sample_purchase_order
):
    """Test creating a purchase order with minimal required fields."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    response = await create_purchase_order(
        supplier_code="SUP-001",
        line_items=[
            LineItemRequest(product_code="WIDGET-001", quantity=10.0),
        ],
        context=mock_po_context,
    )

    # Verify
    assert response.reference_number == "PO-2024-001"
    assert response.supplier_code == "SUP-001"
    services.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_empty_supplier_code(mock_po_context):
    """Test creating a purchase order with empty supplier code."""
    # Setup - mock service to raise ValueError for empty supplier code
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.create.side_effect = ValueError(
        "Supplier code cannot be empty"
    )

    # Execute & Verify
    with pytest.raises(ValueError, match="Supplier code cannot be empty"):
        await create_purchase_order(
            supplier_code="",
            line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
            context=mock_po_context,
        )


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
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.create.return_value = sample_purchase_order

    # Execute
    response = await create_purchase_order(
        supplier_code="SUP-001",
        line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
        order_date="2024-01-15",
        context=mock_po_context,
    )

    # Verify
    assert response.reference_number == "PO-2024-001"
    services.purchase_orders.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_purchase_order_with_different_statuses(
    mock_po_context, sample_purchase_order
):
    """Test creating a purchase order with different valid statuses."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.create.return_value = sample_purchase_order

    # Test each valid status
    for status in ["Draft", "Approved", "Sent", "Received"]:
        response = await create_purchase_order(
            supplier_code="SUP-001",
            line_items=[LineItemRequest(product_code="WIDGET-001", quantity=10.0)],
            status=status,
            context=mock_po_context,
        )
        assert response.reference_number == "PO-2024-001"

    # Verify create was called for each status
    assert services.purchase_orders.create.call_count == 4


# ============================================================================
# Test delete_purchase_order
# ============================================================================


@pytest.mark.asyncio
async def test_delete_purchase_order_not_found(mock_po_context):
    """Test deleting a purchase order that doesn't exist."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = None

    # Execute
    response = await delete_purchase_order(
        reference_number="PO-MISSING", context=mock_po_context
    )

    # Verify
    assert response.success is False
    assert "not found" in response.message
    assert "PO-MISSING" in response.message


@pytest.mark.asyncio
async def test_delete_purchase_order_accepted(mock_po_context, sample_purchase_order):
    """Test deleting a purchase order when user accepts confirmation."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = sample_purchase_order
    services.purchase_orders.delete.return_value = (
        True,
        "Purchase order PO-2024-001 deleted successfully",
    )
    mock_po_context.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))

    # Execute
    response = await delete_purchase_order(
        reference_number="PO-2024-001", context=mock_po_context
    )

    # Verify
    assert response.success is True
    assert "✅" in response.message
    assert "deleted successfully" in response.message

    # Verify elicitation was called with preview
    mock_po_context.elicit.assert_called_once()
    elicit_args = mock_po_context.elicit.call_args
    assert "⚠️ Delete purchase order" in elicit_args[1]["message"]
    assert "Test Supplier" in elicit_args[1]["message"]

    # Verify deletion was called
    services.purchase_orders.delete.assert_called_once_with("PO-2024-001")


@pytest.mark.asyncio
async def test_delete_purchase_order_declined(mock_po_context, sample_purchase_order):
    """Test deleting a purchase order when user declines confirmation."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = sample_purchase_order
    mock_po_context.elicit = AsyncMock(return_value=DeclinedElicitation(data=None))

    # Execute
    response = await delete_purchase_order(
        reference_number="PO-2024-001", context=mock_po_context
    )

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "declined" in response.message
    assert "PO-2024-001" in response.message

    # Verify deletion was NOT called
    services.purchase_orders.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_purchase_order_cancelled(mock_po_context, sample_purchase_order):
    """Test deleting a purchase order when user cancels confirmation."""
    # Setup
    services = mock_po_context.request_context.lifespan_context
    services.purchase_orders.get_by_reference.return_value = sample_purchase_order
    mock_po_context.elicit = AsyncMock(return_value=CancelledElicitation(data=None))

    # Execute
    response = await delete_purchase_order(
        reference_number="PO-2024-001", context=mock_po_context
    )

    # Verify
    assert response.success is False
    assert "❌" in response.message
    assert "cancelled" in response.message
    assert "PO-2024-001" in response.message

    # Verify deletion was NOT called
    services.purchase_orders.delete.assert_not_called()
