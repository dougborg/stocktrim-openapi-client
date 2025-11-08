"""Report resources for StockTrim MCP Server.

Provides aggregated data resources like inventory status, urgent orders,
and supplier directories. These resources compute data from multiple sources
to provide business intelligence context.
"""

from fastmcp import Context, FastMCP

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_public_api_client.client_types import UNSET

logger = get_logger(__name__)


# ============================================================================
# Inventory Status Report
# ============================================================================


async def _get_inventory_status_report(days_threshold: int, context: Context) -> dict:
    """Get inventory status report showing items approaching stockout.

    Args:
        days_threshold: Days until stockout threshold
        context: Request context with services

    Returns:
        Inventory status report as dictionary
    """
    services = get_services(context)

    try:
        # Get all forecast data
        # Note: The API doesn't support filtering by days_threshold directly,
        # so we query all items and filter in memory
        all_items = await services.client.order_plan.query()

        # Handle both list and single object responses
        if not isinstance(all_items, list):
            all_items = [all_items] if all_items else []

        # Filter by days threshold
        forecast_items = []
        for item in all_items:
            days_until = (
                item.days_until_stock_out
                if item.days_until_stock_out not in (None, UNSET)
                else None
            )
            if days_until is not None and days_until < days_threshold:
                forecast_items.append(item)

        # Build report (limit to 50 for token budget)
        low_stock_items = []
        for item in forecast_items[:50]:
            product_code = (
                item.product_code if item.product_code not in (None, UNSET) else None
            )
            if not product_code:
                continue

            days_until = (
                float(item.days_until_stock_out)
                if item.days_until_stock_out not in (None, UNSET)
                else None
            )
            current_stock = (
                float(item.stock_on_hand)
                if item.stock_on_hand not in (None, UNSET)
                else 0
            )
            recommended_order = (
                float(item.order_quantity)
                if item.order_quantity not in (None, UNSET)
                else 0
            )

            low_stock_items.append(
                {
                    "product_code": product_code,
                    "days_until_stockout": days_until,
                    "current_stock": current_stock,
                    "recommended_order_quantity": recommended_order,
                    "urgency": "high" if days_until and days_until < 7 else "medium",
                }
            )

        return {
            "report_type": "inventory_status",
            "days_threshold": days_threshold,
            "items": low_stock_items,
            "total_items": len(low_stock_items),
            "note": f"Items approaching stockout within {days_threshold} days. Limited to 50 items.",
        }

    except Exception as e:
        logger.error(f"Error generating inventory status report: {e}")
        return {
            "report_type": "inventory_status",
            "days_threshold": days_threshold,
            "items": [],
            "total_items": 0,
            "error": str(e),
        }


# ============================================================================
# Urgent Orders Report
# ============================================================================


async def _get_urgent_orders_report(context: Context) -> dict:
    """Get urgent orders report showing items needing immediate reorder (< 7 days).

    Args:
        context: Request context with services

    Returns:
        Urgent orders report as dictionary
    """
    services = get_services(context)

    try:
        # Get all items and filter for < 7 days until stockout
        # Note: The API doesn't support filtering by days_threshold directly,
        # so we query all items and filter in memory
        all_items = await services.client.order_plan.query()

        # Handle both list and single object responses
        if not isinstance(all_items, list):
            all_items = [all_items] if all_items else []

        # Filter for urgent items (< 7 days)
        forecast_items = []
        for item in all_items:
            days_until = (
                item.days_until_stock_out
                if item.days_until_stock_out not in (None, UNSET)
                else None
            )
            if days_until is not None and days_until < 7:
                forecast_items.append(item)

        # Build report (limit to 30 most urgent)
        urgent_items = []
        for item in forecast_items[:30]:
            product_code = (
                item.product_code if item.product_code not in (None, UNSET) else None
            )
            if not product_code:
                continue

            days_until = (
                float(item.days_until_stock_out)
                if item.days_until_stock_out not in (None, UNSET)
                else None
            )
            current_stock = (
                float(item.stock_on_hand)
                if item.stock_on_hand not in (None, UNSET)
                else 0
            )
            recommended_order = (
                float(item.order_quantity)
                if item.order_quantity not in (None, UNSET)
                else 0
            )

            urgent_items.append(
                {
                    "product_code": product_code,
                    "days_until_stockout": days_until,
                    "current_stock": current_stock,
                    "recommended_order_quantity": recommended_order,
                }
            )

        return {
            "report_type": "urgent_orders",
            "items": urgent_items,
            "total_items": len(urgent_items),
            "note": "Items needing reorder within 7 days. Limited to 30 items.",
        }

    except Exception as e:
        logger.error(f"Error generating urgent orders report: {e}")
        return {
            "report_type": "urgent_orders",
            "items": [],
            "total_items": 0,
            "error": str(e),
        }


# ============================================================================
# Supplier Directory Report
# ============================================================================


async def _get_supplier_directory_report(context: Context) -> dict:
    """Get supplier directory with all active suppliers.

    Args:
        context: Request context with services

    Returns:
        Supplier directory as dictionary
    """
    services = get_services(context)

    try:
        # Get all suppliers
        suppliers = await services.suppliers.list_all(active_only=False)

        # Handle both list and single object responses
        if not isinstance(suppliers, list):
            suppliers = [suppliers] if suppliers else []

        # Build directory
        supplier_list = []
        for supplier in suppliers[:50]:  # Limit to 50 for token budget
            supplier_list.append(
                {
                    "supplier_code": supplier.supplier_code
                    if supplier.supplier_code not in (None, UNSET)
                    else None,
                    "name": supplier.supplier_name
                    if supplier.supplier_name not in (None, UNSET)
                    else None,
                    "email": supplier.email_address
                    if supplier.email_address not in (None, UNSET)
                    else None,
                    "primary_contact": supplier.primary_contact_name
                    if supplier.primary_contact_name not in (None, UNSET)
                    else None,
                    "default_lead_time": supplier.default_lead_time
                    if supplier.default_lead_time not in (None, UNSET)
                    else None,
                }
            )

        return {
            "report_type": "supplier_directory",
            "suppliers": supplier_list,
            "total_suppliers": len(supplier_list),
            "note": "All suppliers. Limited to 50 suppliers.",
        }

    except Exception as e:
        logger.error(f"Error generating supplier directory: {e}")
        return {
            "report_type": "supplier_directory",
            "suppliers": [],
            "total_suppliers": 0,
            "error": str(e),
        }


# ============================================================================
# Resource Registration
# ============================================================================


def register_report_resources(mcp: FastMCP) -> None:
    """Register report resources with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.resource(
        uri="stocktrim://reports/inventory-status{?days_threshold}",
        name="Inventory Status Report",
        description="Get items approaching stockout within specified days",
        mime_type="application/json",
    )
    async def get_inventory_status_report(
        context: Context, days_threshold: int = 30
    ) -> dict:
        """Get inventory status report."""
        return await _get_inventory_status_report(days_threshold, context)

    @mcp.resource(
        uri="stocktrim://reports/urgent-orders",
        name="Urgent Orders Report",
        description="Get items needing immediate reorder (< 7 days until stockout)",
        mime_type="application/json",
    )
    async def get_urgent_orders_report(context: Context) -> dict:
        """Get urgent orders report."""
        return await _get_urgent_orders_report(context)

    @mcp.resource(
        uri="stocktrim://reports/supplier-directory",
        name="Supplier Directory",
        description="Get directory of all suppliers with contact information",
        mime_type="application/json",
    )
    async def get_supplier_directory_report(context: Context) -> dict:
        """Get supplier directory report."""
        return await _get_supplier_directory_report(context)
