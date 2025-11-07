"""Supplier management service."""

from __future__ import annotations

import logging

from stocktrim_mcp_server.services.base import BaseService
from stocktrim_public_api_client.generated.models import SupplierResponseDto

logger = logging.getLogger(__name__)


class SupplierService(BaseService):
    """Service for supplier management operations."""

    async def get_by_code(self, code: str) -> SupplierResponseDto | None:
        """Get a single supplier by code.

        Args:
            code: Supplier code

        Returns:
            Supplier details if found, None otherwise

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Supplier code")
        logger.info(f"Getting supplier: {code}")

        supplier = await self._client.suppliers.find_by_code(code)

        if not supplier:
            logger.warning(f"Supplier not found: {code}")
            return None

        logger.info(f"Supplier retrieved: {code}")
        return supplier

    async def list_all(self, active_only: bool = False) -> list[SupplierResponseDto]:
        """List all suppliers.

        Note: The active_only parameter is included for API compatibility but is not
        currently used because the StockTrim API does not expose an is_active field
        for suppliers.

        Args:
            active_only: Reserved for future use (default: False)

        Returns:
            List of suppliers

        Raises:
            Exception: If API call fails
        """
        logger.info("Listing suppliers")

        # Get all suppliers
        suppliers = await self._client.suppliers.get_all()

        # Handle API returning either single object or list
        if isinstance(suppliers, list):
            pass  # Already a list
        else:
            suppliers = [suppliers] if suppliers else []

        logger.info(f"Found {len(suppliers)} suppliers")
        return suppliers

    async def create(
        self,
        code: str,
        name: str,
        email: str | None = None,
        primary_contact: str | None = None,
        default_lead_time: int | None = None,
        street_address: str | None = None,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        state: str | None = None,
        country: str | None = None,
        post_code: str | None = None,
        external_id: str | None = None,
    ) -> SupplierResponseDto:
        """Create a new supplier.

        Args:
            code: Unique supplier code
            name: Supplier name
            email: Supplier email (optional)
            primary_contact: Primary contact name (optional)
            default_lead_time: Default lead time in days (optional)
            street_address: Street address (optional)
            address_line_1: Address line 1 (optional)
            address_line_2: Address line 2 (optional)
            state: State/province (optional)
            country: Country (optional)
            post_code: Postal code (optional)
            external_id: External system ID (optional)

        Returns:
            Created supplier details

        Raises:
            ValueError: If required fields are empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Supplier code")
        self.validate_not_empty(name, "Supplier name")

        logger.info(f"Creating supplier: {code}")

        # Import SupplierRequestDto from generated models
        from stocktrim_public_api_client.generated.models import SupplierRequestDto

        # Create supplier DTO with all fields
        supplier_dto = SupplierRequestDto(
            supplier_code=code,
            supplier_name=name,
            email_address=email,
            primary_contact_name=primary_contact,
            default_lead_time=default_lead_time,
            street_address=street_address,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            state=state,
            country=country,
            post_code=post_code,
            external_id=external_id,
        )

        # Create supplier
        created_supplier = await self._client.suppliers.create_one(supplier_dto)

        if not created_supplier:
            raise Exception(f"Failed to create supplier {code}")

        logger.info(f"Supplier created: {code}")
        return created_supplier

    async def delete(self, code: str) -> tuple[bool, str]:
        """Delete a supplier by code.

        Args:
            code: Supplier code to delete

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            ValueError: If code is empty
            Exception: If API call fails
        """
        self.validate_not_empty(code, "Supplier code")
        logger.info(f"Deleting supplier: {code}")

        # Check if supplier exists first
        supplier = await self._client.suppliers.find_by_code(code)
        if not supplier:
            return False, f"Supplier {code} not found"

        # Delete supplier
        await self._client.suppliers.delete(code)

        logger.info(f"Supplier deleted: {code}")
        return True, f"Supplier {code} deleted successfully"
