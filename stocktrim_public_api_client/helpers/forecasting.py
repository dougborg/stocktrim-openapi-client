"""Forecast management and processing status operations."""

from __future__ import annotations

import asyncio
import time
from typing import cast

from stocktrim_public_api_client.generated.api.processing_status import (
    get_api_processing_status,
)
from stocktrim_public_api_client.generated.api.run_forecast_calculations import (
    post_api_run_forecast_calculations,
)
from stocktrim_public_api_client.generated.models.processing_status_response_dto import (
    ProcessingStatusResponseDto,
)
from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap


class Forecasting(Base):
    """Forecast management and processing.

    Provides operations for triggering forecast recalculation and monitoring
    processing status.
    """

    async def run_calculations(self) -> None:
        """Trigger forecast recalculation for all products.

        This initiates a background process to recalculate forecasts based on
        current sales data, inventory levels, and configured algorithms.

        The calculation runs asynchronously. Use get_processing_status() or
        wait_for_completion() to monitor progress.

        Returns:
            None. Raises exception if the trigger fails.

        Example:
            >>> # Trigger forecast calculation
            >>> await client.forecasting.run_calculations()
            >>>
            >>> # Wait for completion
            >>> status = await client.forecasting.wait_for_completion()
            >>> print(f"Forecasts updated: {status.status_message}")
        """
        response = await post_api_run_forecast_calculations.asyncio_detailed(
            client=self._client,
        )
        unwrap(response)  # Raises on error, otherwise returns None

    async def get_processing_status(self) -> ProcessingStatusResponseDto:
        """Get current processing status.

        Returns:
            ProcessingStatusResponseDto with:
            - is_processing: Boolean indicating if calculation is running
            - percentage_complete: Progress percentage (0-100)
            - status_message: Current status description

        Example:
            >>> status = await client.forecasting.get_processing_status()
            >>> if status.is_processing:
            ...     print(f"Progress: {status.percentage_complete}%")
            ...     print(f"Status: {status.status_message}")
            >>> else:
            ...     print("No processing in progress")
        """
        response = await get_api_processing_status.asyncio_detailed(
            client=self._client,
        )
        return cast(ProcessingStatusResponseDto, unwrap(response))

    async def wait_for_completion(
        self,
        poll_interval: int = 5,
        timeout: int = 600,
    ) -> ProcessingStatusResponseDto:
        """Wait for forecast calculation to complete.

        Polls the processing status at regular intervals until the calculation
        is complete or the timeout is reached.

        Args:
            poll_interval: Seconds between status checks (default: 5).
            timeout: Maximum seconds to wait (default: 600 = 10 minutes).

        Returns:
            Final ProcessingStatusResponseDto when complete.

        Raises:
            TimeoutError: If calculation doesn't complete within timeout.

        Example:
            >>> # Trigger and wait
            >>> await client.forecasting.run_calculations()
            >>> final_status = await client.forecasting.wait_for_completion(
            ...     poll_interval=5,
            ...     timeout=300,
            ... )
            >>> print(f"Complete: {final_status.status_message}")
        """
        start_time = time.time()

        while True:
            status = await self.get_processing_status()

            # Check if done
            if not status.is_processing:
                return status

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Forecast calculation did not complete within {timeout} seconds. "
                    f"Last status: {status.status_message} "
                    f"({status.percentage_complete}% complete)"
                )

            # Wait before next poll
            await asyncio.sleep(poll_interval)
