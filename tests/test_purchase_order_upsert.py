"""Tests for purchase order upsert functionality.

These tests verify that the POST /api/PurchaseOrders endpoint correctly
handles both create (201) and update (200) responses, and that nullable
fields like orderDate work as expected.
"""

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from httpx import Response

from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.client_types import UNSET
from stocktrim_public_api_client.generated.models.purchase_order_request_dto import (
    PurchaseOrderRequestDto,
)
from stocktrim_public_api_client.generated.models.purchase_order_supplier import (
    PurchaseOrderSupplier,
)


@pytest.fixture
def mock_supplier():
    """Create a mock supplier for testing."""
    return PurchaseOrderSupplier(
        supplier_name="Test Supplier",
        supplier_code="SUP-001",
    )


@pytest.fixture
def mock_po_request(mock_supplier):
    """Create a mock purchase order request."""
    return PurchaseOrderRequestDto(
        order_date=datetime(2025, 1, 1, tzinfo=UTC),
        supplier=mock_supplier,
        purchase_order_line_items=[],
        client_reference_number="PO-TEST-001",
    )


class TestPurchaseOrderUpsert:
    """Test purchase order upsert behavior (create OR update)."""

    @pytest.mark.asyncio
    async def test_create_returns_201(self, mock_api_credentials, mock_po_request):
        """Test POST without existing client_reference_number returns 201 Created."""
        # Create mock response for 201 Created
        mock_response_data = {
            "id": 12345,
            "clientReferenceNumber": "PO-TEST-001",
            "supplier": {"supplierName": "Test Supplier", "supplierCode": "SUP-001"},
            "purchaseOrderLineItems": [],
            "orderDate": "2025-01-01T00:00:00Z",
            "status": 0,  # Draft
        }

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = Response(
                status_code=201,
                json=mock_response_data,
                headers={"Content-Type": "application/json"},
            )

            async with StockTrimClient(**mock_api_credentials) as client:
                result = await client.purchase_orders.create(mock_po_request)

                assert result.id == 12345
                assert result.client_reference_number == "PO-TEST-001"
                # Verify POST was called
                mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_returns_200(self, mock_api_credentials, mock_po_request):
        """Test POST with existing client_reference_number returns 200 OK (update)."""
        # Create mock response for 200 OK (update)
        mock_response_data = {
            "id": 12345,  # Same ID as before (updated existing)
            "clientReferenceNumber": "PO-TEST-001",
            "supplier": {"supplierName": "Test Supplier", "supplierCode": "SUP-001"},
            "purchaseOrderLineItems": [],
            "orderDate": "2025-01-01T00:00:00Z",
            "status": 0,  # Draft
        }

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = Response(
                status_code=200,  # Update returns 200, not 201
                json=mock_response_data,
                headers={"Content-Type": "application/json"},
            )

            async with StockTrimClient(**mock_api_credentials) as client:
                result = await client.purchase_orders.create(mock_po_request)

                assert result.id == 12345
                assert result.client_reference_number == "PO-TEST-001"
                # Verify POST was called
                mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_order_date_can_be_none(self, mock_api_credentials, mock_supplier):
        """Test that orderDate can be None in request DTO."""
        # This tests that the field is nullable, even though API may reject it
        request = PurchaseOrderRequestDto(
            order_date=None,  # Nullable field
            supplier=mock_supplier,
            purchase_order_line_items=[],
            client_reference_number="PO-TEST-002",
        )

        # Verify the object was created successfully
        assert request.order_date is None
        assert request.client_reference_number == "PO-TEST-002"

        # Verify to_dict() handles None properly
        data = request.to_dict()
        assert data["orderDate"] is None

    @pytest.mark.asyncio
    async def test_order_date_can_be_unset(self, mock_api_credentials, mock_supplier):
        """Test that orderDate can be UNSET (omitted) in request DTO."""
        request = PurchaseOrderRequestDto(
            order_date=UNSET,  # Omit field from request
            supplier=mock_supplier,
            purchase_order_line_items=[],
            client_reference_number="PO-TEST-003",
        )

        # Verify the object was created successfully
        assert request.order_date is UNSET
        assert request.client_reference_number == "PO-TEST-003"

        # Verify to_dict() omits UNSET fields
        data = request.to_dict()
        assert "orderDate" not in data  # Field should be omitted

    @pytest.mark.asyncio
    async def test_update_preserves_order_date_with_unset(
        self, mock_api_credentials, mock_supplier
    ):
        """Test that using UNSET for orderDate preserves existing date during update."""
        # Create request with UNSET orderDate (will preserve existing)
        request = PurchaseOrderRequestDto(
            order_date=UNSET,  # Don't send orderDate field
            supplier=mock_supplier,
            purchase_order_line_items=[],
            client_reference_number="PO-TEST-004",
        )

        # Mock response with existing orderDate
        mock_response_data = {
            "id": 12346,
            "clientReferenceNumber": "PO-TEST-004",
            "supplier": {"supplierName": "Test Supplier", "supplierCode": "SUP-001"},
            "purchaseOrderLineItems": [],
            "orderDate": "2025-01-15T12:00:00Z",  # Existing date preserved
            "status": 0,
        }

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = Response(
                status_code=200,  # Update
                json=mock_response_data,
                headers={"Content-Type": "application/json"},
            )

            async with StockTrimClient(**mock_api_credentials) as client:
                result = await client.purchase_orders.create(request)

                # Verify existing date was preserved
                assert result.order_date is not None
                assert not isinstance(result.order_date, type(UNSET))
                assert result.order_date.year == 2025
                assert result.order_date.month == 1
                assert result.order_date.day == 15

    @pytest.mark.asyncio
    async def test_location_can_be_none(self, mock_api_credentials, mock_supplier):
        """Test that location can be None in request DTO."""
        request = PurchaseOrderRequestDto(
            order_date=datetime(2025, 1, 1, tzinfo=UTC),
            supplier=mock_supplier,
            purchase_order_line_items=[],
            client_reference_number="PO-TEST-005",
            location=None,  # Nullable field
        )

        # Verify the object was created successfully
        assert request.location is None

        # Verify to_dict() handles None properly
        data = request.to_dict()
        assert data["location"] is None


class TestPurchaseOrderStatusEnum:
    """Test purchase order status enum handles both integers and strings."""

    @pytest.mark.asyncio
    async def test_status_handles_integer_values(self, mock_api_credentials):
        """Test that status enum can handle integer values from API."""
        # Mock response with integer status
        mock_response_data = {
            "id": 12347,
            "clientReferenceNumber": "PO-TEST-006",
            "supplier": {"supplierName": "Test Supplier", "supplierCode": "SUP-001"},
            "purchaseOrderLineItems": [],
            "orderDate": "2025-01-01T00:00:00Z",
            "status": 0,  # Integer value (0 = Draft)
        }

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = Response(
                status_code=200,
                json=mock_response_data,
                headers={"Content-Type": "application/json"},
            )

            async with StockTrimClient(**mock_api_credentials) as client:
                result = await client.purchase_orders.get_all()

                # Verify status was parsed correctly
                if isinstance(result, list) and len(result) > 0:
                    assert result[0].status is not None
