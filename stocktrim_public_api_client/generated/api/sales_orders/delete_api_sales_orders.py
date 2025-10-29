from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    *,
    product_id: str | Unset = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["api-auth-id"] = api_auth_id

    headers["api-auth-signature"] = api_auth_signature

    params: dict[str, Any] = {}

    params["productId"] = product_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/SalesOrders",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Any | ProblemDetails]:
    """
    Args:
        product_id (str | Unset):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        product_id=product_id,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Any | ProblemDetails | None:
    """
    Args:
        product_id (str | Unset):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return sync_detailed(
        client=client,
        product_id=product_id,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Any | ProblemDetails]:
    """
    Args:
        product_id (str | Unset):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        product_id=product_id,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Any | ProblemDetails | None:
    """
    Args:
        product_id (str | Unset):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            product_id=product_id,
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
        )
    ).parsed
