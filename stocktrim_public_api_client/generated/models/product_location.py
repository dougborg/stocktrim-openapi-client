from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductLocation")


@_attrs_define
class ProductLocation:
    """
    Attributes:
        location_code (str):
        location_name (Union[None, Unset, str]):
        stock_on_hand (Union[None, Unset, float]):
        stock_on_order (Union[None, Unset, float]):
    """

    location_code: str
    location_name: Union[None, Unset, str] = UNSET
    stock_on_hand: Union[None, Unset, float] = UNSET
    stock_on_order: Union[None, Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        location_code = self.location_code

        location_name: Union[None, Unset, str]
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        stock_on_hand: Union[None, Unset, float]
        if isinstance(self.stock_on_hand, Unset):
            stock_on_hand = UNSET
        else:
            stock_on_hand = self.stock_on_hand

        stock_on_order: Union[None, Unset, float]
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

        def _parse_location_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        def _parse_stock_on_hand(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        stock_on_hand = _parse_stock_on_hand(d.pop("stockOnHand", UNSET))

        def _parse_stock_on_order(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        stock_on_order = _parse_stock_on_order(d.pop("stockOnOrder", UNSET))

        product_location = cls(
            location_code=location_code,
            location_name=location_name,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
        )

        return product_location
