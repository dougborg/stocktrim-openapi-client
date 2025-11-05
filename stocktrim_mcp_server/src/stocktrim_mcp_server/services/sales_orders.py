"""Sales order management service."""

from __future__ import annotations

import logging
from datetime import datetime

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import (
    SalesOrderRequestDto,
    SalesOrderResponseDto,
)

logger = logging.getLogger(__name__)


class SalesOrderService(BaseService):
    """Service for sales order management operations."""

    async def create(
        self,
        product_id: str,
        order_date: datetime,
        quantity: float,
        external_reference_id: str | None = None,
        unit_price: float | None = None,
        location_code: str | None = None,
        location_name: str | None = None,
        customer_code: str | None = None,
        customer_name: str | None = None,
    ) -> SalesOrderResponseDto:
        """Create a new sales order.

        Args:
            product_id: Product ID for the order
            order_date: Order date (ISO format)
            quantity: Quantity ordered
            external_reference_id: External reference ID (optional)
            unit_price: Unit price (optional)
            location_code: Location code (optional)
            location_name: Location name (optional)
            customer_code: Customer code (optional)
            customer_name: Customer name (optional)

        Returns:
            Created sales order details

        Raises:
            ValueError: If required fields are invalid
            Exception: If API call fails
        """
        self.validate_not_empty(product_id, "Product ID")
        self.validate_positive(quantity, "Quantity")

        logger.info(
            f"Creating sales order for product {product_id}, quantity {quantity}"
        )

        # Create sales order DTO
        order_dto = SalesOrderRequestDto(
            product_id=product_id,
            order_date=order_date,
            quantity=quantity,
            external_reference_id=external_reference_id,
            unit_price=unit_price,
            location_code=location_code,
            location_name=location_name,
            customer_code=customer_code,
            customer_name=customer_name,
        )

        # Create the sales order
        created_order = await self._client.sales_orders.create(order_dto)

        logger.info(f"Sales order created successfully for product {product_id}")
        return created_order

    async def get_all(
        self, product_id: str | None = None
    ) -> list[SalesOrderResponseDto]:
        """Get all sales orders, optionally filtered by product.

        Args:
            product_id: Optional product ID to filter by

        Returns:
            List of sales order details

        Raises:
            Exception: If API call fails
        """
        logger.info(
            "Getting sales orders"
            + (f" for product {product_id}" if product_id else "")
        )

        # Get sales orders, optionally filtered by product
        if product_id:
            orders = await self._client.sales_orders.get_for_product(product_id)
        else:
            orders = await self._client.sales_orders.get_all()

        logger.info(f"Found {len(orders)} sales orders")
        return orders

    async def get_for_product(self, product_id: str) -> list[SalesOrderResponseDto]:
        """Get all sales orders for a specific product.

        Args:
            product_id: Product ID to filter by

        Returns:
            List of sales order details

        Raises:
            ValueError: If product_id is empty
            Exception: If API call fails
        """
        self.validate_not_empty(product_id, "Product ID")
        logger.info(f"Getting sales orders for product: {product_id}")

        orders = await self._client.sales_orders.get_for_product(product_id)

        logger.info(f"Found {len(orders)} sales orders for product {product_id}")
        return orders

    async def delete_for_product(self, product_id: str) -> tuple[bool, str]:
        """Delete all sales orders for a specific product.

        Args:
            product_id: Product ID to delete orders for

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            ValueError: If product_id is empty
            Exception: If API call fails
        """
        self.validate_not_empty(product_id, "Product ID")
        logger.info(f"Deleting sales orders for product: {product_id}")

        # Check if any sales orders exist for this product
        orders = await self._client.sales_orders.get_for_product(product_id)
        if not orders:
            logger.warning(f"No sales orders found for product: {product_id}")
            return False, f"No sales orders found for product {product_id}"

        # Delete sales orders for product
        await self._client.sales_orders.delete_for_product(product_id)

        logger.info(f"Sales orders deleted for product: {product_id}")
        return True, f"Sales orders for product {product_id} deleted successfully"
