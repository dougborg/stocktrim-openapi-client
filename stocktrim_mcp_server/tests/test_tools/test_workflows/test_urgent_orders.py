"""Tests for urgent order workflow tools."""

from unittest.mock import AsyncMock

import pytest
from fastmcp.tools import ToolResult

from stocktrim_mcp_server.tools.tool_result_utils import (
    tool_result_text,
    unwrap_tool_result,
)
from stocktrim_mcp_server.tools.workflows.urgent_orders import (
    GeneratePurchaseOrdersRequest,
    GeneratePurchaseOrdersResponse,
    ReviewUrgentOrdersRequest,
    ReviewUrgentOrdersResponse,
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


async def _review(
    request: ReviewUrgentOrdersRequest, ctx
) -> ReviewUrgentOrdersResponse:
    """Call the public wrapper and unwrap to the typed Pydantic response."""
    result = await review_urgent_order_requirements(request, ctx)
    return unwrap_tool_result(result, ReviewUrgentOrdersResponse)


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
    response = await _review(request, mock_urgent_context)

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
    response = await _review(request, mock_urgent_context)

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
    response = await _review(request, mock_urgent_context)

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
    response = await _review(request, mock_urgent_context)

    # Verify cost calculation (15.50 * 100.0 = 1550.0)
    assert response.total_estimated_cost == 1550.0
    assert response.suppliers[0].total_estimated_cost == 1550.0


@pytest.mark.asyncio
async def test_review_urgent_orders_sends_singular_filter_criteria(
    mock_urgent_context, urgent_order_item
):
    """The /api/OrderPlan endpoint expects OrderPlanFilterCriteria (singular
    `location`/`supplier`/`category`), not OrderPlanFilterCriteriaDto. Sending
    the Dto returns 415 from StockTrim (bug surfaced 2026-05-26).
    """
    from stocktrim_public_api_client.generated.models.order_plan_filter_criteria import (
        OrderPlanFilterCriteria,
    )

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    request = ReviewUrgentOrdersRequest(
        days_threshold=30,
        location_codes=["WH-01"],
        supplier_codes=["SUP-001"],
        category="Widgets",
    )
    await _review(request, mock_urgent_context)

    mock_client.order_plan.query.assert_called_once()
    criteria = mock_client.order_plan.query.call_args.args[0]
    assert isinstance(criteria, OrderPlanFilterCriteria)
    # Singular fields mapped from the list-shaped request:
    assert criteria.location == "WH-01"
    assert criteria.supplier == "SUP-001"
    assert criteria.category == "Widgets"


@pytest.mark.asyncio
async def test_review_urgent_orders_narrows_multifilter_with_warning(
    mock_urgent_context, urgent_order_item
):
    """When multiple locations/suppliers are requested, only the first is
    sent to the API (which doesn't support multi-filter) and a warning is
    logged so operators see that the others were dropped."""
    import structlog.testing

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    request = ReviewUrgentOrdersRequest(
        days_threshold=30,
        location_codes=["WH-01", "WH-02"],
        supplier_codes=["SUP-001", "SUP-002", "SUP-003"],
    )
    with structlog.testing.capture_logs() as captured:
        await _review(request, mock_urgent_context)

    criteria = mock_client.order_plan.query.call_args.args[0]
    assert criteria.location == "WH-01"
    assert criteria.supplier == "SUP-001"
    # Both narrowings should have surfaced as warnings.
    warnings = [
        r
        for r in captured
        if r.get("log_level") == "warning"
        and r.get("event") == "order_plan_multifilter_narrowed"
    ]
    by_field = {r["field"]: r for r in warnings}
    assert set(by_field) == {"location_codes", "supplier_codes"}
    # Counts and bounded previews replace the raw `dropped` list to keep
    # structured logs small when callers pass long filter lists.
    assert by_field["location_codes"]["dropped_count"] == 1
    assert by_field["location_codes"]["dropped_preview"] == ["WH-02"]
    assert by_field["supplier_codes"]["dropped_count"] == 2
    assert by_field["supplier_codes"]["dropped_preview"] == ["SUP-002", "SUP-003"]


@pytest.mark.asyncio
async def test_review_urgent_orders_caps_warning_preview_for_long_lists(
    mock_urgent_context, urgent_order_item
):
    """A very long list should still narrow to one value, but the warning
    log only carries a bounded preview (not the full dropped list) so
    structured logs don't bloat for outlier inputs."""
    import structlog.testing

    from stocktrim_mcp_server.tools.workflows.urgent_orders import (
        _NARROWED_LOG_PREVIEW,
    )

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    long_locations = [f"WH-{i:03d}" for i in range(50)]
    request = ReviewUrgentOrdersRequest(
        days_threshold=30, location_codes=long_locations
    )
    with structlog.testing.capture_logs() as captured:
        await _review(request, mock_urgent_context)

    warning = next(
        r
        for r in captured
        if r.get("event") == "order_plan_multifilter_narrowed"
        and r.get("field") == "location_codes"
    )
    # 50 inputs → first kept, remaining 49 dropped; preview must be exactly
    # the impl's cap (not a looser bound — looser would silently regress).
    assert warning["dropped_count"] == 49
    assert len(warning["dropped_preview"]) == _NARROWED_LOG_PREVIEW
    # Preview starts at the right offset (first dropped element).
    assert warning["dropped_preview"][0] == "WH-001"
    assert warning["dropped_preview"][-1] == f"WH-{_NARROWED_LOG_PREVIEW:03d}"


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
    response = await _review(request, mock_urgent_context)

    # Verify - only items with days_until_stock_out < 15 should be included
    assert response.total_items == 1
    assert response.suppliers[0].items[0].product_code == "URGENT-001"


# ============================================================================
# Test review_urgent_order_requirements (public wrapper — ToolResult shape)
# ============================================================================


@pytest.mark.asyncio
async def test_review_urgent_orders_returns_tool_result_with_json_content(
    mock_urgent_context, urgent_order_item
):
    """Public wrapper returns a ToolResult with JSON content + structured payload."""
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent_order_item]

    request = ReviewUrgentOrdersRequest(days_threshold=30)
    result = await review_urgent_order_requirements(request, mock_urgent_context)

    assert isinstance(result, ToolResult)

    response = unwrap_tool_result(result, ReviewUrgentOrdersResponse)
    assert response.total_items == 1
    assert response.suppliers[0].supplier_code == "SUP-001"

    # content is the JSON-serialized response (LLM model context per SEP-1865).
    text = tool_result_text(result)
    assert text == response.model_dump_json(indent=2)


