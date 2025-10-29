from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.bill_of_materials_response_dto import BillOfMaterialsResponseDto
from ...models.problem_details import ProblemDetails


def _get_kwargs(
    *,
    product_id: str | Unset = UNSET,
    component_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["productId"] = product_id

    params["componentId"] = component_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/boms",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | BillOfMaterialsResponseDto | ProblemDetails | None:
    if response.status_code == 201:
        response_201 = BillOfMaterialsResponseDto.from_dict(response.json())

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
) -> Response[Any | BillOfMaterialsResponseDto | ProblemDetails]:
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
    component_id: str | Unset = UNSET,
) -> Response[Any | BillOfMaterialsResponseDto | ProblemDetails]:
    """
    Args:
        product_id (str | Unset):
        component_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BillOfMaterialsResponseDto | ProblemDetails]
    """

    kwargs = _get_kwargs(
        product_id=product_id,
        component_id=component_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    component_id: str | Unset = UNSET,
) -> Any | BillOfMaterialsResponseDto | ProblemDetails | None:
    """
    Args:
        product_id (str | Unset):
        component_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BillOfMaterialsResponseDto | ProblemDetails
    """

    return sync_detailed(
        client=client,
        product_id=product_id,
        component_id=component_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    component_id: str | Unset = UNSET,
) -> Response[Any | BillOfMaterialsResponseDto | ProblemDetails]:
    """
    Args:
        product_id (str | Unset):
        component_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BillOfMaterialsResponseDto | ProblemDetails]
    """

    kwargs = _get_kwargs(
        product_id=product_id,
        component_id=component_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    product_id: str | Unset = UNSET,
    component_id: str | Unset = UNSET,
) -> Any | BillOfMaterialsResponseDto | ProblemDetails | None:
    """
    Args:
        product_id (str | Unset):
        component_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BillOfMaterialsResponseDto | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            product_id=product_id,
            component_id=component_id,
        )
    ).parsed
