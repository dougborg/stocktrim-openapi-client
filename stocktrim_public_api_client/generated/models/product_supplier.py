from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="ProductSupplier")


@_attrs_define
class ProductSupplier:
    """
    Attributes:
        supplier_id (str):
        supplier_name (None | str | Unset):
        supplier_sku_code (None | str | Unset):
    """

    supplier_id: str
    supplier_name: None | str | Unset = UNSET
    supplier_sku_code: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        supplier_id = self.supplier_id

        supplier_name: None | str | Unset
        if isinstance(self.supplier_name, Unset):
            supplier_name = UNSET
        else:
            supplier_name = self.supplier_name

        supplier_sku_code: None | str | Unset
        if isinstance(self.supplier_sku_code, Unset):
            supplier_sku_code = UNSET
        else:
            supplier_sku_code = self.supplier_sku_code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "supplierId": supplier_id,
            }
        )
        if supplier_name is not UNSET:
            field_dict["supplierName"] = supplier_name
        if supplier_sku_code is not UNSET:
            field_dict["supplierSkuCode"] = supplier_sku_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        supplier_id = d.pop("supplierId")

        def _parse_supplier_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_name = _parse_supplier_name(d.pop("supplierName", UNSET))

        def _parse_supplier_sku_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_sku_code = _parse_supplier_sku_code(d.pop("supplierSkuCode", UNSET))

        product_supplier = cls(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            supplier_sku_code=supplier_sku_code,
        )

        return product_supplier
