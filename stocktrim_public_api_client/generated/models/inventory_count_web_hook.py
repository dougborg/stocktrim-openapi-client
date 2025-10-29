from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="InventoryCountWebHook")


@_attrs_define
class InventoryCountWebHook:
    """
    Attributes:
        calculated_at (datetime.datetime | Unset):
        catalog_object_id (None | str | Unset):
        catalog_object_type (None | str | Unset):
        location_id (None | str | Unset):
        quantity (float | Unset):
        state (None | str | Unset):
    """

    calculated_at: datetime.datetime | Unset = UNSET
    catalog_object_id: None | str | Unset = UNSET
    catalog_object_type: None | str | Unset = UNSET
    location_id: None | str | Unset = UNSET
    quantity: float | Unset = UNSET
    state: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        calculated_at: str | Unset = UNSET
        if not isinstance(self.calculated_at, Unset):
            calculated_at = self.calculated_at.isoformat()

        catalog_object_id: None | str | Unset
        if isinstance(self.catalog_object_id, Unset):
            catalog_object_id = UNSET
        else:
            catalog_object_id = self.catalog_object_id

        catalog_object_type: None | str | Unset
        if isinstance(self.catalog_object_type, Unset):
            catalog_object_type = UNSET
        else:
            catalog_object_type = self.catalog_object_type

        location_id: None | str | Unset
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        quantity = self.quantity

        state: None | str | Unset
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
        calculated_at: datetime.datetime | Unset
        if isinstance(_calculated_at, Unset):
            calculated_at = UNSET
        else:
            calculated_at = isoparse(_calculated_at)

        def _parse_catalog_object_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        catalog_object_id = _parse_catalog_object_id(d.pop("catalog_object_id", UNSET))

        def _parse_catalog_object_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        catalog_object_type = _parse_catalog_object_type(
            d.pop("catalog_object_type", UNSET)
        )

        def _parse_location_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_id = _parse_location_id(d.pop("location_id", UNSET))

        quantity = d.pop("quantity", UNSET)

        def _parse_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

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
