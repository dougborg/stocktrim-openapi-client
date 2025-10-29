from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset
from ..models.api_enum import ApiEnum

T = TypeVar("T", bound="InventoryManagementSystemRequest")


@_attrs_define
class InventoryManagementSystemRequest:
    """
    Attributes:
        api (ApiEnum | Unset):
    """

    api: ApiEnum | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        api: str | Unset = UNSET
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
        api: ApiEnum | Unset
        if isinstance(_api, Unset):
            api = UNSET
        else:
            api = ApiEnum(_api)

        inventory_management_system_request = cls(
            api=api,
        )

        return inventory_management_system_request
