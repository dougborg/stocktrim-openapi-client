"""Order plan and forecast operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.order_plan import post_api_order_plan
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria import (
    OrderPlanFilterCriteria,
)
from stocktrim_public_api_client.generated.models.order_plan_results_dto import (
    OrderPlanResultsDto,
)
from stocktrim_public_api_client.generated.models.sku_optimized_results_dto import (
    SkuOptimizedResultsDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class OrderPlan(Base):
    """Order plan and forecast management.

    Provides operations for querying forecasts and order plan recommendations
    from StockTrim's demand planning system.
    """

    async def query(
        self,
        filter_criteria: OrderPlanFilterCriteria | None = None,
    ) -> list[SkuOptimizedResultsDto]:
        """Query order plan with optional filters.

        The order plan contains forecast results with demand predictions,
        reorder recommendations, safety stock levels, and inventory analysis.

        Args:
            filter_criteria: Optional filters for the order plan query.
                Can filter by location, supplier, category, status, etc.

        Returns:
            List of SkuOptimizedResultsDto objects containing forecast data.

        Example:
            >>> # Get all order plan items
            >>> items = await client.order_plan.query()
            >>>
            >>> # Get filtered results
            >>> from stocktrim_public_api_client.generated.models import (
            ...     OrderPlanFilterCriteria,
            ... )
            >>> criteria = OrderPlanFilterCriteria(
            ...     category="Widgets",
            ...     location="WAREHOUSE-A",
            ... )
            >>> items = await client.order_plan.query(criteria)
        """
        response = await post_api_order_plan.asyncio_detailed(
            client=self._client,
            body=filter_criteria or OrderPlanFilterCriteria(),
        )
        result = unwrap(response)

        # Handle OrderPlanResultsDto wrapper
        if isinstance(result, OrderPlanResultsDto):
            return result.results or []

        # Fallback to empty list
        return []

    async def get_urgent_items(
        self,
        days_threshold: int = 30,
        location_code: str | Unset = UNSET,
        supplier_code: str | Unset = UNSET,
    ) -> list[SkuOptimizedResultsDto]:
        """Get items needing urgent reordering based on days until stockout.

        Args:
            days_threshold: Maximum days until stockout (default: 30).
                Items with fewer days remaining will be returned.
            location_code: Optional location filter.
            supplier_code: Optional supplier filter.

        Returns:
            List of SkuOptimizedResultsDto objects for items needing reorder,
            sorted by days_until_stock_out (most urgent first).

        Example:
            >>> # Get items with < 7 days stock
            >>> urgent = await client.order_plan.get_urgent_items(days_threshold=7)
            >>>
            >>> # Get urgent items at specific location
            >>> urgent = await client.order_plan.get_urgent_items(
            ...     days_threshold=14,
            ...     location_code="WAREHOUSE-A",
            ... )
        """
        # Build filter criteria
        criteria = OrderPlanFilterCriteria(
            location=location_code,
            supplier=supplier_code,
            sort_order="daysUntilStockOut",  # Sort by urgency
        )

        # Query order plan
        all_items = await self.query(criteria)

        # Filter by days threshold and sort
        urgent_items = []
        for item in all_items:
            if item.days_until_stock_out not in (None, UNSET):
                days = cast(int, item.days_until_stock_out)
                if days < days_threshold:
                    urgent_items.append(item)

        # Sort by urgency (lowest days first)
        urgent_items.sort(
            key=lambda x: cast(int, x.days_until_stock_out)
            if x.days_until_stock_out not in (None, UNSET)
            else float("inf")
        )

        return urgent_items

    async def get_by_supplier(
        self,
        supplier_code: str,
    ) -> list[SkuOptimizedResultsDto]:
        """Get order plan items for a specific supplier.

        Args:
            supplier_code: Supplier code to filter by.

        Returns:
            List of SkuOptimizedResultsDto objects for the supplier.

        Example:
            >>> items = await client.order_plan.get_by_supplier("SUP-001")
        """
        criteria = OrderPlanFilterCriteria(
            supplier=supplier_code,
        )
        return await self.query(criteria)

    async def get_by_category(
        self,
        category: str,
    ) -> list[SkuOptimizedResultsDto]:
        """Get order plan items for a product category.

        Args:
            category: Product category to filter by.

        Returns:
            List of SkuOptimizedResultsDto objects for the category.

        Example:
            >>> items = await client.order_plan.get_by_category("Widgets")
        """
        criteria = OrderPlanFilterCriteria(
            category=category,
        )
        return await self.query(criteria)
