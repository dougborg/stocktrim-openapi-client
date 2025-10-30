"""Purchase Orders V2 API operations.

This helper provides access to the V2 Purchase Orders API, which is recommended
over V1 for its consistent return types, pagination support, and the critical
generate_from_order_plan feature.
"""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.purchase_orders_v2 import (
    get_api_v2_purchase_orders,
    get_api_v2_purchase_orders_reference_number,
    post_api_v2_purchase_orders_order_plan,
)
from stocktrim_public_api_client.generated.models.order_plan_filter_criteria_dto import (
    OrderPlanFilterCriteriaDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_response_dto import (
    PurchaseOrderResponseDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_status_dto import (
    PurchaseOrderStatusDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class PurchaseOrdersV2(Base):
    """Purchase Orders V2 API (recommended over V1).

    Provides operations for managing purchase orders using the V2 API endpoints.
    Key features:
    - Consistent return types (always returns arrays from list operations)
    - Pagination support
    - Generate POs from order plan recommendations (critical feature!)
    """

    async def generate_from_order_plan(
        self,
        filter_criteria: OrderPlanFilterCriteriaDto,
    ) -> list[PurchaseOrderResponseDto]:
        """Generate purchase orders from order plan recommendations.

        This is a KEY FEATURE that automatically generates draft purchase orders
        based on StockTrim's forecast analysis and reorder recommendations.

        The generated POs will be in Draft status by default and can be reviewed
        before approval and sending to suppliers.

        Args:
            filter_criteria: Filters to apply when generating POs.
                Can filter by supplier, location, category, status, etc.

        Returns:
            List of generated PurchaseOrderResponseDto objects.
            Each PO contains line items with quantities based on forecast
            recommendations.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     OrderPlanFilterCriteriaDto,
            ... )
            >>>
            >>> # Generate POs for specific suppliers
            >>> criteria = OrderPlanFilterCriteriaDto(
            ...     supplier_codes=["SUP-001", "SUP-002"],
            ...     location_codes=["WAREHOUSE-A"],
            ... )
            >>> pos = await client.purchase_orders_v2.generate_from_order_plan(criteria)
            >>>
            >>> for po in pos:
            ...     print(f"PO {po.reference_number} for {po.supplier.supplier_name}")
            ...     print(f"Status: {po.status}, Total: ${po.total_cost}")
        """
        response = await post_api_v2_purchase_orders_order_plan.asyncio_detailed(
            client=self._client,
            body=filter_criteria,
        )
        result = unwrap(response)
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def get_all_paginated(
        self,
        page: int = 0,
        page_size: int = 10,
        status: PurchaseOrderStatusDto | Unset = UNSET,
    ) -> list[PurchaseOrderResponseDto]:
        """Get all purchase orders with pagination.

        Args:
            page: Page number (default: 0).
            page_size: Items per page (default: 10).
            status: Optional status filter (Draft, Approved, Sent, Received).

        Returns:
            List of PurchaseOrderResponseDto objects for the requested page.

        Example:
            >>> # Get first page
            >>> pos = await client.purchase_orders_v2.get_all_paginated(
            ...     page=0,
            ...     page_size=20,
            ... )
            >>>
            >>> # Get only approved POs
            >>> from stocktrim_public_api_client.generated.models import (
            ...     PurchaseOrderStatusDto,
            ... )
            >>> pos = await client.purchase_orders_v2.get_all_paginated(
            ...     status=PurchaseOrderStatusDto.APPROVED,
            ... )
        """
        response = await get_api_v2_purchase_orders.asyncio_detailed(
            client=self._client,
            page=page,
            page_size=page_size,
            status=status,
        )
        result = unwrap(response)
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def get_by_reference(
        self,
        reference_number: str,
    ) -> PurchaseOrderResponseDto | None:
        """Get a purchase order by reference number.

        Args:
            reference_number: The PO reference number to retrieve.

        Returns:
            PurchaseOrderResponseDto if found, None otherwise.

        Example:
            >>> po = await client.purchase_orders_v2.get_by_reference("PO-2024-001")
            >>> if po:
            ...     print(f"Supplier: {po.supplier.supplier_name}")
            ...     print(f"Total: ${po.total_cost}")
        """
        try:
            response = (
                await get_api_v2_purchase_orders_reference_number.asyncio_detailed(
                    client=self._client,
                    reference_number=reference_number,
                )
            )
            return cast(PurchaseOrderResponseDto, unwrap(response))
        except Exception:
            # Return None if not found
            return None

    async def find_by_supplier(
        self,
        supplier_code: str,
        status: PurchaseOrderStatusDto | Unset = UNSET,
    ) -> list[PurchaseOrderResponseDto]:
        """Get all purchase orders for a specific supplier.

        Warning: This method fetches all pages and filters client-side, which can
        be inefficient for suppliers with many purchase orders. For large datasets
        (thousands of POs), this could result in fetching and filtering many pages
        of data. The API's V2 endpoint does NOT support server-side filtering by
        supplier, so all purchase orders must be fetched and filtered locally. This
        can be extremely inefficient if you have a large number of purchase orders.
        Consider using get_all_paginated() directly with manual pagination if you
        need more control over the number of records fetched.

        Args:
            supplier_code: Supplier code to filter by.
            status: Optional status filter.

        Returns:
            List of PurchaseOrderResponseDto objects for the supplier.

        Example:
            >>> pos = await client.purchase_orders_v2.find_by_supplier("SUP-001")
            >>> for po in pos:
            ...     print(f"PO {po.reference_number}: {po.status}")
        """
        all_pos: list[PurchaseOrderResponseDto] = []
        page = 0
        page_size = 50

        while True:
            pos = await self.get_all_paginated(
                page=page,
                page_size=page_size,
                status=status,
            )

            if not pos:
                break

            # Filter by supplier code
            supplier_pos = [
                po
                for po in pos
                if po.supplier and po.supplier.supplier_code == supplier_code
            ]
            all_pos.extend(supplier_pos)

            # Check if we got less than page_size (last page)
            if len(pos) < page_size:
                break

            page += 1

        return all_pos
