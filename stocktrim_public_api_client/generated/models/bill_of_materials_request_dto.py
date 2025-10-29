from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="BillOfMaterialsRequestDto")


@_attrs_define
class BillOfMaterialsRequestDto:
    """
    Attributes:
        product_id (str):
        component_id (str):
        quantity (float | None | Unset):
    """

    product_id: str
    component_id: str
    quantity: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        component_id = self.component_id

        quantity: float | None | Unset
        if isinstance(self.quantity, Unset):
            quantity = UNSET
        else:
            quantity = self.quantity

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "productId": product_id,
                "componentId": component_id,
            }
        )
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        product_id = d.pop("productId")

        component_id = d.pop("componentId")

        def _parse_quantity(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        quantity = _parse_quantity(d.pop("quantity", UNSET))

        bill_of_materials_request_dto = cls(
            product_id=product_id,
            component_id=component_id,
            quantity=quantity,
        )

        return bill_of_materials_request_dto
