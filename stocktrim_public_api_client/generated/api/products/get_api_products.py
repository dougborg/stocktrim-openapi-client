from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.products_response_dto import ProductsResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    code: Union[Unset, str] = UNSET,
    page_no: Union[Unset, str] = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["api-auth-id"] = api_auth_id

    headers["api-auth-signature"] = api_auth_signature

    params: dict[str, Any] = {}

    params["code"] = code

    params["pageNo"] = page_no

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/Products",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProductsResponseDto.from_dict(response_200_item_data)

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
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    page_no: Union[Unset, str] = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    """
    Args:
        code (Union[Unset, str]):
        page_no (Union[Unset, str]):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProblemDetails, list['ProductsResponseDto']]]
    """

    kwargs = _get_kwargs(
        code=code,
        page_no=page_no,
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
    code: Union[Unset, str] = UNSET,
    page_no: Union[Unset, str] = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    """
    Args:
        code (Union[Unset, str]):
        page_no (Union[Unset, str]):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProblemDetails, list['ProductsResponseDto']]
    """

    return sync_detailed(
        client=client,
        code=code,
        page_no=page_no,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    page_no: Union[Unset, str] = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    """
    Args:
        code (Union[Unset, str]):
        page_no (Union[Unset, str]):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ProblemDetails, list['ProductsResponseDto']]]
    """

    kwargs = _get_kwargs(
        code=code,
        page_no=page_no,
        api_auth_id=api_auth_id,
        api_auth_signature=api_auth_signature,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    page_no: Union[Unset, str] = UNSET,
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, ProblemDetails, list["ProductsResponseDto"]]]:
    """
    Args:
        code (Union[Unset, str]):
        page_no (Union[Unset, str]):
        api_auth_id (str):
        api_auth_signature (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ProblemDetails, list['ProductsResponseDto']]
    """

    return (
        await asyncio_detailed(
            client=client,
            code=code,
            page_no=page_no,
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
        )
    ).parsed
