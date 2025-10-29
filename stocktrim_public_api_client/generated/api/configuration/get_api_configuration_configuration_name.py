from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import Response
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.inventory_management_system_response import (
    InventoryManagementSystemResponse,
)
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    configuration_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/Configuration/{configuration_name}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | InventoryManagementSystemResponse | ProblemDetails | None:
    if response.status_code == 200:
        response_200 = InventoryManagementSystemResponse.from_dict(response.json())

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
) -> Response[Any | InventoryManagementSystemResponse | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | InventoryManagementSystemResponse | ProblemDetails]:
    """
    Args:
        configuration_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | InventoryManagementSystemResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        configuration_name=configuration_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | InventoryManagementSystemResponse | ProblemDetails | None:
    """
    Args:
        configuration_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | InventoryManagementSystemResponse | ProblemDetails
    """

    return sync_detailed(
        configuration_name=configuration_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | InventoryManagementSystemResponse | ProblemDetails]:
    """
    Args:
        configuration_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | InventoryManagementSystemResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        configuration_name=configuration_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | InventoryManagementSystemResponse | ProblemDetails | None:
    """
    Args:
        configuration_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | InventoryManagementSystemResponse | ProblemDetails
    """

    return (
        await asyncio_detailed(
            configuration_name=configuration_name,
            client=client,
        )
    ).parsed
