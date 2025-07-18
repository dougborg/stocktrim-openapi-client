from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.square_web_hook_object import SquareWebHookObject


T = TypeVar("T", bound="SquareWebHookData")


@_attrs_define
class SquareWebHookData:
    """
    Attributes:
        type_ (Union[None, Unset, str]):
        id (Union[None, Unset, str]):
        object_ (Union[Unset, SquareWebHookObject]):
    """

    type_: Union[None, Unset, str] = UNSET
    id: Union[None, Unset, str] = UNSET
    object_: Union[Unset, "SquareWebHookObject"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_: Union[None, Unset, str]
        if isinstance(self.type_, Unset):
            type_ = UNSET
        else:
            type_ = self.type_

        id: Union[None, Unset, str]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        object_: Union[Unset, dict[str, Any]] = UNSET
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

        def _parse_type_(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type_ = _parse_type_(d.pop("type", UNSET))

        def _parse_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        id = _parse_id(d.pop("id", UNSET))

        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, SquareWebHookObject]
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
