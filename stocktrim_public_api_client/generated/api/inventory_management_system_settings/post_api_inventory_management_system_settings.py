from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import Response
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.inventory_management_system_request import (
    InventoryManagementSystemRequest,
)
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    *,
    body: InventoryManagementSystemRequest
    | InventoryManagementSystemRequest
    | InventoryManagementSystemRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/InventoryManagementSystemSettings",
    }

    if isinstance(body, InventoryManagementSystemRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, InventoryManagementSystemRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, InventoryManagementSystemRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | None:
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201

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
    body: InventoryManagementSystemRequest
    | InventoryManagementSystemRequest
    | InventoryManagementSystemRequest,
) -> Response[Any | ProblemDetails]:
    """
    Args:
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: InventoryManagementSystemRequest
    | InventoryManagementSystemRequest
    | InventoryManagementSystemRequest,
) -> Any | ProblemDetails | None:
    """
    Args:
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: InventoryManagementSystemRequest
    | InventoryManagementSystemRequest
    | InventoryManagementSystemRequest,
) -> Response[Any | ProblemDetails]:
    """
    Args:
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: InventoryManagementSystemRequest
    | InventoryManagementSystemRequest
    | InventoryManagementSystemRequest,
) -> Any | ProblemDetails | None:
    """
    Args:
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):
        body (InventoryManagementSystemRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
