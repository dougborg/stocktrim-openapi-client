"""Bill of Materials (BOM) operations."""

from __future__ import annotations

from typing import cast

from stocktrim_public_api_client.client_types import UNSET, Unset
from stocktrim_public_api_client.generated.api.bill_of_materials import (
    delete_api_boms,
    get_api_boms,
    post_api_boms,
)
from stocktrim_public_api_client.generated.models.bill_of_materials_request_dto import (
    BillOfMaterialsRequestDto,
)
from stocktrim_public_api_client.generated.models.bill_of_materials_response_dto import (
    BillOfMaterialsResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class BillOfMaterials(Base):
    """Bill of Materials management.

    Provides operations for managing BOMs - the relationships between
    assembled products and their component parts.
    """

    async def get(
        self,
        product_id: str | Unset = UNSET,
        component_id: str | Unset = UNSET,
    ) -> list[BillOfMaterialsResponseDto]:
        """Get BOMs with optional filters.

        Args:
            product_id: Optional filter by product (assembled item).
            component_id: Optional filter by component (part).

        Returns:
            List of BillOfMaterialsResponseDto objects.

        Example:
            >>> # Get all BOMs
            >>> boms = await client.bill_of_materials.get()
            >>>
            >>> # Get BOMs for a specific product
            >>> boms = await client.bill_of_materials.get(product_id="WIDGET-001")
            >>>
            >>> # Get all BOMs that use a specific component
            >>> boms = await client.bill_of_materials.get(component_id="PART-123")
        """
        response = await get_api_boms.asyncio_detailed(
            client=self._client,
            product_id=product_id,
            component_id=component_id,
        )
        result = unwrap(response)
        return result if isinstance(result, list) else []  # type: ignore[return-value]

    async def create(
        self,
        bom: BillOfMaterialsRequestDto,
    ) -> BillOfMaterialsResponseDto:
        """Create a BOM relationship.

        Args:
            bom: BOM data with product_id, component_id, and quantity.

        Returns:
            Created BillOfMaterialsResponseDto object.

        Example:
            >>> from stocktrim_public_api_client.generated.models import (
            ...     BillOfMaterialsRequestDto,
            ... )
            >>>
            >>> # Widget requires 2 units of Part-A
            >>> bom = await client.bill_of_materials.create(
            ...     BillOfMaterialsRequestDto(
            ...         product_id="WIDGET-001",
            ...         component_id="PART-A",
            ...         quantity=2.0,
            ...     )
            ... )
            >>> print(f"Assembly time: {bom.assembly_time_days} days")
        """
        response = await post_api_boms.asyncio_detailed(
            client=self._client,
            body=bom,
        )
        return cast(BillOfMaterialsResponseDto, unwrap(response))

    async def delete(
        self,
        product_id: str,
        component_id: str,
    ) -> None:
        """Delete a BOM relationship.

        Args:
            product_id: Product (assembled item) ID.
            component_id: Component (part) ID.

        Returns:
            None. Raises exception if deletion fails.

        Example:
            >>> await client.bill_of_materials.delete(
            ...     product_id="WIDGET-001",
            ...     component_id="PART-A",
            ... )
        """
        response = await delete_api_boms.asyncio_detailed(
            client=self._client,
            product_id=product_id,
            component_id=component_id,
        )
        unwrap(response)  # Raises on error

    async def get_for_product(
        self,
        product_id: str,
    ) -> list[BillOfMaterialsResponseDto]:
        """Get all components for a product (assembled item).

        Convenience method for getting the complete BOM for a product.

        Args:
            product_id: Product ID to get components for.

        Returns:
            List of BillOfMaterialsResponseDto objects showing all components.

        Example:
            >>> # Get all parts needed to build WIDGET-001
            >>> components = await client.bill_of_materials.get_for_product(
            ...     "WIDGET-001"
            ... )
            >>> for comp in components:
            ...     print(f"Need {comp.quantity} of {comp.component_id}")
        """
        return await self.get(product_id=product_id)

    async def get_uses_of_component(
        self,
        component_id: str,
    ) -> list[BillOfMaterialsResponseDto]:
        """Get all products that use a specific component.

        Convenience method for finding where a component is used.

        Args:
            component_id: Component ID to search for.

        Returns:
            List of BillOfMaterialsResponseDto objects showing all products
            that use this component.

        Example:
            >>> # Find all products that use PART-A
            >>> usage = await client.bill_of_materials.get_uses_of_component("PART-A")
            >>> for bom in usage:
            ...     print(f"{bom.product_id} uses {bom.quantity} units")
        """
        return await self.get(component_id=component_id)
