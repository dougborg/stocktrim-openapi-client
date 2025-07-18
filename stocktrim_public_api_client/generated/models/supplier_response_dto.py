from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SupplierResponseDto")


@_attrs_define
class SupplierResponseDto:
    """
    Attributes:
        supplier_code (str):
        id (Union[Unset, int]):
        supplier_name (Union[None, Unset, str]):
        email_address (Union[None, Unset, str]):
        primary_contact_name (Union[None, Unset, str]):
        external_id (Union[None, Unset, str]):
        default_lead_time (Union[None, Unset, int]):
        street_address (Union[None, Unset, str]):
        address_line_1 (Union[None, Unset, str]):
        address_line_2 (Union[None, Unset, str]):
        state (Union[None, Unset, str]):
        country (Union[None, Unset, str]):
        post_code (Union[None, Unset, str]):
    """

    supplier_code: str
    id: Union[Unset, int] = UNSET
    supplier_name: Union[None, Unset, str] = UNSET
    email_address: Union[None, Unset, str] = UNSET
    primary_contact_name: Union[None, Unset, str] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    default_lead_time: Union[None, Unset, int] = UNSET
    street_address: Union[None, Unset, str] = UNSET
    address_line_1: Union[None, Unset, str] = UNSET
    address_line_2: Union[None, Unset, str] = UNSET
    state: Union[None, Unset, str] = UNSET
    country: Union[None, Unset, str] = UNSET
    post_code: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        supplier_code = self.supplier_code

        id = self.id

        supplier_name: Union[None, Unset, str]
        if isinstance(self.supplier_name, Unset):
            supplier_name = UNSET
        else:
            supplier_name = self.supplier_name

        email_address: Union[None, Unset, str]
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        primary_contact_name: Union[None, Unset, str]
        if isinstance(self.primary_contact_name, Unset):
            primary_contact_name = UNSET
        else:
            primary_contact_name = self.primary_contact_name

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        default_lead_time: Union[None, Unset, int]
        if isinstance(self.default_lead_time, Unset):
            default_lead_time = UNSET
        else:
            default_lead_time = self.default_lead_time

        street_address: Union[None, Unset, str]
        if isinstance(self.street_address, Unset):
            street_address = UNSET
        else:
            street_address = self.street_address

        address_line_1: Union[None, Unset, str]
        if isinstance(self.address_line_1, Unset):
            address_line_1 = UNSET
        else:
            address_line_1 = self.address_line_1

        address_line_2: Union[None, Unset, str]
        if isinstance(self.address_line_2, Unset):
            address_line_2 = UNSET
        else:
            address_line_2 = self.address_line_2

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        else:
            country = self.country

        post_code: Union[None, Unset, str]
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

        def _parse_supplier_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        supplier_name = _parse_supplier_name(d.pop("supplierName", UNSET))

        def _parse_email_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email_address = _parse_email_address(d.pop("emailAddress", UNSET))

        def _parse_primary_contact_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_contact_name = _parse_primary_contact_name(d.pop("primaryContactName", UNSET))

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_default_lead_time(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        default_lead_time = _parse_default_lead_time(d.pop("defaultLeadTime", UNSET))

        def _parse_street_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        street_address = _parse_street_address(d.pop("streetAddress", UNSET))

        def _parse_address_line_1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address_line_1 = _parse_address_line_1(d.pop("addressLine1", UNSET))

        def _parse_address_line_2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address_line_2 = _parse_address_line_2(d.pop("addressLine2", UNSET))

        def _parse_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state = _parse_state(d.pop("state", UNSET))

        def _parse_country(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        country = _parse_country(d.pop("country", UNSET))

        def _parse_post_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

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
