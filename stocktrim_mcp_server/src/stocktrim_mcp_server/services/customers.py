"""Customer management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import CustomersResponseDto

logger = logging.getLogger(__name__)


class CustomerService(BaseService):
    """Service for customer management operations."""

    async def get_by_code(self, code: str) -> CustomersResponseDto | None:
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

        customer = await self._client.customers.get(code)

        if not customer:
            logger.warning(f"Customer not found: {code}")
            return None

        logger.info(f"Customer retrieved: {code}")
        return customer

    async def list_all(self) -> list[CustomersResponseDto]:
        """List all customers.

        Returns:
            List of all customers

        Raises:
            Exception: If API call fails
        """
        logger.info("Listing all customers")

        customers = await self._client.customers.get_all()

        logger.info(f"Found {len(customers)} customers")
        return customers

    async def create(
        self,
        code: str,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        address: str | None = None,
    ) -> CustomersResponseDto:
        """Create a new customer.

        Args:
            code: Unique customer code
            name: Customer name
            email: Customer email (optional)
            phone: Customer phone (optional)
            address: Customer address (optional)

        Returns:
            Created customer details

        Raises:
            ValueError: If required fields are empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Customer code")
        self.validate_not_empty(name, "Customer name")

        logger.info(f"Creating customer: {code}")

        # Import CustomersRequestDto from generated models
        from stocktrim_public_api_client.generated.models import CustomersRequestDto

        # Create customer DTO
        customer_dto = CustomersRequestDto(
            code=code,
            name=name,
            email=email,
            phone=phone,
            address=address,
        )

        # Create customer
        created_customer = await self._client.customers.create(customer_dto)

        if not created_customer:
            raise Exception(f"Failed to create customer {code}")

        logger.info(f"Customer created: {code}")
        return created_customer
