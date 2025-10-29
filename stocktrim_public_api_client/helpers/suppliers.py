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
        return result if isinstance(result, list) else []

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
