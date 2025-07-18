import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="InventoryCountWebHook")


@_attrs_define
class InventoryCountWebHook:
    """
    Attributes:
        calculated_at (Union[Unset, datetime.datetime]):
        catalog_object_id (Union[None, Unset, str]):
        catalog_object_type (Union[None, Unset, str]):
        location_id (Union[None, Unset, str]):
        quantity (Union[Unset, float]):
        state (Union[None, Unset, str]):
    """

    calculated_at: Union[Unset, datetime.datetime] = UNSET
    catalog_object_id: Union[None, Unset, str] = UNSET
    catalog_object_type: Union[None, Unset, str] = UNSET
    location_id: Union[None, Unset, str] = UNSET
    quantity: Union[Unset, float] = UNSET
    state: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        calculated_at: Union[Unset, str] = UNSET
        if not isinstance(self.calculated_at, Unset):
            calculated_at = self.calculated_at.isoformat()

        catalog_object_id: Union[None, Unset, str]
        if isinstance(self.catalog_object_id, Unset):
            catalog_object_id = UNSET
        else:
            catalog_object_id = self.catalog_object_id

        catalog_object_type: Union[None, Unset, str]
        if isinstance(self.catalog_object_type, Unset):
            catalog_object_type = UNSET
        else:
            catalog_object_type = self.catalog_object_type

        location_id: Union[None, Unset, str]
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        quantity = self.quantity

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if calculated_at is not UNSET:
            field_dict["calculated_at"] = calculated_at
        if catalog_object_id is not UNSET:
            field_dict["catalog_object_id"] = catalog_object_id
        if catalog_object_type is not UNSET:
            field_dict["catalog_object_type"] = catalog_object_type
        if location_id is not UNSET:
            field_dict["location_id"] = location_id
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _calculated_at = d.pop("calculated_at", UNSET)
        calculated_at: Union[Unset, datetime.datetime]
        if isinstance(_calculated_at, Unset):
            calculated_at = UNSET
        else:
            calculated_at = isoparse(_calculated_at)

        def _parse_catalog_object_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        catalog_object_id = _parse_catalog_object_id(d.pop("catalog_object_id", UNSET))

        def _parse_catalog_object_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        catalog_object_type = _parse_catalog_object_type(d.pop("catalog_object_type", UNSET))

        def _parse_location_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_id = _parse_location_id(d.pop("location_id", UNSET))

        quantity = d.pop("quantity", UNSET)

        def _parse_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state = _parse_state(d.pop("state", UNSET))

        inventory_count_web_hook = cls(
            calculated_at=calculated_at,
            catalog_object_id=catalog_object_id,
            catalog_object_type=catalog_object_type,
            location_id=location_id,
            quantity=quantity,
            state=state,
        )

        return inventory_count_web_hook
