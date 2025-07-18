from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Address")


@_attrs_define
class Address:
    """
    Attributes:
        address_line_1 (Union[None, Unset, str]):
        address_line_2 (Union[None, Unset, str]):
        locality (Union[None, Unset, str]):
        administrative_district_level_1 (Union[None, Unset, str]):
        postal_code (Union[None, Unset, str]):
        country (Union[None, Unset, str]):
    """

    address_line_1: Union[None, Unset, str] = UNSET
    address_line_2: Union[None, Unset, str] = UNSET
    locality: Union[None, Unset, str] = UNSET
    administrative_district_level_1: Union[None, Unset, str] = UNSET
    postal_code: Union[None, Unset, str] = UNSET
    country: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
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

        locality: Union[None, Unset, str]
        if isinstance(self.locality, Unset):
            locality = UNSET
        else:
            locality = self.locality

        administrative_district_level_1: Union[None, Unset, str]
        if isinstance(self.administrative_district_level_1, Unset):
            administrative_district_level_1 = UNSET
        else:
            administrative_district_level_1 = self.administrative_district_level_1

        postal_code: Union[None, Unset, str]
        if isinstance(self.postal_code, Unset):
            postal_code = UNSET
        else:
            postal_code = self.postal_code

        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        else:
            country = self.country

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if address_line_1 is not UNSET:
            field_dict["address_line_1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["address_line_2"] = address_line_2
        if locality is not UNSET:
            field_dict["locality"] = locality
        if administrative_district_level_1 is not UNSET:
            field_dict["administrative_district_level_1"] = administrative_district_level_1
        if postal_code is not UNSET:
            field_dict["postal_code"] = postal_code
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_address_line_1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address_line_1 = _parse_address_line_1(d.pop("address_line_1", UNSET))

        def _parse_address_line_2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address_line_2 = _parse_address_line_2(d.pop("address_line_2", UNSET))

        def _parse_locality(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        locality = _parse_locality(d.pop("locality", UNSET))

        def _parse_administrative_district_level_1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        administrative_district_level_1 = _parse_administrative_district_level_1(
            d.pop("administrative_district_level_1", UNSET)
        )

        def _parse_postal_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        postal_code = _parse_postal_code(d.pop("postal_code", UNSET))

        def _parse_country(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        country = _parse_country(d.pop("country", UNSET))

        address = cls(
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            locality=locality,
            administrative_district_level_1=administrative_district_level_1,
            postal_code=postal_code,
            country=country,
        )

        return address
