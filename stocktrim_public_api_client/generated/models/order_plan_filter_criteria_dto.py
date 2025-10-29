from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset
from ..models.current_status_enum import CurrentStatusEnum

T = TypeVar("T", bound="OrderPlanFilterCriteriaDto")


@_attrs_define
class OrderPlanFilterCriteriaDto:
    """
    Attributes:
        search_string (None | str | Unset):
        current_status (CurrentStatusEnum | Unset):
        location_codes (list[str] | None | Unset):
        supplier_codes (list[str] | None | Unset):
    """

    search_string: None | str | Unset = UNSET
    current_status: CurrentStatusEnum | Unset = UNSET
    location_codes: list[str] | None | Unset = UNSET
    supplier_codes: list[str] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        search_string: None | str | Unset
        if isinstance(self.search_string, Unset):
            search_string = UNSET
        else:
            search_string = self.search_string

        current_status: str | Unset = UNSET
        if not isinstance(self.current_status, Unset):
            current_status = self.current_status.value

        location_codes: list[str] | None | Unset
        if isinstance(self.location_codes, Unset):
            location_codes = UNSET
        elif isinstance(self.location_codes, list):
            location_codes = self.location_codes

        else:
            location_codes = self.location_codes

        supplier_codes: list[str] | None | Unset
        if isinstance(self.supplier_codes, Unset):
            supplier_codes = UNSET
        elif isinstance(self.supplier_codes, list):
            supplier_codes = self.supplier_codes

        else:
            supplier_codes = self.supplier_codes

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if search_string is not UNSET:
            field_dict["searchString"] = search_string
        if current_status is not UNSET:
            field_dict["currentStatus"] = current_status
        if location_codes is not UNSET:
            field_dict["locationCodes"] = location_codes
        if supplier_codes is not UNSET:
            field_dict["supplierCodes"] = supplier_codes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_search_string(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search_string = _parse_search_string(d.pop("searchString", UNSET))

        _current_status = d.pop("currentStatus", UNSET)
        current_status: CurrentStatusEnum | Unset
        if isinstance(_current_status, Unset):
            current_status = UNSET
        else:
            current_status = CurrentStatusEnum(_current_status)

        def _parse_location_codes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                location_codes_type_0 = cast(list[str], data)

                return location_codes_type_0
            except:  # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        location_codes = _parse_location_codes(d.pop("locationCodes", UNSET))

        def _parse_supplier_codes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                supplier_codes_type_0 = cast(list[str], data)

                return supplier_codes_type_0
            except:  # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        supplier_codes = _parse_supplier_codes(d.pop("supplierCodes", UNSET))

        order_plan_filter_criteria_dto = cls(
            search_string=search_string,
            current_status=current_status,
            location_codes=location_codes,
            supplier_codes=supplier_codes,
        )

        return order_plan_filter_criteria_dto
