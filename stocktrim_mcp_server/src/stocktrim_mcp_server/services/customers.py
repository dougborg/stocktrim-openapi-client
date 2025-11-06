"""Customer management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import CustomerDto
from stocktrim_public_api_client.utils import NotFoundError

logger = logging.getLogger(__name__)


class CustomerService(BaseService):
    """Service for customer management operations."""

    async def get_by_code(self, code: str) -> CustomerDto | None:
        """Get a single customer by code.

        Args:
            code: Customer code

        Returns:
            Customer details if found, None otherwise

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Customer code")
        logger.info(f"Getting customer: {code}")

        try:
            customer = await self._client.customers.get(code)

            if not customer:
                logger.warning(f"Customer not found: {code}")
                return None

            logger.info(f"Customer retrieved: {code}")
            return customer
        except NotFoundError:
            logger.warning(f"Customer not found: {code}")
            return None

    async def list_all(self, limit: int | None = None) -> list[CustomerDto]:
        """List all customers.

        Args:
            limit: Maximum number of customers to return (optional)

        Returns:
            List of customers

        Raises:
            Exception: If API call fails
        """
        logger.info(f"Listing customers (limit: {limit or 'unlimited'})")

        customers = await self._client.customers.get_all()

        # Apply limit if specified
        if limit is not None:
            customers = customers[:limit]

        logger.info(f"Found {len(customers)} customers")
        return customers
