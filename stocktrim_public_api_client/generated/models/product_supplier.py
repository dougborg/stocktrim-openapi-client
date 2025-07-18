from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductSupplier")


@_attrs_define
class ProductSupplier:
    """
    Attributes:
        supplier_id (str):
        supplier_name (Union[None, Unset, str]):
    """

    supplier_id: str
    supplier_name: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        supplier_id = self.supplier_id

        supplier_name: Union[None, Unset, str]
        if isinstance(self.supplier_name, Unset):
            supplier_name = UNSET
        else:
            supplier_name = self.supplier_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "supplierId": supplier_id,
            }
        )
        if supplier_name is not UNSET:
            field_dict["supplierName"] = supplier_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        supplier_id = d.pop("supplierId")

        def _parse_supplier_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        supplier_name = _parse_supplier_name(d.pop("supplierName", UNSET))

        product_supplier = cls(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
        )

        return product_supplier
