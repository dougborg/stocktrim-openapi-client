from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.square_web_hook_object import SquareWebHookObject


T = TypeVar("T", bound="SquareWebHookData")


@_attrs_define
class SquareWebHookData:
    """
    Attributes:
        type_ (None | str | Unset):
        id (None | str | Unset):
        object_ (SquareWebHookObject | Unset):
    """

    type_: None | str | Unset = UNSET
    id: None | str | Unset = UNSET
    object_: SquareWebHookObject | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_: None | str | Unset
        if isinstance(self.type_, Unset):
            type_ = UNSET
        else:
            type_ = self.type_

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        object_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if id is not UNSET:
            field_dict["id"] = id
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.square_web_hook_object import SquareWebHookObject

        d = dict(src_dict)

        def _parse_type_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        type_ = _parse_type_(d.pop("type", UNSET))

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        _object_ = d.pop("object", UNSET)
        object_: SquareWebHookObject | Unset
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = SquareWebHookObject.from_dict(_object_)

        square_web_hook_data = cls(
            type_=type_,
            id=id,
            object_=object_,
        )

        return square_web_hook_data
