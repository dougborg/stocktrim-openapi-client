"""Utility functions for working with StockTrim API responses.

This module provides convenient helpers for unwrapping API responses,
handling errors, and status checking.
"""

from http import HTTPStatus
from typing import TYPE_CHECKING, TypeVar, overload

from .client_types import UNSET, Response, Unset

if TYPE_CHECKING:
    from .generated.models.problem_details import ProblemDetails

T = TypeVar("T")
D = TypeVar("D")


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        problem_details: "ProblemDetails | None" = None,
    ):
        """Initialize API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            problem_details: The ProblemDetails object from the API (if available)
        """
        super().__init__(message)
        self.status_code = status_code
        self.problem_details = problem_details


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""

    pass


class PermissionError(APIError):
    """Raised when permission is denied (403)."""

    pass


class NotFoundError(APIError):
    """Raised when resource is not found (404)."""

    pass


class ValidationError(APIError):
    """Raised when request validation fails (400, 422)."""

    pass


class ServerError(APIError):
    """Raised when server error occurs (5xx)."""

    pass


@overload
def unwrap(
    response: Response[T],
    *,
    raise_on_error: bool = True,
) -> T: ...


@overload
def unwrap(
    response: Response[T],
    *,
    raise_on_error: bool = False,
) -> T | None: ...


def unwrap(
    response: Response[T],
    *,
    raise_on_error: bool = True,
) -> T | None:
    """Unwrap a Response object and return the parsed data or raise an error.

    This is the main utility function for handling API responses. It automatically
    raises appropriate exceptions for error responses and returns the parsed data
    for successful responses.

    Args:
        response: The Response object from an API call
        raise_on_error: If True, raise exceptions on error status codes.
                        If False, return None on errors.

    Returns:
        The parsed response data, or None if raise_on_error=False and an error occurred

    Raises:
        AuthenticationError: When status is 401
        PermissionError: When status is 403
        NotFoundError: When status is 404
        ValidationError: When status is 400 or 422
        ServerError: When status is 5xx
        APIError: For other error status codes

    Example:
        ```python
        from stocktrim_public_api_client import StockTrimClient
        from stocktrim_public_api_client.api.products import get_api_products
        from stocktrim_public_api_client.utils import unwrap

        async with StockTrimClient() as client:
            response = await get_api_products.asyncio_detailed(client=client)
            products = unwrap(response)  # Raises on error, returns parsed data
        ```
    """
    # Identify ProblemDetails (if the body parsed into one) for richer messages
    problem_details = None
    try:
        from .generated.models.problem_details import ProblemDetails

        if isinstance(response.parsed, ProblemDetails):
            problem_details = response.parsed
    except ImportError:
        pass

    # Handle error status codes first — even when the body did not parse
    # (e.g. StockTrim returns 500 with an HTML stack trace that the OpenAPI
    # client cannot decode). Without this branch every 5xx without a parseable
    # body would surface as the misleading "No parsed response data" APIError.
    if response.status_code >= 400:
        if not raise_on_error:
            return None

        # Extract error message from ProblemDetails if available
        if problem_details:
            title = unwrap_unset(problem_details.title)
            detail = unwrap_unset(problem_details.detail)
            message = (
                f"{title}: {detail}"
                if title and detail
                else (title or detail or "Unknown error")
            )
        else:
            message = f"API error with status {response.status_code}"

        # Raise specific exception based on status code
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise AuthenticationError(message, response.status_code, problem_details)
        elif response.status_code == HTTPStatus.FORBIDDEN:
            raise PermissionError(message, response.status_code, problem_details)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(message, response.status_code, problem_details)
        elif response.status_code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ):
            raise ValidationError(message, response.status_code, problem_details)
        elif 500 <= response.status_code < 600:
            raise ServerError(message, response.status_code, problem_details)
        else:
            raise APIError(message, response.status_code, problem_details)

    # Successful status but no parsed body — likely a generator gap
    if response.parsed is None:
        if raise_on_error:
            raise APIError(
                f"No parsed response data for status {response.status_code}",
                response.status_code,
            )
        return None

    return response.parsed


