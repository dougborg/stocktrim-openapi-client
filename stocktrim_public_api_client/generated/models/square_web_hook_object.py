from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer import Customer
    from ..models.inventory_count_web_hook import InventoryCountWebHook
    from ..models.square_web_hook_catalog import SquareWebHookCatalog
    from ..models.square_web_hook_order_updated_data import SquareWebHookOrderUpdatedData


T = TypeVar("T", bound="SquareWebHookObject")


@_attrs_define
class SquareWebHookObject:
    """
    Attributes:
        order_updated (Union[Unset, SquareWebHookOrderUpdatedData]):
        catalog_version (Union[Unset, SquareWebHookCatalog]):
        inventory_counts (Union[None, Unset, list['InventoryCountWebHook']]):
        customer (Union[Unset, Customer]):
    """

    order_updated: Union[Unset, "SquareWebHookOrderUpdatedData"] = UNSET
    catalog_version: Union[Unset, "SquareWebHookCatalog"] = UNSET
    inventory_counts: Union[None, Unset, list["InventoryCountWebHook"]] = UNSET
    customer: Union[Unset, "Customer"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        order_updated: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.order_updated, Unset):
            order_updated = self.order_updated.to_dict()

        catalog_version: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.catalog_version, Unset):
            catalog_version = self.catalog_version.to_dict()

        inventory_counts: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.inventory_counts, Unset):
            inventory_counts = UNSET
        elif isinstance(self.inventory_counts, list):
            inventory_counts = []
            for inventory_counts_type_0_item_data in self.inventory_counts:
                inventory_counts_type_0_item = inventory_counts_type_0_item_data.to_dict()
                inventory_counts.append(inventory_counts_type_0_item)

        else:
            inventory_counts = self.inventory_counts

        customer: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.customer, Unset):
            customer = self.customer.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if order_updated is not UNSET:
            field_dict["order_updated"] = order_updated
        if catalog_version is not UNSET:
            field_dict["catalog_version"] = catalog_version
        if inventory_counts is not UNSET:
            field_dict["inventory_counts"] = inventory_counts
        if customer is not UNSET:
            field_dict["customer"] = customer

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer import Customer
        from ..models.inventory_count_web_hook import InventoryCountWebHook
        from ..models.square_web_hook_catalog import SquareWebHookCatalog
        from ..models.square_web_hook_order_updated_data import SquareWebHookOrderUpdatedData

        d = dict(src_dict)
        _order_updated = d.pop("order_updated", UNSET)
        order_updated: Union[Unset, SquareWebHookOrderUpdatedData]
        if isinstance(_order_updated, Unset):
            order_updated = UNSET
        else:
            order_updated = SquareWebHookOrderUpdatedData.from_dict(_order_updated)

        _catalog_version = d.pop("catalog_version", UNSET)
        catalog_version: Union[Unset, SquareWebHookCatalog]
        if isinstance(_catalog_version, Unset):
            catalog_version = UNSET
        else:
            catalog_version = SquareWebHookCatalog.from_dict(_catalog_version)

        def _parse_inventory_counts(data: object) -> Union[None, Unset, list["InventoryCountWebHook"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                inventory_counts_type_0 = []
                _inventory_counts_type_0 = data
                for inventory_counts_type_0_item_data in _inventory_counts_type_0:
                    inventory_counts_type_0_item = InventoryCountWebHook.from_dict(inventory_counts_type_0_item_data)

                    inventory_counts_type_0.append(inventory_counts_type_0_item)

                return inventory_counts_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["InventoryCountWebHook"]], data)

        inventory_counts = _parse_inventory_counts(d.pop("inventory_counts", UNSET))

        _customer = d.pop("customer", UNSET)
        customer: Union[Unset, Customer]
        if isinstance(_customer, Unset):
            customer = UNSET
        else:
            customer = Customer.from_dict(_customer)

        square_web_hook_object = cls(
            order_updated=order_updated,
            catalog_version=catalog_version,
            inventory_counts=inventory_counts,
            customer=customer,
        )

        return square_web_hook_object
