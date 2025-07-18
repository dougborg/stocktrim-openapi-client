from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Inventory")


@_attrs_define
class Inventory:
    """
    Attributes:
        product_id (Union[None, Unset, str]):
        location_code (Union[None, Unset, str]):
        location_name (Union[None, Unset, str]):
        stock_on_hand (Union[Unset, float]):
        stock_on_order (Union[Unset, float]):
    """

    product_id: Union[None, Unset, str] = UNSET
    location_code: Union[None, Unset, str] = UNSET
    location_name: Union[None, Unset, str] = UNSET
    stock_on_hand: Union[Unset, float] = UNSET
    stock_on_order: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id: Union[None, Unset, str]
        if isinstance(self.product_id, Unset):
            product_id = UNSET
        else:
            product_id = self.product_id

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

        stock_on_hand = self.stock_on_hand

        stock_on_order = self.stock_on_order

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if product_id is not UNSET:
            field_dict["productId"] = product_id
        if location_code is not UNSET:
            field_dict["locationCode"] = location_code
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

        def _parse_product_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        product_id = _parse_product_id(d.pop("productId", UNSET))

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

        stock_on_hand = d.pop("stockOnHand", UNSET)

        stock_on_order = d.pop("stockOnOrder", UNSET)

        inventory = cls(
            product_id=product_id,
            location_code=location_code,
            location_name=location_name,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
        )

        return inventory
