"""Customer management operations."""

from __future__ import annotations

from typing import Any, cast

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

    Example:
        >>> async with StockTrimClient() as client:
        ...     # List all customers
        ...     customers = await client.customers.list()
        ...
        ...     # Get customer by code
        ...     customer = await client.customers.get("CUST-001")
        ...
        ...     # Update customer
        ...     await client.customers.update(CustomerDto(...))
    """

    async def list(self, **filters: Any) -> list[Customer]:
        """List all customers with optional filters.

        Args:
            **filters: Optional filtering parameters.

        Returns:
            List of Customer objects.

        Example:
            >>> customers = await client.customers.list()
        """
        response = await get_api_customers.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def get(self, code: str) -> Customer:
        """Get a specific customer by code.

        Args:
            code: The customer code.

        Returns:
            Customer object.

        Example:
            >>> customer = await client.customers.get("CUST-001")
        """
        response = await get_api_customers_code.asyncio_detailed(
            client=self._client,
            code=code,
        )
        return cast(Customer, unwrap(response))

    async def update(self, customer_data: list[CustomerDto]) -> list[Customer]:
        """Update customers.

        Args:
            customer_data: List of CustomerDto models with customer details.

        Returns:
            List of updated Customer objects.

        Example:
            >>> from stocktrim_public_api_client.generated.models import CustomerDto
            >>> updated = await client.customers.update(
            ...     [CustomerDto(code="CUST-001", name="Updated Name")]
            ... )
        """
        response = await put_api_customers.asyncio_detailed(
            client=self._client,
            body=customer_data,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []
