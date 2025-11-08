"""Tests for report resources."""

from unittest.mock import AsyncMock

import pytest

from stocktrim_mcp_server.resources.reports import (
    _get_inventory_status_report,
    _get_supplier_directory_report,
    _get_urgent_orders_report,
)
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_reports_context(mock_context):
    """Extend mock_context with report resource services."""
    services = mock_context.request_context.lifespan_context
    services.client = AsyncMock()
    services.client.order_plan = AsyncMock()
    services.suppliers = AsyncMock()
    return mock_context


# ============================================================================
# Tests for Inventory Status Report
# ============================================================================


@pytest.mark.asyncio
async def test_get_inventory_status_report_success(mock_reports_context):
    """Test successfully retrieving inventory status report."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            days_until_stock_out=5,
            stock_on_hand=20,
            order_quantity=100,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            days_until_stock_out=15,
            stock_on_hand=50,
            order_quantity=75,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-003",
            days_until_stock_out=25,
            stock_on_hand=100,
            order_quantity=50,
        ),
    ]
    services.client.order_plan.query.return_value = forecast_items

    # Execute
    result = await _get_inventory_status_report(30, mock_reports_context)

    # Verify
    assert result["report_type"] == "inventory_status"
    assert result["days_threshold"] == 30
    assert result["total_items"] == 3
    assert len(result["items"]) == 3

    # Verify urgency classification
    assert result["items"][0]["product_code"] == "WIDGET-001"
    assert result["items"][0]["urgency"] == "high"  # < 7 days
    assert result["items"][1]["urgency"] == "medium"  # >= 7 days
    assert result["items"][2]["urgency"] == "medium"

    services.client.order_plan.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_inventory_status_report_limits_results(mock_reports_context):
    """Test that report limits to 50 items for token budget."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_items = [
        SkuOptimizedResultsDto(
            product_code=f"WIDGET-{i:03d}",
            days_until_stock_out=10,
            stock_on_hand=50,
            order_quantity=100,
        )
        for i in range(1, 101)  # 100 items
    ]
    services.client.order_plan.query.return_value = forecast_items

    # Execute
    result = await _get_inventory_status_report(30, mock_reports_context)

    # Verify - should limit to 50
    assert len(result["items"]) == 50
    assert result["total_items"] == 50
    assert "Limited to 50 items" in result["note"]


@pytest.mark.asyncio
async def test_get_inventory_status_report_handles_single_object(mock_reports_context):
    """Test report handles single object response (not a list)."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_item = SkuOptimizedResultsDto(
        product_code="WIDGET-001",
        days_until_stock_out=5,
        stock_on_hand=20,
        order_quantity=100,
    )
    services.client.order_plan.query.return_value = forecast_item

    # Execute
    result = await _get_inventory_status_report(30, mock_reports_context)

    # Verify
    assert result["total_items"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["product_code"] == "WIDGET-001"


@pytest.mark.asyncio
async def test_get_inventory_status_report_skips_items_without_code(
    mock_reports_context,
):
    """Test that items without product code are skipped."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            days_until_stock_out=5,
            stock_on_hand=20,
            order_quantity=100,
        ),
        SkuOptimizedResultsDto(
            product_code=None,  # Missing product code
            days_until_stock_out=15,
            stock_on_hand=50,
            order_quantity=75,
        ),
    ]
    services.client.order_plan.query.return_value = forecast_items

    # Execute
    result = await _get_inventory_status_report(30, mock_reports_context)

    # Verify - should skip the item without code
    assert result["total_items"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["product_code"] == "WIDGET-001"


@pytest.mark.asyncio
async def test_get_inventory_status_report_handles_error(mock_reports_context):
    """Test that report handles API errors gracefully."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    services.client.order_plan.query.side_effect = Exception("API Error")

    # Execute
    result = await _get_inventory_status_report(30, mock_reports_context)

    # Verify - should return error structure
    assert result["report_type"] == "inventory_status"
    assert result["days_threshold"] == 30
    assert result["items"] == []
    assert result["total_items"] == 0
    assert "error" in result
    assert "API Error" in result["error"]


# ============================================================================
# Tests for Urgent Orders Report
# ============================================================================


@pytest.mark.asyncio
async def test_get_urgent_orders_report_success(mock_reports_context):
    """Test successfully retrieving urgent orders report."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_items = [
        SkuOptimizedResultsDto(
            product_code="WIDGET-001",
            days_until_stock_out=3,
            stock_on_hand=10,
            order_quantity=100,
        ),
        SkuOptimizedResultsDto(
            product_code="WIDGET-002",
            days_until_stock_out=6,
            stock_on_hand=25,
            order_quantity=75,
        ),
    ]
    services.client.order_plan.query.return_value = forecast_items

    # Execute
    result = await _get_urgent_orders_report(mock_reports_context)

    # Verify
    assert result["report_type"] == "urgent_orders"
    assert result["total_items"] == 2
    assert len(result["items"]) == 2
    assert result["items"][0]["product_code"] == "WIDGET-001"
    assert result["items"][0]["days_until_stockout"] == 3.0
    assert result["items"][1]["product_code"] == "WIDGET-002"

    # Verify it queries the order plan (filtering happens in memory)
    services.client.order_plan.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_urgent_orders_report_limits_to_30(mock_reports_context):
    """Test that urgent orders report limits to 30 items."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    forecast_items = [
        SkuOptimizedResultsDto(
            product_code=f"WIDGET-{i:03d}",
            days_until_stock_out=5,
            stock_on_hand=20,
            order_quantity=100,
        )
        for i in range(1, 51)  # 50 items
    ]
    services.client.order_plan.query.return_value = forecast_items

    # Execute
    result = await _get_urgent_orders_report(mock_reports_context)

    # Verify - should limit to 30
    assert len(result["items"]) == 30
    assert result["total_items"] == 30
    assert "Limited to 30 items" in result["note"]


@pytest.mark.asyncio
async def test_get_urgent_orders_report_handles_error(mock_reports_context):
    """Test that urgent orders report handles errors gracefully."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    services.client.order_plan.query.side_effect = Exception("Network Error")

    # Execute
    result = await _get_urgent_orders_report(mock_reports_context)

    # Verify
    assert result["report_type"] == "urgent_orders"
    assert result["items"] == []
    assert result["total_items"] == 0
    assert "error" in result
    assert "Network Error" in result["error"]


