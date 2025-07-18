import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PurchaseOrderLineItem")


@_attrs_define
class PurchaseOrderLineItem:
    """
    Attributes:
        product_id (str):
        quantity (float):
        received_date (Union[None, Unset, datetime.datetime]):
        unit_price (Union[None, Unset, float]):
    """

    product_id: str
    quantity: float
    received_date: Union[None, Unset, datetime.datetime] = UNSET
    unit_price: Union[None, Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        quantity = self.quantity

        received_date: Union[None, Unset, str]
        if isinstance(self.received_date, Unset):
            received_date = UNSET
        elif isinstance(self.received_date, datetime.datetime):
            received_date = self.received_date.isoformat()
        else:
            received_date = self.received_date

        unit_price: Union[None, Unset, float]
        if isinstance(self.unit_price, Unset):
            unit_price = UNSET
        else:
            unit_price = self.unit_price

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "productId": product_id,
                "quantity": quantity,
            }
        )
        if received_date is not UNSET:
            field_dict["receivedDate"] = received_date
        if unit_price is not UNSET:
            field_dict["unitPrice"] = unit_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        product_id = d.pop("productId")

        quantity = d.pop("quantity")

        def _parse_received_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                received_date_type_0 = isoparse(data)

                return received_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        received_date = _parse_received_date(d.pop("receivedDate", UNSET))

        def _parse_unit_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        unit_price = _parse_unit_price(d.pop("unitPrice", UNSET))

        purchase_order_line_item = cls(
            product_id=product_id,
            quantity=quantity,
            received_date=received_date,
            unit_price=unit_price,
        )

        return purchase_order_line_item
