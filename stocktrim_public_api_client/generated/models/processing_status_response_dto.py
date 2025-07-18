from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProcessingStatusResponseDto")


@_attrs_define
class ProcessingStatusResponseDto:
    """
    Attributes:
        id (Union[Unset, int]):
        is_processing (Union[Unset, bool]):
        percentage_complete (Union[Unset, int]):
        status_message (Union[None, Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    is_processing: Union[Unset, bool] = UNSET
    percentage_complete: Union[Unset, int] = UNSET
    status_message: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        is_processing = self.is_processing

        percentage_complete = self.percentage_complete

        status_message: Union[None, Unset, str]
        if isinstance(self.status_message, Unset):
            status_message = UNSET
        else:
            status_message = self.status_message

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
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
        id = d.pop("id", UNSET)

        is_processing = d.pop("isProcessing", UNSET)

        percentage_complete = d.pop("percentageComplete", UNSET)

        def _parse_status_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        status_message = _parse_status_message(d.pop("statusMessage", UNSET))

        processing_status_response_dto = cls(
            id=id,
            is_processing=is_processing,
            percentage_complete=percentage_complete,
            status_message=status_message,
        )

        return processing_status_response_dto
