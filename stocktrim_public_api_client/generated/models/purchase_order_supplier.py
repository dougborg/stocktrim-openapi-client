from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="PurchaseOrderSupplier")


@_attrs_define
class PurchaseOrderSupplier:
    """
    Attributes:
        supplier_code (None | str | Unset):
        supplier_name (None | str | Unset):
    """

    supplier_code: None | str | Unset = UNSET
    supplier_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        supplier_code: None | str | Unset
        if isinstance(self.supplier_code, Unset):
            supplier_code = UNSET
        else:
            supplier_code = self.supplier_code

        supplier_name: None | str | Unset
        if isinstance(self.supplier_name, Unset):
            supplier_name = UNSET
        else:
            supplier_name = self.supplier_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if supplier_code is not UNSET:
            field_dict["supplierCode"] = supplier_code
        if supplier_name is not UNSET:
            field_dict["supplierName"] = supplier_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_supplier_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_code = _parse_supplier_code(d.pop("supplierCode", UNSET))

        def _parse_supplier_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_name = _parse_supplier_name(d.pop("supplierName", UNSET))

        purchase_order_supplier = cls(
            supplier_code=supplier_code,
            supplier_name=supplier_name,
        )

        return purchase_order_supplier
