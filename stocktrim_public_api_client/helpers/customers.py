"""Customer management operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.generated.api.customers import (
    get_api_customers,
    get_api_customers_code,
    put_api_customers,
)
from stocktrim_public_api_client.generated.models.customer import Customer
from stocktrim_public_api_client.generated.models.customer_dto import CustomerDto
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Customers(Base):
    """Customer management.

    Provides operations for managing customers in StockTrim.
    """

    async def get_all(self) -> list[CustomerDto]:
        """Get all customers.

        Returns:
            List of CustomerDto objects.

        Example:
            >>> customers = await client.customers.get_all()
        """
        response = await get_api_customers.asyncio_detailed(client=self._client)
        result = unwrap(response)
        return result if isinstance(result, list) else []

    async def get(self, code: str) -> CustomerDto:
        """Get a specific customer by code.

        Args:
            code: The customer code.

        Returns:
            CustomerDto object.

        Example:
            >>> customer = await client.customers.get("CUST-001")
        """
        response = await get_api_customers_code.asyncio_detailed(
            client=self._client,
            code=code,
        )
        return cast(CustomerDto, unwrap(response))

    async def update(self, customer: CustomerDto) -> list[Customer]:
        """Update a customer (create or update based on code).

        Args:
            customer: Customer data to update.

        Returns:
            List of updated Customer objects.

        Example:
            >>> from stocktrim_public_api_client.generated.models import CustomerDto
            >>> updated = await client.customers.update(
            ...     CustomerDto(code="CUST-001", name="Updated Name")
            ... )
        """
        response = await put_api_customers.asyncio_detailed(
            client=self._client,
            body=customer,
        )
        result = unwrap(response)
        return result if isinstance(result, list) else []
