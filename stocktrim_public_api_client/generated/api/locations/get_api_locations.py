from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import UNSET, Response, Unset
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.location_response_dto import LocationResponseDto
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    *,
    code: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["code"] = code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/Locations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | LocationResponseDto | ProblemDetails | None:
    if response.status_code == 200:
        response_200 = LocationResponseDto.from_dict(response.json())

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
) -> Response[Any | LocationResponseDto | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
) -> Response[Any | LocationResponseDto | ProblemDetails]:
    """
    Args:
        code (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LocationResponseDto | ProblemDetails]
    """

    kwargs = _get_kwargs(
        code=code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
) -> Any | LocationResponseDto | ProblemDetails | None:
    """
    Args:
        code (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LocationResponseDto | ProblemDetails
    """

    return sync_detailed(
        client=client,
        code=code,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
) -> Response[Any | LocationResponseDto | ProblemDetails]:
    """
    Args:
        code (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LocationResponseDto | ProblemDetails]
    """

    kwargs = _get_kwargs(
        code=code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
) -> Any | LocationResponseDto | ProblemDetails | None:
    """
    Args:
        code (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LocationResponseDto | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            code=code,
        )
    ).parsed
