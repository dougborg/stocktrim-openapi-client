from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.api_enum import ApiEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="InventoryManagementSystemRequest")


@_attrs_define
class InventoryManagementSystemRequest:
    """
    Attributes:
        api (Union[Unset, ApiEnum]):
    """

    api: Union[Unset, ApiEnum] = UNSET

    def to_dict(self) -> dict[str, Any]:
        api: Union[Unset, str] = UNSET
        if not isinstance(self.api, Unset):
            api = self.api.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if api is not UNSET:
            field_dict["api"] = api

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _api = d.pop("api", UNSET)
        api: Union[Unset, ApiEnum]
        if isinstance(_api, Unset):
            api = UNSET
        else:
            api = ApiEnum(_api)

        inventory_management_system_request = cls(
            api=api,
        )

        return inventory_management_system_request
