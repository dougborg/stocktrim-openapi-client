"""
StockTrimClient - The pythonic StockTrim API client with automatic resilience.

This client uses httpx's native transport layer to provide automatic retries,
custom header authentication, and error handling for all API calls without any
decorators or wrapper methods needed.
"""

import contextlib
import logging
import os
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

import httpx
from dotenv import load_dotenv
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from httpx import AsyncHTTPTransport
else:
    AsyncHTTPTransport = httpx.AsyncHTTPTransport

from .generated.client import AuthenticatedClient


class ResilientAsyncTransport(AsyncHTTPTransport):
    """
    Custom async transport that adds retry logic and custom authentication
    directly at the HTTP transport layer.

    This makes ALL requests through the client automatically resilient
    without any wrapper methods or decorators.

    Features:
    - Automatic retries with exponential backoff using tenacity
    - Custom header authentication (api-auth-id, api-auth-signature)
    - Request/response logging and metrics
    """

    def __init__(
        self,
        api_auth_id: str,
        api_auth_signature: str,
        max_retries: int = 5,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.api_auth_id = api_auth_id
        self.api_auth_signature = api_auth_signature
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle the request with automatic retries and custom authentication.

        This method is called for every HTTP request made through the client.
        """
        # Add StockTrim authentication headers
        request.headers["api-auth-id"] = self.api_auth_id
        request.headers["api-auth-signature"] = self.api_auth_signature

        return await self._handle_single_request(request)

    async def _handle_single_request(self, request: httpx.Request) -> httpx.Response:
        """Handle a single request with retries using tenacity."""

        # Define a properly typed retry decorator
        def _make_retry_decorator() -> Callable[
            [Callable[[], Awaitable[httpx.Response]]],
            Callable[[], Awaitable[httpx.Response]],
        ]:
            return retry(
                stop=stop_after_attempt(self.max_retries + 1),
                wait=wait_exponential(multiplier=1, min=1, max=60),
                retry=(
                    retry_if_result(
                        lambda response: response.status_code == 429
                        or (500 <= response.status_code < 600)
                    )
                    | retry_if_exception_type(
                        (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError)
                    )
                ),
                reraise=True,
            )

        @_make_retry_decorator()
        async def _make_request_with_retry() -> httpx.Response:
            """Make the actual HTTP request with retry logic."""
            response = await super(ResilientAsyncTransport, self).handle_async_request(
                request
            )

            if response.status_code == 429:
                self.logger.warning(
                    "Rate limited, retrying after exponential backoff"
                )

            elif 500 <= response.status_code < 600:
                self.logger.warning(
                    f"Server error {response.status_code}, retrying with exponential backoff"
                )

            return response

        # Execute the request with retries
        try:
            response = await _make_request_with_retry()
            return response
        except RetryError as e:
            # For retry errors (when server keeps returning 4xx/5xx), return the last response
            self.logger.error(
                f"Request failed after {self.max_retries} retries, extracting last response"
            )

            # Extract the last response - tenacity stores it in the last_attempt
            try:
                if hasattr(e, "last_attempt") and e.last_attempt is not None:
                    last_response = e.last_attempt.result()
                    self.logger.debug(f"Got last response: {type(last_response)}")
                    if isinstance(last_response, httpx.Response) or (
                        hasattr(last_response, "status_code")
                    ):
                        # Handle both real responses and mocks (for testing)
                        self.logger.debug(
                            f"Returning last response with status {last_response.status_code}"
                        )
                        return last_response
                    else:
                        self.logger.debug(
                            f"Last response is not httpx.Response, it's {type(last_response)}"
                        )
                else:
                    self.logger.debug("No last_attempt found in retry error")
            except Exception as extract_error:
                self.logger.debug(f"Error extracting last response: {extract_error}")

            # If we can't extract the response, re-raise
            self.logger.error("Could not extract last response from retry error")
            raise
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError) as e:
            # For network errors, we want to re-raise the exception
            self.logger.error(f"Network error after {self.max_retries} retries: {e}")
            raise
        except Exception as e:
            # For other unexpected errors, re-raise
            self.logger.error(f"Unexpected error after {self.max_retries} retries: {e}")
            raise


class StockTrimClient:
    """
    A pythonic StockTrim API client with automatic resilience.

    This client provides:
    - Automatic retries with exponential backoff
    - Custom header authentication for StockTrim API
    - Consistent error handling
    - Modern async/await support

    Example usage:
        async with StockTrimClient() as client:
            # All API calls automatically get retries and authentication
            response = await some_api_method.asyncio_detailed(client=client)
    """

    def __init__(
        self,
        api_auth_id: str | None = None,
        api_auth_signature: str | None = None,
        base_url: str = "https://api.stocktrim.com",
        max_retries: int = 5,
        timeout: float = 30.0,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the StockTrim API client.

        Args:
            api_auth_id: StockTrim API authentication ID (or set STOCKTRIM_API_AUTH_ID env var)
            api_auth_signature: StockTrim API authentication signature (or set STOCKTRIM_API_AUTH_SIGNATURE env var)
            base_url: Base URL for the StockTrim API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            logger: Custom logger instance
        """
        # Load environment variables
        load_dotenv()

        self.api_auth_id = api_auth_id or os.getenv("STOCKTRIM_API_AUTH_ID")
        self.api_auth_signature = api_auth_signature or os.getenv("STOCKTRIM_API_AUTH_SIGNATURE")
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)

        if not self.api_auth_id or not self.api_auth_signature:
            raise ValueError(
                "StockTrim API credentials are required. "
                "Provide api_auth_id and api_auth_signature parameters or set "
                "STOCKTRIM_API_AUTH_ID and STOCKTRIM_API_AUTH_SIGNATURE environment variables."
            )

        self._client: AuthenticatedClient | None = None

    @property
    def client(self) -> AuthenticatedClient:
        """
        Get the authenticated client instance with resilient transport.

        This property provides access to the fully configured OpenAPI client
        with automatic retries and authentication built into the transport layer.
        """
        if self._client is None:
            # Create the resilient transport
            # At this point, credentials are guaranteed to be strings due to validation in __init__
            assert self.api_auth_id is not None
            assert self.api_auth_signature is not None
            
            transport = ResilientAsyncTransport(
                api_auth_id=self.api_auth_id,
                api_auth_signature=self.api_auth_signature,
                max_retries=self.max_retries,
                logger=self.logger,
            )

            # Create the authenticated client with custom transport
            self._client = AuthenticatedClient(
                base_url=self.base_url,
                token="",  # StockTrim uses custom headers, not bearer token
                timeout=self.timeout,
                transport=transport,
            )

        return self._client

    async def __aenter__(self) -> "StockTrimClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        await self.close()

    async def close(self) -> None:
        """Close the client and clean up resources."""
        if self._client is not None:
            with contextlib.suppress(Exception):
                await self._client.get_async_httpx_client().aclose()
            self._client = None

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"StockTrimClient(base_url='{self.base_url}', max_retries={self.max_retries})"
