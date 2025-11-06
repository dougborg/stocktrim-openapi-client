"""Tests for urgent order workflow tools."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.tools.workflows.urgent_orders import (
    GeneratePurchaseOrdersRequest,
    ReviewUrgentOrdersRequest,
    generate_purchase_orders_from_urgent_items,
    review_urgent_order_requirements,
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
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)


@pytest.fixture
def urgent_order_item():
    """Create a sample urgent order item."""
    return SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        name="Blue Widget",
        stock_on_hand=5.0,
        days_until_stock_out=10,
        order_quantity=100.0,
        sku_cost=15.50,
        location_name="Main Warehouse",
    )


@pytest.fixture
def mock_urgent_context(mock_context):
    """Extend mock_context for urgent order workflows."""
    from stocktrim_public_api_client.generated.models.products_response_dto import (
        ProductsResponseDto,
    )

    mock_client = mock_context.request_context.lifespan_context.client
    mock_client.order_plan = AsyncMock()
    mock_client.purchase_orders_v2 = AsyncMock()

    # Mock products service for supplier lookup with supplier_code
    product_with_supplier = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        name="Test Widget",
        supplier_code="SUP-001",  # Add supplier code for lookup
    )

    services = mock_context.request_context.lifespan_context
    services.products = AsyncMock()
    services.products.list_all.return_value = [product_with_supplier]

    return mock_context


# ============================================================================
# Test review_urgent_order_requirements
# ============================================================================


@pytest.mark.asyncio
async def test_review_urgent_orders_success(mock_urgent_context, urgent_order_item):
    """Test successfully reviewing urgent order requirements."""
    # Setup
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    # Execute
    request = ReviewUrgentOrdersRequest(
        days_threshold=30,
        location_codes=["WH-01"],
        supplier_codes=["SUP-001"],
    )
    response = await review_urgent_order_requirements(request, mock_urgent_context)

    # Verify
    assert response.total_items == 1
    assert len(response.suppliers) == 1
    assert response.suppliers[0].supplier_code == "SUP-001"
    assert response.suppliers[0].total_items == 1
    assert len(response.suppliers[0].items) == 1
    assert response.suppliers[0].items[0].product_code == "WIDGET-001"
    assert response.suppliers[0].items[0].days_until_stock_out == 10

    mock_client.order_plan.query.assert_called_once()


@pytest.mark.asyncio
async def test_review_urgent_orders_no_urgent_items(mock_urgent_context):
    """Test reviewing when no items are urgent."""
    # Setup - items with days_until_stock_out > threshold
    item = SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        days_until_stock_out=50,  # Not urgent (> 30 days threshold)
        order_quantity=100.0,
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [item]

    # Execute
    request = ReviewUrgentOrdersRequest(days_threshold=30)
    response = await review_urgent_order_requirements(request, mock_urgent_context)

    # Verify
    assert response.total_items == 0
    assert len(response.suppliers) == 0
    assert response.total_estimated_cost is None


@pytest.mark.asyncio
async def test_review_urgent_orders_multiple_suppliers(mock_urgent_context):
    """Test reviewing urgent orders with multiple suppliers."""
    from stocktrim_public_api_client.generated.models.products_response_dto import (
        ProductsResponseDto,
    )

    # Setup - Create items for different suppliers
    item1 = SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        days_until_stock_out=10,
        order_quantity=100.0,
        sku_cost=15.50,
    )
    item2 = SkuOptimizedResultsDto(
        product_code="GADGET-001",
        days_until_stock_out=15,
        order_quantity=50.0,
        sku_cost=25.00,
    )

    # Mock products with different suppliers
    product1 = ProductsResponseDto(
        product_id="prod-123",
        product_code_readable="WIDGET-001",
        supplier_code="SUP-001",
    )
    product2 = ProductsResponseDto(
        product_id="prod-456",
        product_code_readable="GADGET-001",
        supplier_code="SUP-002",
    )

    services = mock_urgent_context.request_context.lifespan_context
    services.products.list_all.return_value = [product1, product2]

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [item1, item2]

    # Execute
    request = ReviewUrgentOrdersRequest(days_threshold=30)
    response = await review_urgent_order_requirements(request, mock_urgent_context)

    # Verify
    assert response.total_items == 2
    assert len(response.suppliers) == 2
    # Suppliers should be sorted by total_items descending, but both have 1 item
    supplier_codes = {s.supplier_code for s in response.suppliers}
    assert "SUP-001" in supplier_codes
    assert "SUP-002" in supplier_codes


@pytest.mark.asyncio
async def test_review_urgent_orders_with_cost_calculation(
    mock_urgent_context, urgent_order_item
):
    """Test reviewing urgent orders with cost calculation."""
    # Setup
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    # Execute
    request = ReviewUrgentOrdersRequest(days_threshold=30)
    response = await review_urgent_order_requirements(request, mock_urgent_context)

    # Verify cost calculation (15.50 * 100.0 = 1550.0)
    assert response.total_estimated_cost == 1550.0
    assert response.suppliers[0].total_estimated_cost == 1550.0


@pytest.mark.asyncio
async def test_review_urgent_orders_filters_by_threshold(mock_urgent_context):
    """Test that items are filtered by days_threshold."""
    # Setup - Mix of urgent and non-urgent items
    urgent_item = SkuOptimizedResultsDto(
        product_code="URGENT-001",
        days_until_stock_out=5,
        order_quantity=10.0,
    )
    not_urgent_item = SkuOptimizedResultsDto(
        product_code="OK-001",
        days_until_stock_out=20,
        order_quantity=10.0,
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_item, not_urgent_item]

    # Execute with threshold of 15 days
    request = ReviewUrgentOrdersRequest(days_threshold=15)
    response = await review_urgent_order_requirements(request, mock_urgent_context)

    # Verify - only items with days_until_stock_out < 15 should be included
    assert response.total_items == 1
    assert response.suppliers[0].items[0].product_code == "URGENT-001"


# ============================================================================
# Test generate_purchase_orders_from_urgent_items
# ============================================================================


@pytest.mark.asyncio
async def test_generate_purchase_orders_success(mock_urgent_context):
    """Test successfully generating purchase orders."""
    # Setup
    po = PurchaseOrderResponseDto(
        reference_number="PO-2024-001",
        supplier=PurchaseOrderSupplier(
            supplier_code="SUP-001",
            supplier_name="Acme Supplies",
        ),
        purchase_order_line_items=[],
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.purchase_orders_v2.generate_from_order_plan.return_value = [po]

    # Execute
    request = GeneratePurchaseOrdersRequest(
        days_threshold=30,
        location_codes=["WH-01"],
        supplier_codes=["SUP-001"],
    )
    response = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )

    # Verify
    assert response.total_count == 1
    assert len(response.purchase_orders) == 1
    assert response.purchase_orders[0].reference_number == "PO-2024-001"
    assert response.purchase_orders[0].supplier_code == "SUP-001"
    assert response.purchase_orders[0].supplier_name == "Acme Supplies"
    assert response.purchase_orders[0].status == "Draft"

    mock_client.purchase_orders_v2.generate_from_order_plan.assert_called_once()


@pytest.mark.asyncio
async def test_generate_purchase_orders_no_orders(mock_urgent_context):
    """Test generating purchase orders when none are needed."""
    # Setup
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.purchase_orders_v2.generate_from_order_plan.return_value = []

    # Execute
    request = GeneratePurchaseOrdersRequest(days_threshold=30)
    response = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )

    # Verify
    assert response.total_count == 0
    assert len(response.purchase_orders) == 0


@pytest.mark.asyncio
async def test_generate_purchase_orders_multiple(mock_urgent_context):
    """Test generating multiple purchase orders."""
    # Setup
    po1 = PurchaseOrderResponseDto(
        reference_number="PO-2024-001",
        supplier=PurchaseOrderSupplier(
            supplier_code="SUP-001",
            supplier_name="Acme Supplies",
        ),
        purchase_order_line_items=[{}, {}],  # 2 items
        status=PurchaseOrderStatusDto.DRAFT,
    )
    po2 = PurchaseOrderResponseDto(
        reference_number="PO-2024-002",
        supplier=PurchaseOrderSupplier(
            supplier_code="SUP-002",
            supplier_name="Beta Corp",
        ),
        purchase_order_line_items=[{}, {}, {}],  # 3 items
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.purchase_orders_v2.generate_from_order_plan.return_value = [po1, po2]

    # Execute
    request = GeneratePurchaseOrdersRequest(days_threshold=14)
    response = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )

    # Verify
    assert response.total_count == 2
    assert len(response.purchase_orders) == 2
    assert response.purchase_orders[0].item_count == 2
    assert response.purchase_orders[1].item_count == 3


@pytest.mark.asyncio
async def test_generate_purchase_orders_with_filters(mock_urgent_context):
    """Test generating purchase orders with location and supplier filters."""
    # Setup
    po = PurchaseOrderResponseDto(
        reference_number="PO-2024-001",
        supplier=PurchaseOrderSupplier(supplier_code="SUP-001", supplier_name="Acme"),
        purchase_order_line_items=[],
        status=PurchaseOrderStatusDto.DRAFT,
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.purchase_orders_v2.generate_from_order_plan.return_value = [po]

    # Execute
    request = GeneratePurchaseOrdersRequest(
        days_threshold=30,
        location_codes=["WH-01", "WH-02"],
        supplier_codes=["SUP-001", "SUP-002"],
    )
    response = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )

    # Verify
    assert response.total_count == 1

    # Verify filter criteria was passed correctly
    call_args = mock_client.purchase_orders_v2.generate_from_order_plan.call_args
    filter_criteria = call_args[0][0]
    assert filter_criteria.location_codes == ["WH-01", "WH-02"]
    assert filter_criteria.supplier_codes == ["SUP-001", "SUP-002"]
