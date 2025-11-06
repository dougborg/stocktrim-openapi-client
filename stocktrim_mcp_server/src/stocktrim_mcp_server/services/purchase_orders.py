"""Purchase Order management service."""

from __future__ import annotations

import logging
from datetime import datetime

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models import (
    PurchaseOrderLineItem,
    PurchaseOrderLocation,
    PurchaseOrderRequestDto,
    PurchaseOrderResponseDto,
    PurchaseOrderStatusDto,
    PurchaseOrderSupplier,
)

logger = logging.getLogger(__name__)


class PurchaseOrderService(BaseService):
    """Service for purchase order management operations."""

    async def get_by_reference(
        self, reference_number: str
    ) -> PurchaseOrderResponseDto | None:
        """Get a purchase order by reference number.

        Args:
            reference_number: Purchase order reference number

        Returns:
            Purchase order details if found, None otherwise

        Raises:
            ValueError: If reference number is empty
            Exception: If API call fails
        """
        self.validate_not_empty(reference_number, "Reference number")
        logger.info(f"Getting purchase order: {reference_number}")

        po = await self._client.purchase_orders.find_by_reference(reference_number)

        if not po:
            logger.warning(f"Purchase order not found: {reference_number}")
            return None

        logger.info(f"Purchase order retrieved: {reference_number}")
        return po

    async def list_all(self) -> list[PurchaseOrderResponseDto]:
        """List all purchase orders.

        Returns:
            List of purchase orders

        Raises:
            Exception: If API call fails
        """
        logger.info("Listing all purchase orders")

        result = await self._client.purchase_orders.get_all()

        # Handle API inconsistency - could return single object or list
        if isinstance(result, list):
            pos = result
        else:
            pos = [result] if result else []

        logger.info(f"Found {len(pos)} purchase orders")
        return pos

    async def create(
        self,
        supplier_code: str,
        line_items: list[dict],
        supplier_name: str | None = None,
        order_date: datetime | None = None,
        location_code: str | None = None,
        location_name: str | None = None,
        reference_number: str | None = None,
        client_reference_number: str | None = None,
        status: str | None = "Draft",
    ) -> PurchaseOrderResponseDto:
        """Create a new purchase order.

        Args:
            supplier_code: Supplier code (required)
            line_items: List of line items, each with product_code, quantity, and optional unit_price
            supplier_name: Supplier name (optional)
            order_date: Order date (defaults to now if not provided)
            location_code: Location code (optional)
            location_name: Location name (optional)
            reference_number: Custom reference number (optional)
            client_reference_number: Client reference number (optional)
            status: Purchase order status (Draft, Approved, Sent, Received) - defaults to Draft

        Returns:
            Created purchase order details

        Raises:
            ValueError: If required fields are empty or invalid
            Exception: If API call fails
        """
        self.validate_not_empty(supplier_code, "Supplier code")

        if not line_items:
            raise ValueError("At least one line item is required")

        logger.info(f"Creating purchase order for supplier: {supplier_code}")

        # Default to now if not provided
        if order_date is None:
            order_date = datetime.now()

        # Build supplier object
        supplier = PurchaseOrderSupplier(
            supplier_code=supplier_code,
            supplier_name=supplier_name,
        )

        # Build location object (optional)
        location = None
        if location_code or location_name:
            location = PurchaseOrderLocation(
                location_code=location_code,
                location_name=location_name,
            )

        # Build line items
        po_line_items = []
        for item in line_items:
            if "product_code" not in item or "quantity" not in item:
                raise ValueError(
                    "Each line item must have product_code and quantity fields"
                )

            if item["quantity"] <= 0:
                raise ValueError("Line item quantity must be greater than 0")

            po_line_items.append(
                PurchaseOrderLineItem(
                    product_id=item["product_code"],
                    quantity=item["quantity"],
                    unit_price=item.get("unit_price"),
                )
            )

        # Parse status
        # Note: PurchaseOrderStatusDto is a string enum with values:
        #   DRAFT="Draft", APPROVED="Approved", SENT="Sent", RECEIVED="Received"
        # The enum can be matched by attribute name (DRAFT, APPROVED, etc.)
        # and the value is the title-case string ("Draft", "Approved", etc.).
        po_status = None
        if status:
            try:
                # Try to match by name (case-insensitive)
                status_upper = status.upper()
                if hasattr(PurchaseOrderStatusDto, status_upper):
                    po_status = getattr(PurchaseOrderStatusDto, status_upper)
                else:
                    # Invalid status provided, default to Draft
                    logger.warning(
                        f"Invalid status '{status}' provided, defaulting to Draft"
                    )
                    po_status = PurchaseOrderStatusDto.DRAFT
            except (ValueError, AttributeError):
                logger.warning(
                    f"Invalid status '{status}' provided, defaulting to Draft"
                )
                po_status = PurchaseOrderStatusDto.DRAFT

        # Build purchase order DTO
        po_dto = PurchaseOrderRequestDto(
            order_date=order_date,
            supplier=supplier,
            purchase_order_line_items=po_line_items,
            reference_number=reference_number,
            client_reference_number=client_reference_number,
            location=location if location else UNSET,
            status=po_status if po_status else UNSET,
        )

        # Create purchase order
        created_po = await self._client.purchase_orders.create(po_dto)

        if not created_po:
            raise Exception(
                f"Failed to create purchase order for supplier {supplier_code}"
            )

        logger.info(f"Purchase order created: {created_po.reference_number}")
        return created_po

    async def delete(self, reference_number: str) -> tuple[bool, str]:
        """Delete a purchase order by reference number.

        Args:
            reference_number: Reference number to delete

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            ValueError: If reference number is empty
            Exception: If API call fails
        """
        self.validate_not_empty(reference_number, "Reference number")
        logger.info(f"Deleting purchase order: {reference_number}")

        # Check if PO exists first
        po = await self._client.purchase_orders.find_by_reference(reference_number)
        if not po:
            return False, f"Purchase order {reference_number} not found"

        # Delete PO
        await self._client.purchase_orders.delete(reference_number=reference_number)

        logger.info(f"Purchase order deleted: {reference_number}")
        return True, f"Purchase order {reference_number} deleted successfully"