@pytest.mark.asyncio
async def test_review_urgent_orders_empty_state_round_trips(
    mock_urgent_context,
):
    """Empty result still produces a typed payload that round-trips."""
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = []

    request = ReviewUrgentOrdersRequest(days_threshold=30)
    result = await review_urgent_order_requirements(request, mock_urgent_context)

    response = unwrap_tool_result(result, ReviewUrgentOrdersResponse)
    assert response.total_items == 0
    assert response.suppliers == []
    assert response.total_estimated_cost is None


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
    result = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )
    response = unwrap_tool_result(result, GeneratePurchaseOrdersResponse)

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
    result = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )
    response = unwrap_tool_result(result, GeneratePurchaseOrdersResponse)

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
    result = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )
    response = unwrap_tool_result(result, GeneratePurchaseOrdersResponse)

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
    result = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )
    response = unwrap_tool_result(result, GeneratePurchaseOrdersResponse)

    # Verify
    assert response.total_count == 1

    # Verify filter criteria was passed correctly
    call_args = mock_client.purchase_orders_v2.generate_from_order_plan.call_args
    filter_criteria = call_args[0][0]
    assert filter_criteria.location_codes == ["WH-01", "WH-02"]
    assert filter_criteria.supplier_codes == ["SUP-001", "SUP-002"]


# ============================================================================
# Session preference fallback (#150)
# ============================================================================


@pytest.mark.asyncio
async def test_review_urgent_orders_falls_back_to_pref_threshold(mock_urgent_context):
    """When request.days_threshold is None, prefs.days_threshold is used."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    # Stub get_state to return our preference dict.
    pref = SessionPreferences(days_threshold=15)
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    # 5-day item (urgent under threshold=15) and 20-day item (not urgent).
    urgent = SkuOptimizedResultsDto(
        product_code="URGENT-001", days_until_stock_out=5, order_quantity=10.0
    )
    not_urgent = SkuOptimizedResultsDto(
        product_code="OK-001", days_until_stock_out=20, order_quantity=10.0
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent, not_urgent]

    # No days_threshold supplied — must inherit from prefs.
    request = ReviewUrgentOrdersRequest()
    response = await _review(request, mock_urgent_context)

    assert response.total_items == 1
    assert response.suppliers[0].items[0].product_code == "URGENT-001"


@pytest.mark.asyncio
async def test_review_urgent_orders_explicit_arg_wins_over_pref(mock_urgent_context):
    """Explicit request.days_threshold overrides any stored preference."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(days_threshold=100)  # would let the 20-day item through
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    urgent = SkuOptimizedResultsDto(
        product_code="URGENT-001", days_until_stock_out=5, order_quantity=10.0
    )
    not_urgent = SkuOptimizedResultsDto(
        product_code="OK-001", days_until_stock_out=20, order_quantity=10.0
    )
    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = [urgent, not_urgent]

    # Explicit 10 should override pref's 100.
    request = ReviewUrgentOrdersRequest(days_threshold=10)
    response = await _review(request, mock_urgent_context)

    assert response.total_items == 1
    assert response.suppliers[0].items[0].product_code == "URGENT-001"


