from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.sales_order_request_dto import SalesOrderRequestDto
from ...models.sales_order_response_dto import SalesOrderResponseDto
from ...types import Response


def _get_kwargs(
    *,
    body: Union[
        SalesOrderRequestDto,
        SalesOrderRequestDto,
        SalesOrderRequestDto,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["api-auth-id"] = api_auth_id

    headers["api-auth-signature"] = api_auth_signature

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/SalesOrders",
    }

    if isinstance(body, SalesOrderRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, SalesOrderRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, SalesOrderRequestDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    if response.status_code == 201:
        response_201 = SalesOrderResponseDto.from_dict(response.json())

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
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        SalesOrderRequestDto,
        SalesOrderRequestDto,
        SalesOrderRequestDto,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProblemDetails, SalesOrderResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        SalesOrderRequestDto,
        SalesOrderRequestDto,
        SalesOrderRequestDto,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProblemDetails, SalesOrderResponseDto]
    """

    return sync_detailed(
        client=client,
        body=body,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        SalesOrderRequestDto,
        SalesOrderRequestDto,
        SalesOrderRequestDto,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProblemDetails, SalesOrderResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        SalesOrderRequestDto,
        SalesOrderRequestDto,
        SalesOrderRequestDto,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, ProblemDetails, SalesOrderResponseDto]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):
        body (SalesOrderRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProblemDetails, SalesOrderResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
        )
    ).parsed