def is_success(response: Response[T]) -> bool:
    """Check if a response indicates success (2xx status code).

    Args:
        response: The Response object to check

    Returns:
        True if status code is 2xx, False otherwise

    Example:
        ```python
        response = await some_api_call.asyncio_detailed(client=client)
        if is_success(response):
            data = response.parsed
        ```
    """
    return 200 <= response.status_code < 300


def is_error(response: Response[T]) -> bool:
    """Check if a response indicates an error (4xx or 5xx status code).

    Args:
        response: The Response object to check

    Returns:
        True if status code is 4xx or 5xx, False otherwise

    Example:
        ```python
        response = await some_api_call.asyncio_detailed(client=client)
        if is_error(response):
            print(f"Error: {response.status_code}")
        ```
    """
    return response.status_code >= 400


@overload
def unwrap_unset(value: T | Unset | None) -> T | None: ...


@overload
def unwrap_unset(value: T | Unset | None, default: D) -> T | D: ...


def unwrap_unset(value: T | Unset | None, default: D | None = None) -> T | D | None:
    """Unwrap an UNSET (or None) sentinel value.

    The OpenAPI-generated client uses ``UNSET`` to distinguish "field not provided"
    from "field explicitly set to None". Both sentinels are normalised to ``default``
    here so call sites can treat absence uniformly.

    With no ``default`` the return type is ``T | None``; with a default the return
    type widens to ``T | D``, where ``D`` may differ from ``T`` (e.g. an ``int |
    Unset`` value with a ``float('inf')`` default for use as a sort key).

    Args:
        value: Value that might be ``UNSET`` or ``None``
        default: Value to return when ``value`` is ``UNSET`` or ``None``

    Returns:
        The unwrapped value, or ``default`` if value is ``UNSET`` or ``None``.

    Example:
        ```python
        from stocktrim_public_api_client.client_types import UNSET
        from stocktrim_public_api_client.utils import unwrap_unset

        unwrap_unset(42)  # 42
        unwrap_unset(UNSET)  # None
        unwrap_unset(UNSET, 0)  # 0
        unwrap_unset(None, "n/a")  # "n/a"
        unwrap_unset(UNSET, float("inf"))  # inf — default may differ from T
        ```
    """
    if value is None or isinstance(value, Unset):
        return default
    return value


def to_unset(value: T | None) -> T | Unset:
    """Convert ``None`` to the ``UNSET`` sentinel value.

    Useful when building generated request models from optional Pydantic fields,
    where ``None`` means "not provided" and should be sent as ``UNSET`` to avoid
    overwriting existing server-side values.

    Args:
        value: Value that might be ``None``

    Returns:
        The value unchanged if not ``None``, or ``UNSET`` if ``None``.

    Example:
        ```python
        from stocktrim_public_api_client.utils import to_unset

        to_unset(42)  # 42
        to_unset(None)  # UNSET
        ```
    """
    return UNSET if value is None else value


def get_error_message(response: Response[T]) -> str | None:
    """Extract error message from a response.

    Args:
        response: The Response object to extract error from

    Returns:
        Error message string, or None if no error or message couldn't be extracted

    Example:
        ```python
        response = await some_api_call.asyncio_detailed(client=client)
        if is_error(response):
            message = get_error_message(response)
            print(f"Error: {message}")
        ```
    """
    if not is_error(response):
        return None

    # Try to extract from ProblemDetails
    try:
        from .generated.models.problem_details import ProblemDetails

        if isinstance(response.parsed, ProblemDetails):
            problem = response.parsed
            title = unwrap_unset(problem.title)
            detail = unwrap_unset(problem.detail)
            return f"{title}: {detail}" if title and detail else (title or detail)
    except ImportError:
        pass

    # Fallback to status code
    return f"HTTP {response.status_code}"


__all__ = [
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "PermissionError",
    "ServerError",
    "ValidationError",
    "get_error_message",
    "is_error",
    "is_success",
    "to_unset",
    "unwrap",
    "unwrap_unset",
]
