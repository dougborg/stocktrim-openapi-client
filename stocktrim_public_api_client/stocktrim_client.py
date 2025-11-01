"""
StockTrimClient - The pythonic StockTrim API client with automatic resilience.

This client uses httpx's native transport layer to provide automatic retries,
custom header authentication, and error handling for all API calls without any
decorators or wrapper methods needed.
"""

import contextlib
import json
import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

import httpx
from dotenv import load_dotenv
from httpx import AsyncHTTPTransport
from httpx_retries import Retry, RetryTransport

from .client_types import Unset
from .generated.client import AuthenticatedClient

# StockTrim doesn't have standardized error response models in the OpenAPI spec
# We'll add support for ProblemDetails if present, but also handle generic errors
try:
    from .generated.models.problem_details import ProblemDetails
except ImportError:
    ProblemDetails = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from .helpers.bill_of_materials import BillOfMaterials
    from .helpers.customers import Customers
    from .helpers.forecasting import Forecasting
    from .helpers.inventory import Inventory
    from .helpers.locations import Locations
    from .helpers.order_plan import OrderPlan
    from .helpers.products import Products
    from .helpers.purchase_orders import PurchaseOrders
    from .helpers.purchase_orders_v2 import PurchaseOrdersV2
    from .helpers.sales_orders import SalesOrders
    from .helpers.suppliers import Suppliers


