from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="SupplierResponseDto")


@_attrs_define
class SupplierResponseDto:
    """
    Attributes:
        supplier_code (str):
        id (int | Unset):
        supplier_name (None | str | Unset):
        email_address (None | str | Unset):
        primary_contact_name (None | str | Unset):
        external_id (None | str | Unset):
        default_lead_time (int | None | Unset):
        street_address (None | str | Unset):
        address_line_1 (None | str | Unset):
        address_line_2 (None | str | Unset):
        state (None | str | Unset):
        country (None | str | Unset):
        post_code (None | str | Unset):
    """

    supplier_code: str
    id: int | Unset = UNSET
    supplier_name: None | str | Unset = UNSET
    email_address: None | str | Unset = UNSET
    primary_contact_name: None | str | Unset = UNSET
    external_id: None | str | Unset = UNSET
    default_lead_time: int | None | Unset = UNSET
    street_address: None | str | Unset = UNSET
    address_line_1: None | str | Unset = UNSET
    address_line_2: None | str | Unset = UNSET
    state: None | str | Unset = UNSET
    country: None | str | Unset = UNSET
    post_code: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        supplier_code = self.supplier_code

        id = self.id

        supplier_name: None | str | Unset
        if isinstance(self.supplier_name, Unset):
            supplier_name = UNSET
        else:
            supplier_name = self.supplier_name

        email_address: None | str | Unset
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        primary_contact_name: None | str | Unset
        if isinstance(self.primary_contact_name, Unset):
            primary_contact_name = UNSET
        else:
            primary_contact_name = self.primary_contact_name

        external_id: None | str | Unset
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        default_lead_time: int | None | Unset
        if isinstance(self.default_lead_time, Unset):
            default_lead_time = UNSET
        else:
            default_lead_time = self.default_lead_time

        street_address: None | str | Unset
        if isinstance(self.street_address, Unset):
            street_address = UNSET
        else:
            street_address = self.street_address

        address_line_1: None | str | Unset
        if isinstance(self.address_line_1, Unset):
            address_line_1 = UNSET
        else:
            address_line_1 = self.address_line_1

        address_line_2: None | str | Unset
        if isinstance(self.address_line_2, Unset):
            address_line_2 = UNSET
        else:
            address_line_2 = self.address_line_2

        state: None | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        country: None | str | Unset
        if isinstance(self.country, Unset):
            country = UNSET
        else:
            country = self.country

        post_code: None | str | Unset
        if isinstance(self.post_code, Unset):
            post_code = UNSET
        else:
            post_code = self.post_code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "supplierCode": supplier_code,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if supplier_name is not UNSET:
            field_dict["supplierName"] = supplier_name
        if email_address is not UNSET:
            field_dict["emailAddress"] = email_address
        if primary_contact_name is not UNSET:
            field_dict["primaryContactName"] = primary_contact_name
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if default_lead_time is not UNSET:
            field_dict["defaultLeadTime"] = default_lead_time
        if street_address is not UNSET:
            field_dict["streetAddress"] = street_address
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if state is not UNSET:
            field_dict["state"] = state
        if country is not UNSET:
            field_dict["country"] = country
        if post_code is not UNSET:
            field_dict["postCode"] = post_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        supplier_code = d.pop("supplierCode")

        id = d.pop("id", UNSET)

        def _parse_supplier_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_name = _parse_supplier_name(d.pop("supplierName", UNSET))

        def _parse_email_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email_address = _parse_email_address(d.pop("emailAddress", UNSET))

        def _parse_primary_contact_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_contact_name = _parse_primary_contact_name(
            d.pop("primaryContactName", UNSET)
        )

        def _parse_external_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_default_lead_time(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        default_lead_time = _parse_default_lead_time(d.pop("defaultLeadTime", UNSET))

        def _parse_street_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        street_address = _parse_street_address(d.pop("streetAddress", UNSET))

        def _parse_address_line_1(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        address_line_1 = _parse_address_line_1(d.pop("addressLine1", UNSET))

        def _parse_address_line_2(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        address_line_2 = _parse_address_line_2(d.pop("addressLine2", UNSET))

        def _parse_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        state = _parse_state(d.pop("state", UNSET))

        def _parse_country(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        country = _parse_country(d.pop("country", UNSET))

        def _parse_post_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        post_code = _parse_post_code(d.pop("postCode", UNSET))

        supplier_response_dto = cls(
            supplier_code=supplier_code,
            id=id,
            supplier_name=supplier_name,
            email_address=email_address,
            primary_contact_name=primary_contact_name,
            external_id=external_id,
            default_lead_time=default_lead_time,
            street_address=street_address,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            state=state,
            country=country,
            post_code=post_code,
        )

        return supplier_response_dto
