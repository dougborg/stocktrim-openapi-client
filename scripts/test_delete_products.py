#!/usr/bin/env python3
"""Test DELETE /api/Products status code."""

import asyncio
import logging
from datetime import datetime

from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.generated.models import ProductsRequestDto

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("stocktrim_client").setLevel(logging.DEBUG)


async def main():
    """Test DELETE /api/Products status code."""
    client = StockTrimClient()

    try:
        # Create test product
        test_id = f"TEST-DEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Creating test product: {test_id}")

        product = ProductsRequestDto(
            product_id=test_id,
            product_code_readable=test_id,
            name="Test Product for DELETE",
        )

        await client.products.create(product)
        logger.info(f"✅ Created product: {test_id}")

        # Delete it
        logger.info(f"Deleting product: {test_id}")
        logger.info("About to call client.products.delete()...")
        try:
            result = await client.products.delete(test_id)
            logger.info("✅ DELETE completed successfully")
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result value: {result}")
        except Exception as e:
            logger.error(f"❌ DELETE failed: {e}", exc_info=True)

    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())
