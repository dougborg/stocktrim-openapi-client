import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SquareWebHookOrderUpdatedData")


@_attrs_define
class SquareWebHookOrderUpdatedData:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]):
        location_id (Union[None, Unset, str]):
        order_id (Union[None, Unset, str]):
        state (Union[None, Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
        version (Union[Unset, int]):
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[None, Unset, str] = UNSET
    order_id: Union[None, Unset, str] = UNSET
    state: Union[None, Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    version: Union[Unset, int] = UNSET

    def to_dict(self) -> dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        location_id: Union[None, Unset, str]
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        order_id: Union[None, Unset, str]
        if isinstance(self.order_id, Unset):
            order_id = UNSET
        else:
            order_id = self.order_id

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        version = self.version

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if location_id is not UNSET:
            field_dict["location_id"] = location_id
        if order_id is not UNSET:
            field_dict["order_id"] = order_id
        if state is not UNSET:
            field_dict["state"] = state
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_location_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_id = _parse_location_id(d.pop("location_id", UNSET))

        def _parse_order_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        order_id = _parse_order_id(d.pop("order_id", UNSET))

        def _parse_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state = _parse_state(d.pop("state", UNSET))

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        version = d.pop("version", UNSET)

        square_web_hook_order_updated_data = cls(
            created_at=created_at,
            location_id=location_id,
            order_id=order_id,
            state=state,
            updated_at=updated_at,
            version=version,
        )

        return square_web_hook_order_updated_data