def _find_null_fields(data: Any, path: str = "") -> list[str]:
    """
    Recursively find all null fields in a JSON response.

    Args:
        data: The JSON data to inspect (dict, list, or primitive)
        path: The current path in dot notation (e.g., "order.supplier.name")

    Returns:
        List of paths to null fields (e.g., ["orderDate", "supplier.supplierName"])
    """
    null_fields: list[str] = []

    if data is None and path:
        # Found a null field (but not the root - that's handled separately)
        return [path]

    if isinstance(data, dict):
        for key, value in data.items():
            field_path = f"{path}.{key}" if path else key
            null_fields.extend(_find_null_fields(value, field_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            field_path = f"{path}[{i}]" if path else f"[{i}]"
            null_fields.extend(_find_null_fields(item, field_path))

    return null_fields


class IdempotentOnlyRetry(Retry):
    """
    Custom Retry class that only retries idempotent methods (GET, HEAD, OPTIONS, TRACE)
    on server errors (5xx status codes).

    StockTrim doesn't have rate limiting (429), so we only need to handle 5xx errors
    and we only retry idempotent methods to avoid duplicate operations.
    """

    # Idempotent methods that are always safe to retry
    IDEMPOTENT_METHODS = frozenset(["HEAD", "GET", "OPTIONS", "TRACE"])

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize and track the current request method."""
        super().__init__(*args, **kwargs)
        self._current_method: str | None = None

    def is_retryable_method(self, method: str) -> bool:
        """
        Allow all methods to pass through the initial check.

        Store the method for later use in is_retryable_status_code.
        """
        self._current_method = method.upper()
        # Accept all methods - we'll filter in is_retryable_status_code
        return self._current_method in self.allowed_methods

    def is_retryable_status_code(self, status_code: int) -> bool:
        """
        Check if a status code is retryable for the current method.

        For 5xx errors, only allow idempotent methods.
        """
        # First check if the status code is in the allowed list at all
        if status_code not in self.status_forcelist:
            return False

        # If we don't know the method, fall back to default behavior
        if self._current_method is None:
            return True

        # Server errors (5xx) - only retry idempotent methods
        return self._current_method in self.IDEMPOTENT_METHODS

    def increment(self) -> "IdempotentOnlyRetry":
        """Return a new retry instance with the attempt count incremented."""
        # Call parent's increment which creates a new instance of our class
        new_retry = cast(IdempotentOnlyRetry, super().increment())
        # Preserve the current method across retry attempts
        new_retry._current_method = self._current_method
        return new_retry


class ErrorLoggingTransport(AsyncHTTPTransport):
    """
    Transport layer that adds comprehensive logging for all HTTP requests and responses.

    This transport wraps another AsyncHTTPTransport and intercepts responses to log:
    - DEBUG: Request details (sanitized headers), response bodies for 2xx responses
    - INFO: Successful 2xx responses with timing
    - WARNING: Null responses that may cause TypeErrors
    - ERROR: 4xx client errors and 5xx server errors with response details
    """

    #: Maximum characters to show from response bodies in DEBUG logs
    RESPONSE_BODY_MAX_LENGTH = 200
    MAX_NULL_FIELDS_TO_LOG = 20

    def __init__(
        self,
        wrapped_transport: AsyncHTTPTransport | None = None,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the error logging transport.

        Args:
            wrapped_transport: The transport to wrap. If None, creates a new AsyncHTTPTransport.
            logger: Logger instance for capturing error details. If None, creates a default logger.
            **kwargs: Additional arguments passed to AsyncHTTPTransport if wrapped_transport is None.
        """
        super().__init__()
        if wrapped_transport is None:
            wrapped_transport = AsyncHTTPTransport(**kwargs)
        self._wrapped_transport = wrapped_transport
        self.logger = logger or logging.getLogger(__name__)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle request and log based on response status code."""
        # Log request details at DEBUG level
        await self._log_request(request)

        # Track timing
        start_time = time.time()
        response = await self._wrapped_transport.handle_async_request(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log based on status code
        if 200 <= response.status_code < 300:
            await self._log_success_response(response, request, duration_ms)
        elif 400 <= response.status_code < 500:
            await self._log_client_error(response, request, duration_ms)
        elif 500 <= response.status_code < 600:
            await self._log_server_error(response, request, duration_ms)
        else:
            # Unexpected status codes (1xx, 3xx redirects shouldn't reach here)
            self.logger.warning(
                f"{request.method} {request.url} -> {response.status_code} "
                f"({duration_ms:.0f}ms)"
            )

        return response

    async def _log_request(self, request: httpx.Request) -> None:
        """Log request details at DEBUG level with sanitized headers."""
        if not self.logger.isEnabledFor(logging.DEBUG):
            return

        # Sanitize headers (remove auth headers)
        safe_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in {"authorization", "api-auth-id", "api-auth-signature"}
        }

        self.logger.debug(
            f"Request: {request.method} {request.url}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "headers": safe_headers,
            },
        )

    async def _log_success_response(
        self, response: httpx.Response, request: httpx.Request, duration_ms: float
    ) -> None:
        """Log successful response at INFO level with DEBUG details."""
        method = request.method
        url = str(request.url)
        status_code = response.status_code

        # INFO level: just status and timing
        self.logger.info(f"{method} {url} -> {status_code} ({duration_ms:.0f}ms)")

        # DEBUG level: include response body excerpt
        if self.logger.isEnabledFor(logging.DEBUG):
            # Read response content if it's streaming
            if hasattr(response, "aread"):
                with contextlib.suppress(TypeError, AttributeError):
                    await response.aread()

            try:
                response_body = response.json()
                body_type = type(response_body).__name__

                if response_body is None:
                    self.logger.debug("Response body: null (JSON null)")
                elif isinstance(response_body, list):
                    self.logger.debug(
                        f"Response body: list[{len(response_body)}] items"
                    )
                elif isinstance(response_body, dict):
                    body_str = str(response_body)
                    body_excerpt = body_str[: self.RESPONSE_BODY_MAX_LENGTH]
                    ellipsis = (
                        "..." if len(body_str) > self.RESPONSE_BODY_MAX_LENGTH else ""
                    )
                    self.logger.debug(f"Response body: {body_excerpt}{ellipsis}")
                else:
                    self.logger.debug(
                        f"Response body type: {body_type}, value: {str(response_body)[: self.RESPONSE_BODY_MAX_LENGTH]}"
                    )
            except (json.JSONDecodeError, TypeError, ValueError):
                body_excerpt = response.text[: self.RESPONSE_BODY_MAX_LENGTH]
                ellipsis = (
                    "..." if len(response.text) > self.RESPONSE_BODY_MAX_LENGTH else ""
                )
                self.logger.debug(f"Response body (non-JSON): {body_excerpt}{ellipsis}")

    async def _log_client_error(
        self, response: httpx.Response, request: httpx.Request, duration_ms: float
    ) -> None:
        """
        Log detailed information for 400-level client errors.

        Tries to parse as ProblemDetails if available, otherwise logs raw error.
        """
        method = request.method
        url = str(request.url)
        status_code = response.status_code

        # Read response content if it's streaming
        if hasattr(response, "aread"):
            with contextlib.suppress(TypeError, AttributeError):
                await response.aread()

        try:
            error_data = response.json()
        except (json.JSONDecodeError, TypeError, ValueError):
            response_text = getattr(response, "text", "")
            text_excerpt = response_text[:500]
            ellipsis = "..." if len(response_text) > 500 else ""
            self.logger.error(
                f"Client error {status_code} for {method} {url} ({duration_ms:.0f}ms) - "
                f"Response: {text_excerpt}{ellipsis}"
            )
            return

        # Try to parse as ProblemDetails if the model is available
        if ProblemDetails is not None:
            try:
                problem = ProblemDetails.from_dict(error_data)
                self._log_problem_details(
                    problem, method, url, status_code, duration_ms
                )
                return
            except (TypeError, ValueError, AttributeError) as e:
                self.logger.debug(
                    f"Failed to parse as ProblemDetails: {type(e).__name__}: {e}"
                )

        # Fallback: log raw error data
        self.logger.error(
            f"Client error {status_code} for {method} {url} ({duration_ms:.0f}ms) - "
            f"Error: {error_data}"
        )

    async def _log_server_error(
        self, response: httpx.Response, request: httpx.Request, duration_ms: float
    ) -> None:
        """Log detailed information for 500-level server errors."""
        method = request.method
        url = str(request.url)
        status_code = response.status_code

        # Read response content if it's streaming
        if hasattr(response, "aread"):
            with contextlib.suppress(TypeError, AttributeError):
                await response.aread()

        try:
            error_data = response.json()
            self.logger.error(
                f"Server error {status_code} for {method} {url} ({duration_ms:.0f}ms) - "
                f"Response: {error_data}"
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            response_text = getattr(response, "text", "")
            text_excerpt = response_text[:500]
            ellipsis = "..." if len(response_text) > 500 else ""
            self.logger.error(
                f"Server error {status_code} for {method} {url} ({duration_ms:.0f}ms) - "
                f"Response: {text_excerpt}{ellipsis}"
            )

    def _log_problem_details(
        self,
        problem: Any,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Log errors using the ProblemDetails model."""
        log_message = (
            f"Client error {status_code} for {method} {url} ({duration_ms:.0f}ms)"
        )

        # Check for Unset values before logging
        title = problem.title if not isinstance(problem.title, Unset) else None
        detail = problem.detail if not isinstance(problem.detail, Unset) else None
        type_ = problem.type_ if not isinstance(problem.type_, Unset) else None
        instance = problem.instance if not isinstance(problem.instance, Unset) else None

        if title:
            log_message += f"\n  Title: {title}"
        if detail:
            log_message += f"\n  Detail: {detail}"
        if type_:
            log_message += f"\n  Type: {type_}"
        if instance:
            log_message += f"\n  Instance: {instance}"

        # Log any additional properties
        if hasattr(problem, "additional_properties") and problem.additional_properties:
            formatted = ", ".join(
                f"{k}: {v!r}" for k, v in problem.additional_properties.items()
            )
            log_message += f"\n  Additional info: {formatted}"

        self.logger.error(log_message)

    def log_parsing_error(
        self,
        error: TypeError | ValueError | AttributeError | Exception,
        response: httpx.Response,
        request: httpx.Request,
    ) -> None:
        """
        Log detailed information when an error occurs during response parsing.

        This method intelligently inspects the error and response to provide
        actionable debugging information with fix suggestions:
        - For TypeErrors: Shows null fields and provides 3 fix options with doc links
        - For ValueErrors: Shows the error and response excerpt
        - For any parsing error: Logs the raw response for inspection

        Args:
            error: The exception that occurred during parsing
            response: The HTTP response that was being parsed
            request: The original HTTP request

        Example output for TypeError with null fields:
            ERROR: TypeError during parsing for GET /api/V2/PurchaseOrders
            ERROR: TypeError: object of type 'NoneType' has no len()
            ERROR: Found 3 null field(s) in response:
            ERROR:   - orderDate
            ERROR:   - fullyReceivedDate
            ERROR:   - supplier.supplierName
            ERROR:
            ERROR: Possible fixes:
            ERROR:   1. Add fields to NULLABLE_FIELDS in scripts/regenerate_client.py and regenerate
            ERROR:   2. Update OpenAPI spec to mark these fields as 'nullable: true'
            ERROR:   3. Handle null values defensively in helper methods
            ERROR:
            ERROR: See: docs/contributing/api-feedback.md#nullable-date-fields-not-marked-in-spec

        Example output for ValueError:
            ERROR: ValueError during parsing for POST /api/Products
            ERROR: ValueError: invalid literal for int() with base 10: 'abc'
            ERROR: Response excerpt: {"id": "abc", "name": "Product 1"}
        """
        method = request.method
        url = str(request.url)
        error_type = type(error).__name__

        self.logger.error(f"{error_type} during parsing for {method} {url}")
        self.logger.error(f"{error_type}: {error}")

        # Try to parse response and provide context
        try:
            response_data = response.json()

            # For TypeErrors, check for null fields (common cause)
            if isinstance(error, TypeError):
                null_fields = _find_null_fields(response_data)

                if null_fields:
                    self.logger.error(
                        f"Found {len(null_fields)} null field(s) in response:"
                    )
                    for field_path in null_fields[: self.MAX_NULL_FIELDS_TO_LOG]:
                        self.logger.error(f"  - {field_path}")
                    if len(null_fields) > self.MAX_NULL_FIELDS_TO_LOG:
                        self.logger.error(
                            f"  ... and {len(null_fields) - self.MAX_NULL_FIELDS_TO_LOG} more null fields"
                        )

                    # Provide actionable fix suggestions
                    self.logger.error("")  # Blank line for readability
                    self.logger.error("Possible fixes:")
                    self.logger.error(
                        "  1. Add fields to NULLABLE_FIELDS in scripts/regenerate_client.py and regenerate"
                    )
                    self.logger.error(
                        "  2. Update OpenAPI spec to mark these fields as 'nullable: true'"
                    )
                    self.logger.error(
                        "  3. Handle null values defensively in helper methods"
                    )
                    self.logger.error("")  # Blank line for readability
                    self.logger.error(
                        "See: docs/contributing/api-feedback.md#nullable-arrays-vs-optional-fields"
                    )
                else:
                    # TypeError but no null fields - show response excerpt
                    response_str = str(response_data)
                    excerpt = response_str[: self.RESPONSE_BODY_MAX_LENGTH]
                    ellipsis = (
                        "..."
                        if len(response_str) > self.RESPONSE_BODY_MAX_LENGTH
                        else ""
                    )
                    self.logger.error(
                        f"No null fields found. Response excerpt: {excerpt}{ellipsis}"
                    )
            else:
                # For other errors, show response excerpt
                response_str = str(response_data)
                excerpt = response_str[: self.RESPONSE_BODY_MAX_LENGTH]
                ellipsis = (
                    "..." if len(response_str) > self.RESPONSE_BODY_MAX_LENGTH else ""
                )
                self.logger.error(f"Response excerpt: {excerpt}{ellipsis}")

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            self.logger.error(
                f"Could not parse response as JSON: {type(e).__name__}: {e}"
            )
            text_excerpt = response.text[: self.RESPONSE_BODY_MAX_LENGTH]
            ellipsis = (
                "..." if len(response.text) > self.RESPONSE_BODY_MAX_LENGTH else ""
            )
            self.logger.error(f"Response text: {text_excerpt}{ellipsis}")


class AuthHeaderTransport(AsyncHTTPTransport):
    """
    Transport layer that adds the StockTrim api-auth-signature header.

    StockTrim uses custom headers (api-auth-id, api-auth-signature) instead of
    Bearer token authentication. The api-auth-id header is set by the parent
    AuthenticatedClient using its native auth_header_name customization, while
    this transport adds the api-auth-signature header.
    """

    def __init__(
        self,
        api_auth_signature: str,
        wrapped_transport: AsyncHTTPTransport | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the auth header transport.

        Args:
            api_auth_signature: StockTrim API authentication signature
            wrapped_transport: The transport to wrap. If None, creates a new AsyncHTTPTransport.
            **kwargs: Additional arguments passed to AsyncHTTPTransport if wrapped_transport is None.
        """
        super().__init__()
        if wrapped_transport is None:
            wrapped_transport = AsyncHTTPTransport(**kwargs)
        self._wrapped_transport = wrapped_transport
        self.api_auth_signature = api_auth_signature

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Add StockTrim api-auth-signature header to the request."""
        request.headers["api-auth-signature"] = self.api_auth_signature
        return await self._wrapped_transport.handle_async_request(request)


def create_resilient_transport(
    api_auth_signature: str,
    max_retries: int = 5,
    logger: logging.Logger | None = None,
    **kwargs: Any,
) -> tuple[RetryTransport, ErrorLoggingTransport]:
    """
    Factory function that creates a chained transport with auth, error logging, and retry capabilities.

    This function chains multiple transport layers:
    1. AsyncHTTPTransport (base HTTP transport)
    2. AuthHeaderTransport (adds StockTrim api-auth-signature header)
    3. ErrorLoggingTransport (logs detailed 4xx errors)
    4. RetryTransport (handles retries for 5xx errors on idempotent methods only)

    Note: The api-auth-id header is set by the parent AuthenticatedClient using
    its native auth_header_name customization. This transport only adds the
    api-auth-signature header.

    Args:
        api_auth_signature: StockTrim API authentication signature
        max_retries: Maximum number of retry attempts for failed requests. Defaults to 5.
        logger: Logger instance for capturing operations. If None, creates a default logger.
        **kwargs: Additional arguments passed to the base AsyncHTTPTransport.
            Common parameters include:
            - http2 (bool): Enable HTTP/2 support
            - limits (httpx.Limits): Connection pool limits
            - verify (bool | str | ssl.SSLContext): SSL certificate verification
            - cert (str | tuple): Client-side certificates
            - trust_env (bool): Trust environment variables for proxy configuration

    Returns:
        A tuple of (RetryTransport, ErrorLoggingTransport) where:
        - RetryTransport: The outermost transport layer for making requests
        - ErrorLoggingTransport: Reference to the logging layer for error handling

    Note:
        StockTrim API simplifications compared to other APIs:
        - No rate limiting (429) handling - StockTrim doesn't rate limit
        - No pagination transport - StockTrim doesn't use pagination
        - Only retries 5xx errors on idempotent methods (GET, HEAD, OPTIONS, TRACE)

    Example:
        ```python
        transport = create_resilient_transport(
            api_auth_signature="your-signature",
            max_retries=3,
        )
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.get(
                "https://api.stocktrim.com/api/Products"
            )
        ```
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Build the transport chain from inside out:
    # 1. Base AsyncHTTPTransport
    base_transport = AsyncHTTPTransport(**kwargs)

    # 2. Wrap with StockTrim api-auth-signature header
    # Note: api-auth-id is handled by AuthenticatedClient's native mechanism
    auth_transport = AuthHeaderTransport(
        api_auth_signature=api_auth_signature,
        wrapped_transport=base_transport,
    )

    # 3. Wrap with error logging
    error_logging_transport = ErrorLoggingTransport(
        wrapped_transport=auth_transport,
        logger=logger,
    )

    # 4. Finally wrap with retry logic (outermost layer)
    # Use IdempotentOnlyRetry which only retries idempotent methods for 5xx errors
    retry = IdempotentOnlyRetry(
        total=max_retries,
        backoff_factor=1.0,  # Exponential backoff: 1, 2, 4, 8, 16 seconds
        respect_retry_after_header=True,  # Honor server's Retry-After header if present
        status_forcelist=[502, 503, 504],  # Only 5xx server errors (no 429)
        allowed_methods=[
            "HEAD",
            "GET",
            "OPTIONS",
            "TRACE",
            "POST",
            "PATCH",
            "PUT",
            "DELETE",
        ],  # Accept all, filter in is_retryable_status_code
    )
    retry_transport = RetryTransport(
        transport=error_logging_transport,
        retry=retry,
    )

    return retry_transport, error_logging_transport


class StockTrimClient(AuthenticatedClient):
    """
    The pythonic StockTrim API client with automatic resilience.

    This client inherits from AuthenticatedClient and can be passed directly to
    generated API methods without needing a .client property.

    Features:
    - Automatic retries on server errors (5xx) for idempotent methods only
    - Custom header authentication (api-auth-id, api-auth-signature)
    - Rich error logging and observability
    - Minimal configuration - just works out of the box

    Simplifications vs other APIs:
    - No rate limiting handling - StockTrim doesn't rate limit
    - No automatic pagination - StockTrim API doesn't paginate
    - Only retries idempotent methods (GET, HEAD, OPTIONS, TRACE) on 5xx errors

    Usage:
        # Basic usage with environment variables
        async with StockTrimClient() as client:
            from stocktrim_public_api_client.api.products import get_api_products

            response = await get_api_products.asyncio_detailed(
                client=client  # Pass client directly - no .client needed!
            )

        # With explicit credentials
        async with StockTrimClient(
            api_auth_id="your-id",
            api_auth_signature="your-signature"
        ) as client:
            # All API calls through client get automatic resilience
            response = await some_api_method.asyncio_detailed(client=client)
    """

    def __init__(
        self,
        api_auth_id: str | None = None,
        api_auth_signature: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 5,
        logger: logging.Logger | None = None,
        **httpx_kwargs: Any,
    ):
        """
        Initialize the StockTrim API client with automatic resilience features.

        Args:
            api_auth_id: StockTrim API authentication ID. If None, will try to load from
                STOCKTRIM_API_AUTH_ID env var.
            api_auth_signature: StockTrim API authentication signature. If None, will try to
                load from STOCKTRIM_API_AUTH_SIGNATURE env var.
            base_url: Base URL for the StockTrim API. Defaults to https://api.stocktrim.com
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of retry attempts for failed requests. Defaults to 5.
            logger: Logger instance for capturing client operations. If None, creates a default logger.
            **httpx_kwargs: Additional arguments passed to the base AsyncHTTPTransport.
                Common parameters include:
                - http2 (bool): Enable HTTP/2 support
                - limits (httpx.Limits): Connection pool limits
                - verify (bool | str | ssl.SSLContext): SSL certificate verification
                - cert (str | tuple): Client-side certificates
                - trust_env (bool): Trust environment variables for proxy configuration
                - event_hooks (dict): Custom event hooks (will be merged with built-in hooks)

        Raises:
            ValueError: If no API credentials are provided and environment variables are not set.

        Note:
            Transport-related parameters (http2, limits, verify, etc.) are correctly
            passed to the innermost AsyncHTTPTransport layer, ensuring they take effect
            even with the layered transport architecture.

        Example:
            >>> async with StockTrimClient() as client:
            ...     # All API calls through client get automatic resilience
            ...     response = await some_api_method.asyncio_detailed(client=client)
        """
        load_dotenv()

        # Setup credentials
        api_auth_id = api_auth_id or os.getenv("STOCKTRIM_API_AUTH_ID")
        api_auth_signature = api_auth_signature or os.getenv(
            "STOCKTRIM_API_AUTH_SIGNATURE"
        )
        base_url = (
            base_url or os.getenv("STOCKTRIM_BASE_URL") or "https://api.stocktrim.com"
        )

        if not api_auth_id or not api_auth_signature:
            raise ValueError(
                "API credentials required (STOCKTRIM_API_AUTH_ID and "
                "STOCKTRIM_API_AUTH_SIGNATURE env vars or api_auth_id and "
                "api_auth_signature params)"
            )

        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries

        # Extract client-level parameters that shouldn't go to the transport
        # Event hooks for observability - start with our defaults
        event_hooks: dict[str, list[Callable[[httpx.Response], Awaitable[None]]]] = {
            "response": [
                self._log_response_metrics,
            ]
        }

        # Extract and merge user hooks
        user_hooks = httpx_kwargs.pop("event_hooks", {})
        for event, hooks in user_hooks.items():
            # Normalize to list and add to existing or create new event
            hook_list = cast(
                list[Callable[[httpx.Response], Awaitable[None]]],
                hooks if isinstance(hooks, list) else [hooks],
            )
            if event in event_hooks:
                event_hooks[event].extend(hook_list)
            else:
                event_hooks[event] = hook_list

        # Create resilient transport with all the layers
        # Note: This transport only adds the api-auth-signature header.
        # The api-auth-id header is added by AuthenticatedClient's native mechanism.
        transport, error_logging_transport = create_resilient_transport(
            api_auth_signature=api_auth_signature,
            max_retries=max_retries,
            logger=self.logger,
            **httpx_kwargs,  # Pass through http2, limits, verify, etc.
        )

        # Store reference to error logging transport for helper methods
        # Public API for helper methods to use enhanced error logging
        self.error_logging_transport = error_logging_transport

        # Initialize parent with resilient transport
        # Use AuthenticatedClient's native customization to add the api-auth-id header:
        # - token: the API auth ID value
        # - auth_header_name: "api-auth-id" (StockTrim's custom header name)
        # - prefix: "" (no prefix like "Bearer")
        super().__init__(
            base_url=base_url,
            token=api_auth_id,  # Use the auth ID as the token value
            auth_header_name="api-auth-id",  # StockTrim's custom header name
            prefix="",  # No prefix (disables "Bearer ")
            timeout=httpx.Timeout(timeout),
            httpx_args={
                "transport": transport,
                "event_hooks": event_hooks,
            },
        )

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self._base_url

    # Domain helper properties (lazy-loaded)
    @property
    def products(self) -> "Products":
        """Access the Products helper for product catalog operations."""
        if not hasattr(self, "_products"):
            from .helpers.products import Products

            self._products = Products(self)
        return self._products

    @property
    def customers(self) -> "Customers":
        """Access the Customers helper for customer management."""
        if not hasattr(self, "_customers"):
            from .helpers.customers import Customers

            self._customers = Customers(self)
        return self._customers

    @property
    def suppliers(self) -> "Suppliers":
        """Access the Suppliers helper for supplier management."""
        if not hasattr(self, "_suppliers"):
            from .helpers.suppliers import Suppliers

            self._suppliers = Suppliers(self)
        return self._suppliers

    @property
    def sales_orders(self) -> "SalesOrders":
        """Access the SalesOrders helper for sales order management."""
        if not hasattr(self, "_sales_orders"):
            from .helpers.sales_orders import SalesOrders

            self._sales_orders = SalesOrders(self)
        return self._sales_orders

    @property
    def purchase_orders(self) -> "PurchaseOrders":
        """Access the PurchaseOrders helper for purchase order management."""
        if not hasattr(self, "_purchase_orders"):
            from .helpers.purchase_orders import PurchaseOrders

            self._purchase_orders = PurchaseOrders(self)
        return self._purchase_orders

    @property
    def inventory(self) -> "Inventory":
        """Access the Inventory helper for inventory management."""
        if not hasattr(self, "_inventory"):
            from .helpers.inventory import Inventory

            self._inventory = Inventory(self)
        return self._inventory

    @property
    def locations(self) -> "Locations":
        """Access the Locations helper for location management."""
        if not hasattr(self, "_locations"):
            from .helpers.locations import Locations

            self._locations = Locations(self)
        return self._locations

    @property
    def order_plan(self) -> "OrderPlan":
        """Access the OrderPlan helper for forecast and demand planning operations."""
        if not hasattr(self, "_order_plan"):
            from .helpers.order_plan import OrderPlan

            self._order_plan = OrderPlan(self)
        return self._order_plan

    @property
    def purchase_orders_v2(self) -> "PurchaseOrdersV2":
        """Access the PurchaseOrdersV2 helper for V2 purchase order operations (recommended over V1)."""
        if not hasattr(self, "_purchase_orders_v2"):
            from .helpers.purchase_orders_v2 import PurchaseOrdersV2

            self._purchase_orders_v2 = PurchaseOrdersV2(self)
        return self._purchase_orders_v2

    @property
    def forecasting(self) -> "Forecasting":
        """Access the Forecasting helper for forecast management and processing status."""
        if not hasattr(self, "_forecasting"):
            from .helpers.forecasting import Forecasting

            self._forecasting = Forecasting(self)
        return self._forecasting

    @property
    def bill_of_materials(self) -> "BillOfMaterials":
        """Access the BillOfMaterials helper for BOM management."""
        if not hasattr(self, "_bill_of_materials"):
            from .helpers.bill_of_materials import BillOfMaterials

            self._bill_of_materials = BillOfMaterials(self)
        return self._bill_of_materials

    async def _log_response_metrics(self, response: httpx.Response) -> None:
        """Log response metrics for observability."""
        request = response.request
        try:
            elapsed_ms = response.elapsed.total_seconds() * 1000
            self.logger.debug(
                f"{request.method} {request.url} -> {response.status_code} "
                f"({elapsed_ms:.0f}ms)"
            )
        except RuntimeError:
            # elapsed is only available after response is read/closed
            self.logger.debug(
                f"{request.method} {request.url} -> {response.status_code}"
            )

    async def __aenter__(self) -> "StockTrimClient":
        """Enter async context manager, returning self for proper type checking."""
        await super().__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        await super().__aexit__(*args)

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"StockTrimClient(base_url='{self._base_url}', "
            f"max_retries={self.max_retries})"
        )


__all__ = [
    "AuthHeaderTransport",
    "ErrorLoggingTransport",
    "IdempotentOnlyRetry",
    "StockTrimClient",
    "create_resilient_transport",
]
