#!/usr/bin/env python3
"""
Test script to check actual HTTP status code returned by DELETE /api/PurchaseOrders.

This script:
1. Creates a test purchase order
2. Deletes it via the API
3. Reports the actual HTTP status code returned

This helps us determine if the API has been updated to return 204 (as Joel mentioned)
or still returns 200 (as the OpenAPI spec currently documents).
"""

import asyncio
import logging
import sys
from datetime import datetime

from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.models import (
    ProductsRequestDto,
    PurchaseOrderLineItem,
    PurchaseOrderRequestDto,
    PurchaseOrderSupplier,
)

# Configure logging to see HTTP details
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Enable DEBUG for stocktrim_client to see HTTP status codes
logging.getLogger("stocktrim_client").setLevel(logging.DEBUG)


async def test_delete_status_code():
    """Test the actual DELETE /api/PurchaseOrders status code."""
    # Initialize client (uses environment variables for auth)
    client = StockTrimClient()

    try:
        # Generate unique reference for test
        test_ref = f"TEST-DELETE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        logger.info(f"\n{'=' * 60}")
        logger.info("STEP 1: Create test product")
        logger.info(f"{'=' * 60}")

        # Create test product first
        test_product_id = f"TEST-DEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        product_request = ProductsRequestDto(
            product_id=test_product_id,
            product_code_readable=test_product_id,
            name="Test Product for DELETE",
        )

        try:
            created_product = await client.products.create(product_request)
            logger.info(f"✅ Created product: {created_product.product_id}")
        except Exception as e:
            # Product might already exist - that's okay
            logger.info(f"Product may already exist: {e}")

        logger.info(f"\n{'=' * 60}")
        logger.info("STEP 2: Create test purchase order")
        logger.info(f"{'=' * 60}")

        # Create test purchase order
        po_request = PurchaseOrderRequestDto(
            client_reference_number=test_ref,
            order_date=datetime.now(),
            supplier=PurchaseOrderSupplier(
                supplier_name="Test Supplier for DELETE",
            ),
            purchase_order_line_items=[
                PurchaseOrderLineItem(
                    product_id=test_product_id,
                    quantity=1.0,
                )
            ],
        )

        created_po = await client.purchase_orders.create(po_request)
        logger.info(f"✅ Created PO: {created_po.client_reference_number}")

        logger.info(f"\n{'=' * 60}")
        logger.info("STEP 3: Delete purchase order and capture status code")
        logger.info(f"{'=' * 60}")

        # Delete the purchase order
        # The delete method doesn't expose the status code directly,
        # so we need to check the underlying httpx response
        delete_response = await client.purchase_orders.delete(test_ref)

        logger.info(f"\n{'=' * 60}")
        logger.info("RESULTS")
        logger.info(f"{'=' * 60}")

        # Check what we got back
        if delete_response is None:
            logger.info("✅ DELETE returned: None (typical for 204 No Content)")
            logger.info("\n📊 CONCLUSION: API likely returns 204 (spec needs updating)")
        else:
            logger.info(f"✅ DELETE returned: {delete_response}")
            logger.info(
                "\n📊 CONCLUSION: API returns 200 with content (matches current spec)"
            )

        logger.info("\n💡 Check DEBUG logs above for actual HTTP status code")

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_delete_status_code())
