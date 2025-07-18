import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address


T = TypeVar("T", bound="Customer")


@_attrs_define
class Customer:
    """
    Attributes:
        birthday (Union[None, Unset, str]):
        company_name (Union[None, Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
        creation_source (Union[None, Unset, str]):
        email_address (Union[None, Unset, str]):
        family_name (Union[None, Unset, str]):
        given_name (Union[None, Unset, str]):
        id (Union[None, Unset, str]):
        phone_number (Union[None, Unset, str]):
        reference_id (Union[None, Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
        version (Union[Unset, int]):
        address (Union[Unset, Address]):
    """

    birthday: Union[None, Unset, str] = UNSET
    company_name: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    creation_source: Union[None, Unset, str] = UNSET
    email_address: Union[None, Unset, str] = UNSET
    family_name: Union[None, Unset, str] = UNSET
    given_name: Union[None, Unset, str] = UNSET
    id: Union[None, Unset, str] = UNSET
    phone_number: Union[None, Unset, str] = UNSET
    reference_id: Union[None, Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    version: Union[Unset, int] = UNSET
    address: Union[Unset, "Address"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        birthday: Union[None, Unset, str]
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        else:
            birthday = self.birthday

        company_name: Union[None, Unset, str]
        if isinstance(self.company_name, Unset):
            company_name = UNSET
        else:
            company_name = self.company_name

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        creation_source: Union[None, Unset, str]
        if isinstance(self.creation_source, Unset):
            creation_source = UNSET
        else:
            creation_source = self.creation_source

        email_address: Union[None, Unset, str]
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        family_name: Union[None, Unset, str]
        if isinstance(self.family_name, Unset):
            family_name = UNSET
        else:
            family_name = self.family_name

        given_name: Union[None, Unset, str]
        if isinstance(self.given_name, Unset):
            given_name = UNSET
        else:
            given_name = self.given_name

        id: Union[None, Unset, str]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        phone_number: Union[None, Unset, str]
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        reference_id: Union[None, Unset, str]
        if isinstance(self.reference_id, Unset):
            reference_id = UNSET
        else:
            reference_id = self.reference_id

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        version = self.version

        address: Union[Unset, dict[str, Any]] = UNSET
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

        def _parse_birthday(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        birthday = _parse_birthday(d.pop("birthday", UNSET))

        def _parse_company_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        company_name = _parse_company_name(d.pop("company_name", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_creation_source(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        creation_source = _parse_creation_source(d.pop("creation_source", UNSET))

        def _parse_email_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email_address = _parse_email_address(d.pop("email_address", UNSET))

        def _parse_family_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        family_name = _parse_family_name(d.pop("family_name", UNSET))

        def _parse_given_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        given_name = _parse_given_name(d.pop("given_name", UNSET))

        def _parse_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_phone_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        def _parse_reference_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reference_id = _parse_reference_id(d.pop("reference_id", UNSET))

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        version = d.pop("version", UNSET)

        _address = d.pop("address", UNSET)
        address: Union[Unset, Address]
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
