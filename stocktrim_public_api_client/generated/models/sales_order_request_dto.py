import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SalesOrderRequestDto")


@_attrs_define
class SalesOrderRequestDto:
    """
    Attributes:
        product_id (str):
        order_date (datetime.datetime):
        quantity (float):
        external_reference_id (Union[None, Unset, str]):
        unit_price (Union[None, Unset, float]):
        location_code (Union[None, Unset, str]):
        location_name (Union[None, Unset, str]):
        customer_code (Union[None, Unset, str]):
        customer_name (Union[None, Unset, str]):
    """

    product_id: str
    order_date: datetime.datetime
    quantity: float
    external_reference_id: Union[None, Unset, str] = UNSET
    unit_price: Union[None, Unset, float] = UNSET
    location_code: Union[None, Unset, str] = UNSET
    location_name: Union[None, Unset, str] = UNSET
    customer_code: Union[None, Unset, str] = UNSET
    customer_name: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        order_date = self.order_date.isoformat()

        quantity = self.quantity

        external_reference_id: Union[None, Unset, str]
        if isinstance(self.external_reference_id, Unset):
            external_reference_id = UNSET
        else:
            external_reference_id = self.external_reference_id

        unit_price: Union[None, Unset, float]
        if isinstance(self.unit_price, Unset):
            unit_price = UNSET
        else:
            unit_price = self.unit_price

        location_code: Union[None, Unset, str]
        if isinstance(self.location_code, Unset):
            location_code = UNSET
        else:
            location_code = self.location_code

        location_name: Union[None, Unset, str]
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        customer_code: Union[None, Unset, str]
        if isinstance(self.customer_code, Unset):
            customer_code = UNSET
        else:
            customer_code = self.customer_code

        customer_name: Union[None, Unset, str]
        if isinstance(self.customer_name, Unset):
            customer_name = UNSET
        else:
            customer_name = self.customer_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "productId": product_id,
                "orderDate": order_date,
                "quantity": quantity,
            }
        )
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if unit_price is not UNSET:
            field_dict["unitPrice"] = unit_price
        if location_code is not UNSET:
            field_dict["locationCode"] = location_code
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if customer_code is not UNSET:
            field_dict["customerCode"] = customer_code
        if customer_name is not UNSET:
            field_dict["customerName"] = customer_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        product_id = d.pop("productId")

        order_date = isoparse(d.pop("orderDate"))

        quantity = d.pop("quantity")

        def _parse_external_reference_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_reference_id = _parse_external_reference_id(d.pop("externalReferenceId", UNSET))

        def _parse_unit_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        unit_price = _parse_unit_price(d.pop("unitPrice", UNSET))

        def _parse_location_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_code = _parse_location_code(d.pop("locationCode", UNSET))

        def _parse_location_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        def _parse_customer_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer_code = _parse_customer_code(d.pop("customerCode", UNSET))

        def _parse_customer_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer_name = _parse_customer_name(d.pop("customerName", UNSET))

        sales_order_request_dto = cls(
            product_id=product_id,
            order_date=order_date,
            quantity=quantity,
            external_reference_id=external_reference_id,
            unit_price=unit_price,
            location_code=location_code,
            location_name=location_name,
            customer_code=customer_code,
            customer_name=customer_name,
        )

        return sales_order_request_dto
