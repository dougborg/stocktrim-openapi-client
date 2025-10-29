from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.inventory_management_system_response import (
    InventoryManagementSystemResponse,
)
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    configuration_name: str,
    *,
    api_auth_id: str,
    api_auth_signature: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["api-auth-id"] = api_auth_id

    headers["api-auth-signature"] = api_auth_signature

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/Configuration/{configuration_name}",
    }

    _kwargs["headers"] = headers
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
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Any | InventoryManagementSystemResponse | ProblemDetails]:
    """
    Args:
        configuration_name (str):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | InventoryManagementSystemResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        configuration_name=configuration_name,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
    api_auth_id: str,
    api_auth_signature: str,
) -> Any | InventoryManagementSystemResponse | ProblemDetails | None:
    """
    Args:
        configuration_name (str):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | InventoryManagementSystemResponse | ProblemDetails
    """

    return sync_detailed(
        configuration_name=configuration_name,
        client=client,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    ).parsed


async def asyncio_detailed(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Any | InventoryManagementSystemResponse | ProblemDetails]:
    """
    Args:
        configuration_name (str):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | InventoryManagementSystemResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        configuration_name=configuration_name,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    configuration_name: str,
    *,
    client: AuthenticatedClient | Client,
    api_auth_id: str,
    api_auth_signature: str,
) -> Any | InventoryManagementSystemResponse | ProblemDetails | None:
    """
    Args:
        configuration_name (str):
        api_auth_id (str):
        api_auth_signature (str):

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
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
        )
    ).parsed
