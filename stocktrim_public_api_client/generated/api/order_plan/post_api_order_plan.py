from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.order_plan_filter_criteria import OrderPlanFilterCriteria
from ...models.order_plan_results_dto import OrderPlanResultsDto
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    *,
    body: Union[
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["api-auth-id"] = api_auth_id

    headers["api-auth-signature"] = api_auth_signature

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/OrderPlan",
    }

    if isinstance(body, OrderPlanFilterCriteria):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json-patch+json"
    if isinstance(body, OrderPlanFilterCriteria):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, OrderPlanFilterCriteria):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/*+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
    if response.status_code == 200:
        response_200 = OrderPlanResultsDto.from_dict(response.json())

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
) -> Response[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
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
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, OrderPlanResultsDto, ProblemDetails]]
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
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, OrderPlanResultsDto, ProblemDetails]
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
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Response[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, OrderPlanResultsDto, ProblemDetails]]
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
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
        OrderPlanFilterCriteria,
    ],
    api_auth_id: str,
    api_auth_signature: str,
) -> Optional[Union[Any, OrderPlanResultsDto, ProblemDetails]]:
    """
    Args:
        api_auth_id (str):
        api_auth_signature (str):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):
        body (OrderPlanFilterCriteria):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, OrderPlanResultsDto, ProblemDetails]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            api_auth_id=api_auth_id,
            api_auth_signature=api_auth_signature,
        )
    ).parsed
