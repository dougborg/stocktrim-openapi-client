from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import UNSET, Response, Unset
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.purchase_order_response_dto import PurchaseOrderResponseDto
from ...models.purchase_order_status_dto import PurchaseOrderStatusDto


def _get_kwargs(
    *,
    page: int | Unset = 0,
    page_size: int | Unset = 10,
    status: PurchaseOrderStatusDto | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["pageSize"] = page_size

    json_status: int | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/V2/PurchaseOrders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | list[PurchaseOrderResponseDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PurchaseOrderResponseDto.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

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
) -> Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 0,
    page_size: int | Unset = 10,
    status: PurchaseOrderStatusDto | Unset = UNSET,
) -> Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]:
    """Get all purchase orders

    Args:
        page (int | Unset):  Default: 0.
        page_size (int | Unset):  Default: 10.
        status (PurchaseOrderStatusDto | Unset): Purchase order status (0=Draft, 1=Approved,
            2=Sent, 3=Received)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 0,
    page_size: int | Unset = 10,
    status: PurchaseOrderStatusDto | Unset = UNSET,
) -> Any | ProblemDetails | list[PurchaseOrderResponseDto] | None:
    """Get all purchase orders

    Args:
        page (int | Unset):  Default: 0.
        page_size (int | Unset):  Default: 10.
        status (PurchaseOrderStatusDto | Unset): Purchase order status (0=Draft, 1=Approved,
            2=Sent, 3=Received)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[PurchaseOrderResponseDto]
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 0,
    page_size: int | Unset = 10,
    status: PurchaseOrderStatusDto | Unset = UNSET,
) -> Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]:
    """Get all purchase orders

    Args:
        page (int | Unset):  Default: 0.
        page_size (int | Unset):  Default: 10.
        status (PurchaseOrderStatusDto | Unset): Purchase order status (0=Draft, 1=Approved,
            2=Sent, 3=Received)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 0,
    page_size: int | Unset = 10,
    status: PurchaseOrderStatusDto | Unset = UNSET,
) -> Any | ProblemDetails | list[PurchaseOrderResponseDto] | None:
    """Get all purchase orders

    Args:
        page (int | Unset):  Default: 0.
        page_size (int | Unset):  Default: 10.
        status (PurchaseOrderStatusDto | Unset): Purchase order status (0=Draft, 1=Approved,
            2=Sent, 3=Received)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[PurchaseOrderResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            status=status,
        )
    ).parsed
