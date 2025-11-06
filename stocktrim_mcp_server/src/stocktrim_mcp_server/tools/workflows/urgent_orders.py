"""Urgent order management workflow tools for StockTrim MCP Server.

This module provides high-level workflow tools for managing urgent reorder requirements
based on forecast data and automatically generating purchase orders.
"""

from __future__ import annotations

from collections import defaultdict

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from stocktrim_mcp_server.dependencies import get_services
from stocktrim_mcp_server.logging_config import get_logger
from stocktrim_mcp_server.observability import observe_tool
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria_dto import (
    OrderPlanFilterCriteriaDto,
)

logger = get_logger(__name__)

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
        # Get services from context (note: order_plan not in service layer yet, uses client directly)
        services = get_services(context)

        # Build filter criteria for order plan query
        # Note: order_plan.get_urgent_items() doesn't support all our filters,
        # so we'll query with filters and filter by days threshold ourselves
        filter_criteria = OrderPlanFilterCriteriaDto(
            location_codes=request.location_codes or UNSET,
            supplier_codes=request.supplier_codes or UNSET,
        )

        # Query order plan (uses client directly as order_plan not in service layer)
        all_items = await services.client.order_plan.query(filter_criteria)

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
                all_products = await services.products.list_all()
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


@observe_tool
async def review_urgent_order_requirements(
    request: ReviewUrgentOrdersRequest, ctx: Context
) -> ReviewUrgentOrdersResponse:
    """Review items that need urgent reordering based on forecast data.

    This workflow tool analyzes StockTrim's forecast and order plan data to identify
    items approaching stockout. Results are grouped by supplier to facilitate
    efficient purchase order generation.

    ## How It Works

    1. Queries the order plan for items with days_until_stock_out < threshold
    2. Enriches data with supplier information from product catalog
    3. Groups items by supplier for consolidated purchasing
    4. Calculates estimated costs per supplier and overall

    ## Common Use Cases

    - **Weekly/Monthly Reorder Cycles**: Run with `days_threshold=30` to identify
      items needing reorder in the next month
    - **Urgent Restocking**: Use lower threshold (7-14 days) for critical items
    - **Supplier-Specific Review**: Filter by `supplier_codes` to review specific vendors
    - **Multi-Location Management**: Use `location_codes` to check each warehouse

    ## Typical Workflow

    1. Run `forecasts_update_and_monitor` to ensure forecasts are current
    2. Call this tool to identify urgent items grouped by supplier
    3. Review the recommendations (items, quantities, costs)
    4. Call `generate_purchase_orders_from_urgent_items` for approved suppliers
    5. Review draft POs in StockTrim UI before approving

    Args:
        request: Request with filters for urgent items
        context: Server context with StockTrimClient

    Returns:
        ReviewUrgentOrdersResponse with items grouped by supplier, including:
        - List of suppliers with urgent items
        - Items per supplier with stock levels and recommendations
        - Total estimated costs per supplier and overall

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
                    "items": [
                        {
                            "product_code": "WIDGET-001",
                            "current_stock": 45.0,
                            "days_until_stock_out": 12,
                            "recommended_order_qty": 200.0,
                            "estimated_unit_cost": 15.50
                        }
                    ],
                    "total_items": 1,
                    "total_estimated_cost": 3100.00
                }
            ],
            "total_items": 1,
            "total_estimated_cost": 3100.00
        }

    See Also:
        - Complete workflow: docs/mcp-server/examples.md#workflow-1-automated-inventory-reordering
        - `generate_purchase_orders_from_urgent_items`: Auto-generate POs from this data
        - `forecasts_update_and_monitor`: Ensure forecasts are current before using this tool
    """
    return await _review_urgent_order_requirements_impl(request, ctx)


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
        # Get services from context (note: purchase_orders_v2 not in service layer yet, uses client directly)
        services = get_services(context)

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

        # Generate POs using V2 API (uses client directly as purchase_orders_v2 not in service layer)
        # This will create draft POs based on order plan recommendations
        generated_pos = (
            await services.client.purchase_orders_v2.generate_from_order_plan(
                filter_criteria
            )
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
                status=str(po.status) if po.status not in (None, UNSET) else None,
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


@observe_tool
async def generate_purchase_orders_from_urgent_items(
    request: GeneratePurchaseOrdersRequest, ctx: Context
) -> GeneratePurchaseOrdersResponse:
    """Generate draft purchase orders for urgent items based on forecast recommendations.

    This workflow tool uses StockTrim's V2 API to automatically generate draft
    purchase orders based on order plan recommendations. The generated POs will
    be in Draft status by default and must be reviewed in StockTrim UI before approval.

    ## How It Works

    1. Queries the order plan with specified filters (location, supplier, category)
    2. Leverages StockTrim's forecast engine to calculate optimal order quantities
    3. Creates draft POs grouped by supplier
    4. Returns PO reference numbers and summary information

    ## Common Use Cases

    - **Automated Weekly Reordering**: Generate POs for all suppliers with urgent items
    - **Supplier-Specific Orders**: Filter by `supplier_codes` to create POs for specific vendors
    - **Location-Based Purchasing**: Use `location_codes` for warehouse-specific orders
    - **Post-Review Generation**: After running `review_urgent_order_requirements`, generate POs
      for approved suppliers

    ## Best Practices

    1. **Review First**: Run `review_urgent_order_requirements` first to see what will be ordered
    2. **Use Supplier Filters**: Generate POs for specific suppliers after review
    3. **Check StockTrim UI**: Always review draft POs before approving
    4. **Monitor Costs**: Review `total_estimated_cost` from review tool before generating

    ## Important Notes

    - **Draft Status**: Generated POs are in Draft status and require manual approval
    - **days_threshold Note**: While accepted for API consistency, the V2 API uses StockTrim's
      internal urgency logic. For precise control, use `review_urgent_order_requirements` first.
    - **No Undo**: Once created, POs must be deleted manually if incorrect. Review carefully!

    Args:
        request: Request with filters for PO generation
        context: Server context with StockTrimClient

    Returns:
        GeneratePurchaseOrdersResponse with created PO details, including:
        - List of generated POs with reference numbers
        - Supplier information per PO
        - Item counts per PO
        - Total PO count

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
                },
                {
                    "reference_number": "PO-2024-002",
                    "supplier_code": "SUP-002",
                    "supplier_name": "Global Parts",
                    "item_count": 3,
                    "status": "Draft"
                }
            ],
            "total_count": 2
        }

    See Also:
        - Complete workflow: docs/mcp-server/examples.md#workflow-1-automated-inventory-reordering
        - `review_urgent_order_requirements`: Review items before generating POs
        - `forecasts_update_and_monitor`: Ensure forecasts are current
    """
    return await _generate_purchase_orders_from_urgent_items_impl(request, ctx)


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
