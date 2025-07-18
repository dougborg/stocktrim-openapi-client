import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.square_web_hook_data import SquareWebHookData


T = TypeVar("T", bound="SquareWebHook")


@_attrs_define
class SquareWebHook:
    """
    Attributes:
        merchant_id (Union[None, Unset, str]):
        type_ (Union[None, Unset, str]):
        event_id (Union[None, Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
        data (Union[Unset, SquareWebHookData]):
    """

    merchant_id: Union[None, Unset, str] = UNSET
    type_: Union[None, Unset, str] = UNSET
    event_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    data: Union[Unset, "SquareWebHookData"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        merchant_id: Union[None, Unset, str]
        if isinstance(self.merchant_id, Unset):
            merchant_id = UNSET
        else:
            merchant_id = self.merchant_id

        type_: Union[None, Unset, str]
        if isinstance(self.type_, Unset):
            type_ = UNSET
        else:
            type_ = self.type_

        event_id: Union[None, Unset, str]
        if isinstance(self.event_id, Unset):
            event_id = UNSET
        else:
            event_id = self.event_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if merchant_id is not UNSET:
            field_dict["merchant_id"] = merchant_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if event_id is not UNSET:
            field_dict["event_id"] = event_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.square_web_hook_data import SquareWebHookData

        d = dict(src_dict)

        def _parse_merchant_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        merchant_id = _parse_merchant_id(d.pop("merchant_id", UNSET))

        def _parse_type_(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type_ = _parse_type_(d.pop("type", UNSET))

        def _parse_event_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        event_id = _parse_event_id(d.pop("event_id", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _data = d.pop("data", UNSET)
        data: Union[Unset, SquareWebHookData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = SquareWebHookData.from_dict(_data)

        square_web_hook = cls(
            merchant_id=merchant_id,
            type_=type_,
            event_id=event_id,
            created_at=created_at,
            data=data,
        )

        return square_web_hook
