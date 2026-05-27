from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="ProcessingStatusRequestDto")


@_attrs_define
class ProcessingStatusRequestDto:
    """
    Attributes:
        is_processing (bool | Unset):
        percentage_complete (int | Unset):
        status_message (None | str | Unset):
    """

    is_processing: bool | Unset = UNSET
    percentage_complete: int | Unset = UNSET
    status_message: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_processing = self.is_processing

        percentage_complete = self.percentage_complete

        status_message: None | str | Unset
        if isinstance(self.status_message, Unset):
            status_message = UNSET
        else:
            status_message = self.status_message

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_processing is not UNSET:
            field_dict["isProcessing"] = is_processing
        if percentage_complete is not UNSET:
            field_dict["percentageComplete"] = percentage_complete
        if status_message is not UNSET:
            field_dict["statusMessage"] = status_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_processing = d.pop("isProcessing", UNSET)

        percentage_complete = d.pop("percentageComplete", UNSET)

        def _parse_status_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status_message = _parse_status_message(d.pop("statusMessage", UNSET))

        processing_status_request_dto = cls(
            is_processing=is_processing,
            percentage_complete=percentage_complete,
            status_message=status_message,
        )

        return processing_status_request_dto
