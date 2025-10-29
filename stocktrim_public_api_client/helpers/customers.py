"""Customer management operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.generated.api.customers import (
    get_api_customers,
    get_api_customers_code,
    put_api_customers,
)
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
        # unwrap() returns the actual type or raises an exception on error
        # Type checker sees the union but at runtime we get the expected type
        return result if isinstance(result, list) else []  # type: ignore[return-value]

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

    async def update(self, customer: CustomerDto) -> list[CustomerDto]:
        """Update a customer (create or update based on code).

        Args:
            customer: Customer data to update.

        Returns:
            List of updated CustomerDto objects.

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
        if isinstance(result, list):
            return cast(list[CustomerDto], result)
        return []

    # Convenience methods

    async def exists(self, code: str) -> bool:
        """Check if a customer with given code exists.

        Args:
            code: The customer code to check.

        Returns:
            True if customer exists, False otherwise.

        Example:
            >>> if await client.customers.exists("CUST-001"):
            ...     print("Customer exists")
        """
        try:
            await self.get(code)
            return True
        except Exception:
            return False

    async def find_or_create(self, code: str, **defaults) -> CustomerDto:
        """Get customer by code, or create if doesn't exist.

        Args:
            code: The customer code.
            **defaults: Default values to use when creating the customer.

        Returns:
            CustomerDto object (existing or newly created).

        Example:
            >>> customer = await client.customers.find_or_create(
            ...     "CUST-001", name="New Customer", email="customer@example.com"
            ... )
        """
        try:
            return await self.get(code)
        except Exception:
            # Customer doesn't exist, create it
            new_customer = CustomerDto(code=code, **defaults)
            await self.update(new_customer)
            return await self.get(code)
