from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="LocationResponseDto")


@_attrs_define
class LocationResponseDto:
    """
    Attributes:
        location_code (str):
        id (int | Unset):
        location_name (None | str | Unset):
        external_id (None | str | Unset):
    """

    location_code: str
    id: int | Unset = UNSET
    location_name: None | str | Unset = UNSET
    external_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        location_code = self.location_code

        id = self.id

        location_name: None | str | Unset
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        external_id: None | str | Unset
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "locationCode": location_code,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if external_id is not UNSET:
            field_dict["externalId"] = external_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        location_code = d.pop("locationCode")

        id = d.pop("id", UNSET)

        def _parse_location_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        def _parse_external_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        location_response_dto = cls(
            location_code=location_code,
            id=id,
            location_name=location_name,
            external_id=external_id,
        )

        return location_response_dto
