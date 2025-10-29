"""Supplier management operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.suppliers import (
    delete_api_suppliers,
    get_api_suppliers,
    post_api_suppliers,
)
from stocktrim_public_api_client.generated.models.supplier_request_dto import (
    SupplierRequestDto,
)
from stocktrim_public_api_client.generated.models.supplier_response_dto import (
    SupplierResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Suppliers(Base):
    """Supplier management.

    Provides operations for managing suppliers in StockTrim.
    """

    async def get_all(
        self,
        code: str | Unset = UNSET,
    ) -> SupplierResponseDto | list[SupplierResponseDto]:
        """Get suppliers, optionally filtered by code.

        Note: The API returns a single object when filtered by code,
        but this is inconsistent with other endpoints. We preserve
        the API's behavior here.

        Args:
            code: Optional supplier code filter.

        Returns:
            SupplierResponseDto or list of SupplierResponseDto objects.

        Example:
            >>> suppliers = await client.suppliers.get_all()
            >>> supplier = await client.suppliers.get_all(code="SUP-001")
        """
        response = await get_api_suppliers.asyncio_detailed(
            client=self._client,
            code=code,
        )
        return cast(
            SupplierResponseDto | list[SupplierResponseDto],
            unwrap(response),
        )

    async def create(
        self, suppliers: list[SupplierRequestDto]
    ) -> list[SupplierResponseDto]:
        """Create new suppliers.

        Args:
            suppliers: List of supplier data to create.

        Returns:
            List of created SupplierResponseDto objects.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SupplierRequestDto,
            ... )
            >>> suppliers = await client.suppliers.create(
            ...     [
            ...         SupplierRequestDto(code="SUP-001", name="Supplier One"),
            ...         SupplierRequestDto(code="SUP-002", name="Supplier Two"),
            ...     ]
            ... )
        """
        response = await post_api_suppliers.asyncio_detailed(
            client=self._client,
            body=suppliers,
        )
        result = unwrap(response)
        # unwrap() returns the actual type or raises an exception on error
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def delete(self, supplier_code_or_name: str | Unset = UNSET) -> None:
        """Delete supplier(s).

        Args:
            supplier_code_or_name: Supplier code or name to delete.

        Example:
            >>> await client.suppliers.delete(supplier_code_or_name="SUP-001")
        """
        await delete_api_suppliers.asyncio_detailed(
            client=self._client,
            supplier_code_or_name=supplier_code_or_name,
        )

    # Convenience methods

    async def find_by_code(self, code: str) -> SupplierResponseDto | None:
        """Find a single supplier by exact code match.

        This method handles the API's inconsistent return type (single vs list)
        and always returns a single object or None.

        Args:
            code: The exact supplier code to search for.

        Returns:
            SupplierResponseDto if found, None otherwise.

        Example:
            >>> supplier = await client.suppliers.find_by_code("SUP-001")
            >>> if supplier:
            ...     print(f"Found: {supplier.name}")
        """
        result = await self.get_all(code=code)
        # Handle API returning either single object or list
        if isinstance(result, list):
            return result[0] if result else None
        return result

    async def create_one(
        self, supplier: SupplierRequestDto
    ) -> SupplierResponseDto | None:
        """Create a single supplier.

        This is a convenience wrapper around the batch create() method
        that accepts a single supplier instead of a list.

        Args:
            supplier: Supplier data to create.

        Returns:
            Created SupplierResponseDto object, or None if creation failed.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SupplierRequestDto,
            ... )
            >>> supplier = await client.suppliers.create_one(
            ...     SupplierRequestDto(code="SUP-001", name="New Supplier")
            ... )
        """
        results = await self.create([supplier])
        return results[0] if results else None

    async def exists(self, code: str) -> bool:
        """Check if a supplier with given code exists.

        Args:
            code: The supplier code to check.

        Returns:
            True if supplier exists, False otherwise.

        Example:
            >>> if await client.suppliers.exists("SUP-001"):
            ...     print("Supplier exists")
        """
        supplier = await self.find_by_code(code)
        return supplier is not None
