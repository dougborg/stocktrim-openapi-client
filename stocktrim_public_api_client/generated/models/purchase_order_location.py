from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="PurchaseOrderLocation")


@_attrs_define
class PurchaseOrderLocation:
    """
    Attributes:
        location_code (None | str | Unset):
        location_name (None | str | Unset):
    """

    location_code: None | str | Unset = UNSET
    location_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        location_code: None | str | Unset
        if isinstance(self.location_code, Unset):
            location_code = UNSET
        else:
            location_code = self.location_code

        location_name: None | str | Unset
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if location_code is not UNSET:
            field_dict["locationCode"] = location_code
        if location_name is not UNSET:
            field_dict["locationName"] = location_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_location_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_code = _parse_location_code(d.pop("locationCode", UNSET))

        def _parse_location_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        purchase_order_location = cls(
            location_code=location_code,
            location_name=location_name,
        )

        return purchase_order_location
