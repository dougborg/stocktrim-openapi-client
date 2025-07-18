from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.products_response_dto import ProductsResponseDto


T = TypeVar("T", bound="BillOfMaterialsResponseDto")


@_attrs_define
class BillOfMaterialsResponseDto:
    """
    Attributes:
        product_id (str):
        component_id (str):
        id (Union[Unset, int]):
        assembly_time_days (Union[None, Unset, int]):
        sku_component (Union[Unset, ProductsResponseDto]):
        sku_product (Union[Unset, ProductsResponseDto]):
        quantity (Union[None, Unset, float]):
    """

    product_id: str
    component_id: str
    id: Union[Unset, int] = UNSET
    assembly_time_days: Union[None, Unset, int] = UNSET
    sku_component: Union[Unset, "ProductsResponseDto"] = UNSET
    sku_product: Union[Unset, "ProductsResponseDto"] = UNSET
    quantity: Union[None, Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        component_id = self.component_id

        id = self.id

        assembly_time_days: Union[None, Unset, int]
        if isinstance(self.assembly_time_days, Unset):
            assembly_time_days = UNSET
        else:
            assembly_time_days = self.assembly_time_days

        sku_component: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sku_component, Unset):
            sku_component = self.sku_component.to_dict()

        sku_product: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sku_product, Unset):
            sku_product = self.sku_product.to_dict()

        quantity: Union[None, Unset, float]
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
        if id is not UNSET:
            field_dict["id"] = id
        if assembly_time_days is not UNSET:
            field_dict["assemblyTimeDays"] = assembly_time_days
        if sku_component is not UNSET:
            field_dict["skuComponent"] = sku_component
        if sku_product is not UNSET:
            field_dict["skuProduct"] = sku_product
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.products_response_dto import ProductsResponseDto

        d = dict(src_dict)
        product_id = d.pop("productId")

        component_id = d.pop("componentId")

        id = d.pop("id", UNSET)

        def _parse_assembly_time_days(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        assembly_time_days = _parse_assembly_time_days(d.pop("assemblyTimeDays", UNSET))

        _sku_component = d.pop("skuComponent", UNSET)
        sku_component: Union[Unset, ProductsResponseDto]
        if isinstance(_sku_component, Unset):
            sku_component = UNSET
        else:
            sku_component = ProductsResponseDto.from_dict(_sku_component)

        _sku_product = d.pop("skuProduct", UNSET)
        sku_product: Union[Unset, ProductsResponseDto]
        if isinstance(_sku_product, Unset):
            sku_product = UNSET
        else:
            sku_product = ProductsResponseDto.from_dict(_sku_product)

        def _parse_quantity(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        quantity = _parse_quantity(d.pop("quantity", UNSET))

        bill_of_materials_response_dto = cls(
            product_id=product_id,
            component_id=component_id,
            id=id,
            assembly_time_days=assembly_time_days,
            sku_component=sku_component,
            sku_product=sku_product,
            quantity=quantity,
        )

        return bill_of_materials_response_dto