@pytest.mark.asyncio
async def test_review_urgent_orders_falls_back_to_pref_supplier(mock_urgent_context):
    """When request.supplier_codes is omitted, the saved supplier_code
    preference is applied to the (singular) OrderPlanFilterCriteria.supplier
    sent to the /api/OrderPlan endpoint."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(supplier_code="SUP-PREF")
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = []

    request = ReviewUrgentOrdersRequest()  # no supplier_codes
    await _review(request, mock_urgent_context)

    mock_client.order_plan.query.assert_called_once()
    filter_criteria = mock_client.order_plan.query.call_args.args[0]
    assert filter_criteria.supplier == "SUP-PREF"


@pytest.mark.asyncio
async def test_review_urgent_orders_explicit_supplier_codes_override_pref(
    mock_urgent_context,
):
    """Explicit request.supplier_codes overrides the saved preference."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(supplier_code="SUP-PREF")
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = []

    request = ReviewUrgentOrdersRequest(supplier_codes=["SUP-EXPLICIT"])
    await _review(request, mock_urgent_context)

    filter_criteria = mock_client.order_plan.query.call_args.args[0]
    assert filter_criteria.supplier == "SUP-EXPLICIT"


@pytest.mark.asyncio
async def test_review_urgent_orders_explicit_empty_clears_pref(mock_urgent_context):
    """An explicit empty list must clear the filter, not fall back to the
    stored preference — `or`-based truthiness would silently apply the pref."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(location_code="WH-PREF", supplier_code="SUP-PREF")
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.order_plan.query.return_value = []

    # Explicit empty lists — caller is asking for an unfiltered query.
    request = ReviewUrgentOrdersRequest(location_codes=[], supplier_codes=[])
    await _review(request, mock_urgent_context)

    filter_criteria = mock_client.order_plan.query.call_args.args[0]
    # Empty list is falsy, so the helper sends UNSET (no filter) to the API.
    from stocktrim_public_api_client.client_types import UNSET

    assert filter_criteria.location is UNSET
    assert filter_criteria.supplier is UNSET


@pytest.mark.asyncio
async def test_generate_purchase_orders_falls_back_to_pref_supplier(
    mock_urgent_context,
):
    """generate_purchase_orders_from_urgent_items must honor the saved
    supplier_code preference too — otherwise it generates POs for *all*
    suppliers when the user intended only their saved one."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(supplier_code="SUP-PREF")
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    mock_client = mock_urgent_context.request_context.lifespan_context.client
    mock_client.purchase_orders_v2.generate_from_order_plan.return_value = []

    request = GeneratePurchaseOrdersRequest()  # no supplier_codes
    await generate_purchase_orders_from_urgent_items(request, mock_urgent_context)

    mock_client.purchase_orders_v2.generate_from_order_plan.assert_called_once()
    filter_criteria = (
        mock_client.purchase_orders_v2.generate_from_order_plan.call_args.args[0]
    )
    assert filter_criteria.supplier_codes == ["SUP-PREF"]


@pytest.mark.asyncio
async def test_generate_purchase_orders_dry_run_skips_api_call(mock_urgent_context):
    """dry_run preference must short-circuit before any API mutation."""
    from stocktrim_mcp_server.tools.preferences import SessionPreferences

    pref = SessionPreferences(dry_run=True)
    mock_urgent_context.get_state = AsyncMock(return_value=pref.model_dump())
    mock_urgent_context.set_state = AsyncMock()

    mock_client = mock_urgent_context.request_context.lifespan_context.client

    request = GeneratePurchaseOrdersRequest(days_threshold=30)
    result = await generate_purchase_orders_from_urgent_items(
        request, mock_urgent_context
    )
    response = unwrap_tool_result(result, GeneratePurchaseOrdersResponse)

    # No POs generated, no API call made.
    assert response.total_count == 0
    assert response.purchase_orders == []
    mock_client.purchase_orders_v2.generate_from_order_plan.assert_not_called()
