"""Urgent order management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for managing urgent reorder requirements
based on forecast data and automatically generating purchase orders.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria_dto import (
    OrderPlanFilterCriteriaDto,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: review_urgent_order_requirements
# ============================================================================


class ReviewUrgentOrdersRequest(BaseModel):
    """Request for reviewing urgent order requirements."""

    days_threshold: int = Field(
        default=30, description="Days until stockout threshold (default: 30)"
    )
    location_codes: list[str] | None = Field(
        default=None, description="Filter by specific locations"
    )
    category: str | None = Field(default=None, description="Filter by product category")
    supplier_codes: list[str] | None = Field(
        default=None, description="Filter by specific suppliers"
    )


class UrgentItemInfo(BaseModel):
    """Information about an urgent item needing reorder."""

    product_code: str | None = Field(description="Product code")
    description: str | None = Field(description="Product description/name")
    current_stock: float | None = Field(description="Current stock on hand")
    days_until_stock_out: int | None = Field(description="Days until stock out")
    recommended_order_qty: float | None = Field(
        description="Recommended order quantity"
    )
    supplier_code: str | None = Field(description="Primary supplier code")
    estimated_unit_cost: float | None = Field(description="Estimated unit cost")
    location_name: str | None = Field(description="Location name")


class SupplierGroupInfo(BaseModel):
    """Urgent items grouped by supplier."""

    supplier_code: str = Field(description="Supplier code")
    items: list[UrgentItemInfo] = Field(description="List of urgent items")
    total_items: int = Field(description="Total number of items")
    total_estimated_cost: float | None = Field(description="Total estimated cost")


class ReviewUrgentOrdersResponse(BaseModel):
    """Response with urgent order requirements grouped by supplier."""

    suppliers: list[SupplierGroupInfo] = Field(
        description="Urgent items grouped by supplier"
    )
    total_items: int = Field(
        description="Total number of urgent items across all suppliers"
    )
    total_estimated_cost: float | None = Field(
        description="Total estimated cost across all suppliers"
    )


async def _review_urgent_order_requirements_impl(
    request: ReviewUrgentOrdersRequest, context: Context
) -> ReviewUrgentOrdersResponse:
    """Implementation of review_urgent_order_requirements tool.

    Args:
        request: Request with filters for urgent items
        context: Server context with StockTrimClient

    Returns:
        ReviewUrgentOrdersResponse with items grouped by supplier

    Raises:
        Exception: If API call fails
    """
    logger.info(
        f"Reviewing urgent order requirements with threshold: {request.days_threshold} days"
    )

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Build filter criteria for order plan query
        # Note: order_plan.get_urgent_items() doesn't support all our filters,
        # so we'll query with filters and filter by days threshold ourselves
        filter_criteria = OrderPlanFilterCriteriaDto(
            location_codes=request.location_codes or UNSET,
            supplier_codes=request.supplier_codes or UNSET,
        )

        # Query order plan
        all_items = await client.order_plan.query(filter_criteria)

        # Filter items by days threshold
        urgent_items = []
        for item in all_items:
            if (
                item.days_until_stock_out not in (None, UNSET)
                and item.days_until_stock_out < request.days_threshold
            ):
                urgent_items.append(item)

        # Sort by urgency (lowest days first)
        urgent_items.sort(
            key=lambda x: (
                x.days_until_stock_out
                if x.days_until_stock_out not in (None, UNSET)
                else float("inf")
            )
        )

        # Group by supplier
        # Note: SkuOptimizedResultsDto doesn't have supplier info directly,
        # we need to get product details to find the supplier.
        # We batch fetch products to avoid N+1 queries. This is more efficient
        # than individual lookups but could be expensive for large catalogs.
        # Only fetch if we have urgent items to process.
        supplier_groups: dict[str, list[UrgentItemInfo]] = defaultdict(list)

        if not urgent_items:
            # No urgent items, return empty response early
            return ReviewUrgentOrdersResponse(
                suppliers=[],
                total_items=0,
                total_estimated_cost=None,
            )

        # Batch fetch product details for all urgent items
        product_codes = [
            item.product_code
            for item in urgent_items
            if item.product_code not in (None, UNSET)
        ]

        # Create a mapping of product_code -> supplier_code
        product_to_supplier = {}
        if product_codes:
            try:
                # Get all products to build supplier mapping
                # Note: This fetches the entire product catalog which could be expensive
                # for large inventories. StockTrim API doesn't provide a batch lookup
                # method, so this is more efficient than N individual API calls.
                all_products = await client.products.get_all()
                for product in all_products:
                    if product.product_code_readable and product.supplier_code not in (
                        None,
                        UNSET,
                    ):
                        product_to_supplier[product.product_code_readable] = (
                            product.supplier_code or "UNKNOWN"
                        )
            except Exception as e:
                logger.warning(
                    f"Could not batch fetch products for supplier mapping: {e}"
                )
                # Continue without supplier mapping - will use "UNKNOWN"

        for item in urgent_items:
            # Get supplier from pre-fetched mapping
            product_code = (
                item.product_code if item.product_code not in (None, UNSET) else None
            )
            supplier_code = (
                product_to_supplier.get(product_code, "UNKNOWN")
                if product_code
                else "UNKNOWN"
            )

            # Create UrgentItemInfo
            urgent_item_info = UrgentItemInfo(
                product_code=item.product_code
                if item.product_code not in (None, UNSET)
                else None,
                description=item.name if item.name not in (None, UNSET) else None,
                current_stock=item.stock_on_hand
                if item.stock_on_hand not in (None, UNSET)
                else None,
                days_until_stock_out=item.days_until_stock_out
                if item.days_until_stock_out not in (None, UNSET)
                else None,
                recommended_order_qty=item.order_quantity
                if item.order_quantity not in (None, UNSET)
                else None,
                supplier_code=supplier_code,
                estimated_unit_cost=item.sku_cost
                if item.sku_cost not in (None, UNSET)
                else None,
                location_name=item.location_name
                if item.location_name not in (None, UNSET)
                else None,
            )

            supplier_groups[supplier_code].append(urgent_item_info)

        # Build response with supplier groups
        supplier_group_infos = []
        total_cost = 0.0
        has_cost_data = False

        for supplier_code, items in supplier_groups.items():
            # Calculate total cost for this supplier
            supplier_cost = 0.0
            supplier_has_cost = False
            for item in items:
                if (
                    item.estimated_unit_cost is not None
                    and item.recommended_order_qty is not None
                ):
                    supplier_cost += (
                        item.estimated_unit_cost * item.recommended_order_qty
                    )
                    supplier_has_cost = True
                    has_cost_data = True

            supplier_group_infos.append(
                SupplierGroupInfo(
                    supplier_code=supplier_code,
                    items=items,
                    total_items=len(items),
                    total_estimated_cost=supplier_cost if supplier_has_cost else None,
                )
            )

            if supplier_has_cost:
                total_cost += supplier_cost

        # Sort supplier groups by total items (descending)
        supplier_group_infos.sort(key=lambda x: x.total_items, reverse=True)

        response = ReviewUrgentOrdersResponse(
            suppliers=supplier_group_infos,
            total_items=len(urgent_items),
            total_estimated_cost=total_cost if has_cost_data else None,
        )

        logger.info(
            f"Found {response.total_items} urgent items across {len(supplier_group_infos)} suppliers"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to review urgent order requirements: {e}")
        raise


async def review_urgent_order_requirements(
    request: ReviewUrgentOrdersRequest, context: Context
) -> ReviewUrgentOrdersResponse:
    """Review items that need urgent reordering based on forecast data.

    This workflow tool analyzes StockTrim's forecast and order plan data to identify
    items approaching stockout. Results are grouped by supplier to facilitate
    purchase order generation.

    The tool queries the order plan for items with days_until_stock_out below the
    specified threshold and enriches the data with supplier information.

    Args:
        request: Request with filters for urgent items
        context: Server context with StockTrimClient

    Returns:
        ReviewUrgentOrdersResponse with items grouped by supplier

    Example:
        Request: {
            "days_threshold": 30,
            "location_codes": ["WAREHOUSE-A"],
            "supplier_codes": ["SUP-001"]
        }
        Returns: {
            "suppliers": [
                {
                    "supplier_code": "SUP-001",
                    "items": [...],
                    "total_items": 5,
                    "total_estimated_cost": 1250.00
                }
            ],
            "total_items": 5,
            "total_estimated_cost": 1250.00
        }
    """
    return await _review_urgent_order_requirements_impl(request, context)


# ============================================================================
# Tool 2: generate_purchase_orders_from_urgent_items
# ============================================================================


class GeneratePurchaseOrdersRequest(BaseModel):
    """Request for generating purchase orders from urgent items.

    Note: The days_threshold parameter is included for API consistency with
    review_urgent_order_requirements, but the V2 API's generate_from_order_plan
    uses StockTrim's internal urgency logic and doesn't directly filter by this value.
    For precise control over which items are included based on days_until_stock_out,
    use review_urgent_order_requirements first, then manually create POs for selected items.
    """

    days_threshold: int = Field(
        default=30,
        description="Days until stockout threshold (for API consistency; not used in V2 API filtering)",
    )
    location_codes: list[str] | None = Field(
        default=None, description="Filter by specific locations"
    )
    supplier_codes: list[str] | None = Field(
        default=None, description="Only generate POs for specific suppliers"
    )
    category: str | None = Field(default=None, description="Filter by product category")


class GeneratedPurchaseOrderInfo(BaseModel):
    """Information about a generated purchase order."""

    reference_number: str | None = Field(description="PO reference number")
    supplier_code: str | None = Field(description="Supplier code")
    supplier_name: str | None = Field(description="Supplier name")
    item_count: int = Field(description="Number of line items")
    status: str | None = Field(description="PO status (typically 'Draft')")


class GeneratePurchaseOrdersResponse(BaseModel):
    """Response with generated purchase order details."""

    purchase_orders: list[GeneratedPurchaseOrderInfo] = Field(
        description="List of generated purchase orders"
    )
    total_count: int = Field(description="Total number of POs generated")


async def _generate_purchase_orders_from_urgent_items_impl(
    request: GeneratePurchaseOrdersRequest, context: Context
) -> GeneratePurchaseOrdersResponse:
    """Implementation of generate_purchase_orders_from_urgent_items tool.

    Args:
        request: Request with filters for PO generation
        context: Server context with StockTrimClient

    Returns:
        GeneratePurchaseOrdersResponse with created PO details

    Raises:
        Exception: If API call fails
    """
    logger.info(
        f"Generating purchase orders for urgent items with threshold: {request.days_threshold} days"
    )

    try:
        # Access StockTrimClient from lifespan context
        server_context = context.request_context.lifespan_context
        client = server_context.client

        # Build filter criteria for V2 API's generate_from_order_plan
        # Note: The V2 API generates POs based on the order plan's recommendations,
        # which already incorporate urgency and reorder logic. The days_threshold
        # parameter is provided for API consistency with review_urgent_order_requirements,
        # but the actual urgency filtering happens within StockTrim's forecast engine.
        # If more granular control is needed, use review_urgent_order_requirements first
        # to identify specific items, then manually create POs for selected suppliers.
        filter_criteria = OrderPlanFilterCriteriaDto(
            location_codes=request.location_codes or UNSET,
            supplier_codes=request.supplier_codes or UNSET,
        )

        # Generate POs using V2 API
        # This will create draft POs based on order plan recommendations
        generated_pos = await client.purchase_orders_v2.generate_from_order_plan(
            filter_criteria
        )

        # Build response with PO details
        po_infos = []
        for po in generated_pos:
            po_info = GeneratedPurchaseOrderInfo(
                reference_number=po.reference_number
                if po.reference_number not in (None, UNSET)
                else None,
                supplier_code=po.supplier.supplier_code
                if po.supplier and po.supplier.supplier_code not in (None, UNSET)
                else None,
                supplier_name=po.supplier.supplier_name
                if po.supplier and po.supplier.supplier_name not in (None, UNSET)
                else None,
                item_count=len(po.purchase_order_line_items)
                if po.purchase_order_line_items
                else 0,
                status=str(po.status.value) if po.status not in (None, UNSET) else None,
            )
            po_infos.append(po_info)

        response = GeneratePurchaseOrdersResponse(
            purchase_orders=po_infos,
            total_count=len(po_infos),
        )

        logger.info(f"Generated {response.total_count} purchase orders")
        return response

    except Exception as e:
        logger.error(f"Failed to generate purchase orders from urgent items: {e}")
        raise


async def generate_purchase_orders_from_urgent_items(
    request: GeneratePurchaseOrdersRequest, context: Context
) -> GeneratePurchaseOrdersResponse:
    """Generate draft purchase orders for urgent items based on forecast recommendations.

    This workflow tool uses StockTrim's V2 API to automatically generate draft
    purchase orders based on order plan recommendations. The generated POs will
    be in Draft status by default and can be reviewed before approval.

    This is a powerful feature that leverages StockTrim's forecast engine to
    automatically create purchase orders with appropriate quantities for items
    needing reorder.

    Note on days_threshold: While this parameter is accepted for API consistency
    with review_urgent_order_requirements, the V2 API's generate_from_order_plan
    endpoint uses StockTrim's internal urgency logic. For more control over which
    items are included based on days_until_stock_out, use review_urgent_order_requirements
    first to analyze items, then generate POs for specific suppliers.

    Args:
        request: Request with filters for PO generation
        context: Server context with StockTrimClient

    Returns:
        GeneratePurchaseOrdersResponse with created PO details

    Example:
        Request: {
            "days_threshold": 14,
            "supplier_codes": ["SUP-001", "SUP-002"],
            "location_codes": ["WAREHOUSE-A"]
        }
        Returns: {
            "purchase_orders": [
                {
                    "reference_number": "PO-2024-001",
                    "supplier_code": "SUP-001",
                    "supplier_name": "Acme Supplies",
                    "item_count": 5,
                    "status": "Draft"
                }
            ],
            "total_count": 1
        }
    """
    return await _generate_purchase_orders_from_urgent_items_impl(request, context)


# ============================================================================
# Tool Registration
# ============================================================================


def register_tools(mcp: FastMCP) -> None:
    """Register urgent order workflow tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
    """
    mcp.tool()(review_urgent_order_requirements)
    mcp.tool()(generate_purchase_orders_from_urgent_items)
