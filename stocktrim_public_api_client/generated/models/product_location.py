from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="ProductLocation")


@_attrs_define
class ProductLocation:
    """
    Attributes:
        location_code (str):
        location_name (None | str | Unset):
        stock_on_hand (float | None | Unset):
        stock_on_order (float | None | Unset):
    """

    location_code: str
    location_name: None | str | Unset = UNSET
    stock_on_hand: float | None | Unset = UNSET
    stock_on_order: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        location_code = self.location_code

        location_name: None | str | Unset
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        stock_on_hand: float | None | Unset
        if isinstance(self.stock_on_hand, Unset):
            stock_on_hand = UNSET
        else:
            stock_on_hand = self.stock_on_hand

        stock_on_order: float | None | Unset
        if isinstance(self.stock_on_order, Unset):
            stock_on_order = UNSET
        else:
            stock_on_order = self.stock_on_order

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "locationCode": location_code,
            }
        )
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if stock_on_hand is not UNSET:
            field_dict["stockOnHand"] = stock_on_hand
        if stock_on_order is not UNSET:
            field_dict["stockOnOrder"] = stock_on_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        location_code = d.pop("locationCode")

        def _parse_location_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        def _parse_stock_on_hand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stock_on_hand = _parse_stock_on_hand(d.pop("stockOnHand", UNSET))

        def _parse_stock_on_order(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stock_on_order = _parse_stock_on_order(d.pop("stockOnOrder", UNSET))

        product_location = cls(
            location_code=location_code,
            location_name=location_name,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
        )

        return product_location
