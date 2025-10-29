from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import Response
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.supplier_request_dto import SupplierRequestDto
from ...models.supplier_response_dto import SupplierResponseDto


def _get_kwargs(
    *,
    body: list[SupplierRequestDto]
    | list[SupplierRequestDto]
    | list[SupplierRequestDto],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/Suppliers",
    }

    if isinstance(body, list[SupplierRequestDto]):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _kwargs["json"].append(body_item)

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, list[SupplierRequestDto]):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _kwargs["json"].append(body_item)

        headers["Content-Type"] = "application/json"
    if isinstance(body, list[SupplierRequestDto]):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _kwargs["json"].append(body_item)

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | list[SupplierResponseDto] | None:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = SupplierResponseDto.from_dict(response_201_item_data)

            response_201.append(response_201_item)

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
) -> Response[Any | ProblemDetails | list[SupplierResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[SupplierRequestDto]
    | list[SupplierRequestDto]
    | list[SupplierRequestDto],
) -> Response[Any | ProblemDetails | list[SupplierResponseDto]]:
    """
    Args:
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[SupplierResponseDto]]
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
    body: list[SupplierRequestDto]
    | list[SupplierRequestDto]
    | list[SupplierRequestDto],
) -> Any | ProblemDetails | list[SupplierResponseDto] | None:
    """
    Args:
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[SupplierResponseDto]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[SupplierRequestDto]
    | list[SupplierRequestDto]
    | list[SupplierRequestDto],
) -> Response[Any | ProblemDetails | list[SupplierResponseDto]]:
    """
    Args:
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[SupplierResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: list[SupplierRequestDto]
    | list[SupplierRequestDto]
    | list[SupplierRequestDto],
) -> Any | ProblemDetails | list[SupplierResponseDto] | None:
    """
    Args:
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):
        body (list[SupplierRequestDto]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[SupplierResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
