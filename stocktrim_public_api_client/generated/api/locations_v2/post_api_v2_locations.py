from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import Response
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.location_request_dto import LocationRequestDto
from ...models.location_response_dto import LocationResponseDto
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    *,
    body: LocationRequestDto | LocationRequestDto | LocationRequestDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/V2/Locations",
    }

    if isinstance(body, LocationRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, LocationRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, LocationRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | LocationResponseDto | ProblemDetails | None:
    if response.status_code == 201:
        response_201 = LocationResponseDto.from_dict(response.json())

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
    body: LocationRequestDto | LocationRequestDto | LocationRequestDto,
) -> Response[Any | LocationResponseDto | ProblemDetails]:
    """Creates or Updates a location using Code as the unique identifier

    Args:
        body (LocationRequestDto):
        body (LocationRequestDto):
        body (LocationRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LocationResponseDto | ProblemDetails]
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
    body: LocationRequestDto | LocationRequestDto | LocationRequestDto,
) -> Any | LocationResponseDto | ProblemDetails | None:
    """Creates or Updates a location using Code as the unique identifier

    Args:
        body (LocationRequestDto):
        body (LocationRequestDto):
        body (LocationRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LocationResponseDto | ProblemDetails
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LocationRequestDto | LocationRequestDto | LocationRequestDto,
) -> Response[Any | LocationResponseDto | ProblemDetails]:
    """Creates or Updates a location using Code as the unique identifier

    Args:
        body (LocationRequestDto):
        body (LocationRequestDto):
        body (LocationRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LocationResponseDto | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: LocationRequestDto | LocationRequestDto | LocationRequestDto,
) -> Any | LocationResponseDto | ProblemDetails | None:
    """Creates or Updates a location using Code as the unique identifier

    Args:
        body (LocationRequestDto):
        body (LocationRequestDto):
        body (LocationRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LocationResponseDto | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
