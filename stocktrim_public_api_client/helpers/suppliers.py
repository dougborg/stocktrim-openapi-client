"""Supplier management operations."""

from __future__ import annotations

from typing import Any, cast

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

    Provides CRUD operations for suppliers in StockTrim.

    Example:
        >>> async with StockTrimClient() as client:
        ...     suppliers = await client.suppliers.list()
        ...     supplier = await client.suppliers.get("SUP-001")
        ...     await client.suppliers.create(SupplierRequestDto(...))
        ...     await client.suppliers.delete("SUP-001")
    """

    async def list(self, **filters: Any) -> list[SupplierResponseDto]:
        """List all suppliers.

        Args:
            **filters: Optional filtering parameters.

        Returns:
            List of SupplierResponseDto objects.

        Example:
            >>> suppliers = await client.suppliers.list()
        """
        response = await get_api_suppliers.asyncio_detailed(
            client=self._client,
            **filters,
        )
        result = unwrap(response)
        if isinstance(result, list):
            return result
        return []

    async def get(self, code: str) -> SupplierResponseDto:
        """Get a specific supplier by code.

        Args:
            code: The supplier code.

        Returns:
            SupplierResponseDto object.

        Example:
            >>> supplier = await client.suppliers.get("SUP-001")
        """
        response = await get_api_suppliers.asyncio_detailed(
            client=self._client,
            code=code,
        )
        result = unwrap(response)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return cast(SupplierResponseDto, result)

    async def create(self, supplier_data: SupplierRequestDto) -> SupplierResponseDto:
        """Create a new supplier.

        Args:
            supplier_data: SupplierRequestDto model with supplier details.

        Returns:
            SupplierResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     SupplierRequestDto,
            ... )
            >>> supplier = await client.suppliers.create(
            ...     SupplierRequestDto(code="SUP-001", name="New Supplier")
            ... )
        """
        response = await post_api_suppliers.asyncio_detailed(
            client=self._client,
            body=[supplier_data],
        )
        result = unwrap(response)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return cast(SupplierResponseDto, result)

    async def delete(self, supplier_code_or_name: str) -> None:
        """Delete a supplier.

        Args:
            supplier_code_or_name: The supplier code or name to delete.

        Example:
            >>> await client.suppliers.delete("SUP-001")
        """
        await delete_api_suppliers.asyncio_detailed(
            client=self._client,
            supplier_code_or_name=supplier_code_or_name,
        )