# ============================================================================
# Tests for Supplier Directory Report
# ============================================================================


@pytest.mark.asyncio
async def test_get_supplier_directory_success(mock_reports_context):
    """Test successfully retrieving supplier directory."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    suppliers = [
        SupplierResponseDto(
            supplier_code="SUP-001",
            supplier_name="Supplier One",
            email_address="orders@sup1.com",
            primary_contact_name="John Doe",
            default_lead_time=14,
        ),
        SupplierResponseDto(
            supplier_code="SUP-002",
            supplier_name="Supplier Two",
            email_address="sales@sup2.com",
            primary_contact_name="Jane Smith",
            default_lead_time=21,
        ),
    ]
    services.suppliers.list_all.return_value = suppliers

    # Execute
    result = await _get_supplier_directory_report(mock_reports_context)

    # Verify
    assert result["report_type"] == "supplier_directory"
    assert result["total_suppliers"] == 2
    assert len(result["suppliers"]) == 2

    assert result["suppliers"][0]["supplier_code"] == "SUP-001"
    assert result["suppliers"][0]["name"] == "Supplier One"
    assert result["suppliers"][0]["email"] == "orders@sup1.com"

    assert result["suppliers"][1]["supplier_code"] == "SUP-002"

    services.suppliers.list_all.assert_called_once_with(active_only=False)


@pytest.mark.asyncio
async def test_get_supplier_directory_limits_to_50(mock_reports_context):
    """Test that supplier directory limits to 50 suppliers."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    suppliers = [
        SupplierResponseDto(
            supplier_code=f"SUP-{i:03d}",
            supplier_name=f"Supplier {i}",
        )
        for i in range(1, 101)  # 100 suppliers
    ]
    services.suppliers.list_all.return_value = suppliers

    # Execute
    result = await _get_supplier_directory_report(mock_reports_context)

    # Verify - should limit to 50
    assert len(result["suppliers"]) == 50
    assert result["total_suppliers"] == 50
    assert "Limited to 50 suppliers" in result["note"]


@pytest.mark.asyncio
async def test_get_supplier_directory_handles_single_object(mock_reports_context):
    """Test directory handles single object response (not a list)."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    supplier = SupplierResponseDto(
        supplier_code="SUP-001",
        supplier_name="Supplier One",
    )
    services.suppliers.list_all.return_value = supplier

    # Execute
    result = await _get_supplier_directory_report(mock_reports_context)

    # Verify
    assert result["total_suppliers"] == 1
    assert len(result["suppliers"]) == 1
    assert result["suppliers"][0]["supplier_code"] == "SUP-001"


@pytest.mark.asyncio
async def test_get_supplier_directory_handles_error(mock_reports_context):
    """Test that supplier directory handles errors gracefully."""
    # Setup
    services = mock_reports_context.request_context.lifespan_context
    services.suppliers.list_all.side_effect = Exception("Database Error")

    # Execute
    result = await _get_supplier_directory_report(mock_reports_context)

    # Verify
    assert result["report_type"] == "supplier_directory"
    assert result["suppliers"] == []
    assert result["total_suppliers"] == 0
    assert "error" in result
    assert "Database Error" in result["error"]
