from http import HTTPStatus
from typing import Any, cast

import httpx

from ....client_types import Response
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.order_plan_filter_criteria_dto import OrderPlanFilterCriteriaDto
from ...models.problem_details import ProblemDetails
from ...models.purchase_order_response_dto import PurchaseOrderResponseDto


def _get_kwargs(
    *,
    body: OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/V2/PurchaseOrders/OrderPlan",
    }

    if isinstance(body, OrderPlanFilterCriteriaDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, OrderPlanFilterCriteriaDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, OrderPlanFilterCriteriaDto):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
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
    body: OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto,
) -> Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]:
    """Generate purchase orders based on the filters passed in. Same as how the StockTrim Order plan screen
    works

    Args:
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]
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
    body: OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto,
) -> Any | ProblemDetails | list[PurchaseOrderResponseDto] | None:
    """Generate purchase orders based on the filters passed in. Same as how the StockTrim Order plan screen
    works

    Args:
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[PurchaseOrderResponseDto]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto,
) -> Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]:
    """Generate purchase orders based on the filters passed in. Same as how the StockTrim Order plan screen
    works

    Args:
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[PurchaseOrderResponseDto]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto
    | OrderPlanFilterCriteriaDto,
) -> Any | ProblemDetails | list[PurchaseOrderResponseDto] | None:
    """Generate purchase orders based on the filters passed in. Same as how the StockTrim Order plan screen
    works

    Args:
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):
        body (OrderPlanFilterCriteriaDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[PurchaseOrderResponseDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
