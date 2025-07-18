from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerDto")


@_attrs_define
class CustomerDto:
    """
    Attributes:
        code (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        street_address (Union[None, Unset, str]):
        address_line_1 (Union[None, Unset, str]):
        address_line_2 (Union[None, Unset, str]):
        state (Union[None, Unset, str]):
        country (Union[None, Unset, str]):
        post_code (Union[None, Unset, str]):
        email_address (Union[None, Unset, str]):
        phone (Union[None, Unset, str]):
        city (Union[None, Unset, str]):
    """

    code: Union[None, Unset, str] = UNSET
    name: Union[None, Unset, str] = UNSET
    street_address: Union[None, Unset, str] = UNSET
    address_line_1: Union[None, Unset, str] = UNSET
    address_line_2: Union[None, Unset, str] = UNSET
    state: Union[None, Unset, str] = UNSET
    country: Union[None, Unset, str] = UNSET
    post_code: Union[None, Unset, str] = UNSET
    email_address: Union[None, Unset, str] = UNSET
    phone: Union[None, Unset, str] = UNSET
    city: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        code: Union[None, Unset, str]
        if isinstance(self.code, Unset):
            code = UNSET
        else:
            code = self.code

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

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

        email_address: Union[None, Unset, str]
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        phone: Union[None, Unset, str]
        if isinstance(self.phone, Unset):
            phone = UNSET
        else:
            phone = self.phone

        city: Union[None, Unset, str]
        if isinstance(self.city, Unset):
            city = UNSET
        else:
            city = self.city

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if name is not UNSET:
            field_dict["name"] = name
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
        if email_address is not UNSET:
            field_dict["emailAddress"] = email_address
        if phone is not UNSET:
            field_dict["phone"] = phone
        if city is not UNSET:
            field_dict["city"] = city

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        code = _parse_code(d.pop("code", UNSET))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

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

        def _parse_email_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email_address = _parse_email_address(d.pop("emailAddress", UNSET))

        def _parse_phone(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        phone = _parse_phone(d.pop("phone", UNSET))

        def _parse_city(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        city = _parse_city(d.pop("city", UNSET))

        customer_dto = cls(
            code=code,
            name=name,
            street_address=street_address,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            state=state,
            country=country,
            post_code=post_code,
            email_address=email_address,
            phone=phone,
            city=city,
        )

        return customer_dto
