from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ...client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address


T = TypeVar("T", bound="Customer")


@_attrs_define
class Customer:
    """
    Attributes:
        birthday (None | str | Unset):
        company_name (None | str | Unset):
        created_at (datetime.datetime | Unset):
        creation_source (None | str | Unset):
        email_address (None | str | Unset):
        family_name (None | str | Unset):
        given_name (None | str | Unset):
        id (None | str | Unset):
        phone_number (None | str | Unset):
        reference_id (None | str | Unset):
        updated_at (datetime.datetime | Unset):
        version (int | Unset):
        address (Address | Unset):
    """

    birthday: None | str | Unset = UNSET
    company_name: None | str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    creation_source: None | str | Unset = UNSET
    email_address: None | str | Unset = UNSET
    family_name: None | str | Unset = UNSET
    given_name: None | str | Unset = UNSET
    id: None | str | Unset = UNSET
    phone_number: None | str | Unset = UNSET
    reference_id: None | str | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    version: int | Unset = UNSET
    address: Address | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        birthday: None | str | Unset
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        else:
            birthday = self.birthday

        company_name: None | str | Unset
        if isinstance(self.company_name, Unset):
            company_name = UNSET
        else:
            company_name = self.company_name

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        creation_source: None | str | Unset
        if isinstance(self.creation_source, Unset):
            creation_source = UNSET
        else:
            creation_source = self.creation_source

        email_address: None | str | Unset
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        family_name: None | str | Unset
        if isinstance(self.family_name, Unset):
            family_name = UNSET
        else:
            family_name = self.family_name

        given_name: None | str | Unset
        if isinstance(self.given_name, Unset):
            given_name = UNSET
        else:
            given_name = self.given_name

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        phone_number: None | str | Unset
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        reference_id: None | str | Unset
        if isinstance(self.reference_id, Unset):
            reference_id = UNSET
        else:
            reference_id = self.reference_id

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        version = self.version

        address: dict[str, Any] | Unset = UNSET
        if not isinstance(self.address, Unset):
            address = self.address.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if birthday is not UNSET:
            field_dict["birthday"] = birthday
        if company_name is not UNSET:
            field_dict["company_name"] = company_name
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if creation_source is not UNSET:
            field_dict["creation_source"] = creation_source
        if email_address is not UNSET:
            field_dict["email_address"] = email_address
        if family_name is not UNSET:
            field_dict["family_name"] = family_name
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if id is not UNSET:
            field_dict["id"] = id
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if reference_id is not UNSET:
            field_dict["reference_id"] = reference_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if version is not UNSET:
            field_dict["version"] = version
        if address is not UNSET:
            field_dict["address"] = address

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.address import Address

        d = dict(src_dict)

        def _parse_birthday(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        birthday = _parse_birthday(d.pop("birthday", UNSET))

        def _parse_company_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        company_name = _parse_company_name(d.pop("company_name", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_creation_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        creation_source = _parse_creation_source(d.pop("creation_source", UNSET))

        def _parse_email_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email_address = _parse_email_address(d.pop("email_address", UNSET))

        def _parse_family_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        family_name = _parse_family_name(d.pop("family_name", UNSET))

        def _parse_given_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        given_name = _parse_given_name(d.pop("given_name", UNSET))

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_phone_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        def _parse_reference_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reference_id = _parse_reference_id(d.pop("reference_id", UNSET))

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        version = d.pop("version", UNSET)

        _address = d.pop("address", UNSET)
        address: Address | Unset
        if isinstance(_address, Unset):
            address = UNSET
        else:
            address = Address.from_dict(_address)

        customer = cls(
            birthday=birthday,
            company_name=company_name,
            created_at=created_at,
            creation_source=creation_source,
            email_address=email_address,
            family_name=family_name,
            given_name=given_name,
            id=id,
            phone_number=phone_number,
            reference_id=reference_id,
            updated_at=updated_at,
            version=version,
            address=address,
        )

        return customer
