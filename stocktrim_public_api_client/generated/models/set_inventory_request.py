from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inventory import Inventory


T = TypeVar("T", bound="SetInventoryRequest")


@_attrs_define
class SetInventoryRequest:
    """
    Attributes:
        update_overall_all_on_order_to_be_sum_of_location (bool | Unset):
        update_overall_all_on_hand_to_be_sum_of_location (bool | Unset):
        inventory (list[Inventory] | None | Unset):
    """

    update_overall_all_on_order_to_be_sum_of_location: bool | Unset = UNSET
    update_overall_all_on_hand_to_be_sum_of_location: bool | Unset = UNSET
    inventory: list[Inventory] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        update_overall_all_on_order_to_be_sum_of_location = (
            self.update_overall_all_on_order_to_be_sum_of_location
        )

        update_overall_all_on_hand_to_be_sum_of_location = (
            self.update_overall_all_on_hand_to_be_sum_of_location
        )

        inventory: list[dict[str, Any]] | None | Unset
        if isinstance(self.inventory, Unset):
            inventory = UNSET
        elif isinstance(self.inventory, list):
            inventory = []
            for inventory_type_0_item_data in self.inventory:
                inventory_type_0_item = inventory_type_0_item_data.to_dict()
                inventory.append(inventory_type_0_item)

        else:
            inventory = self.inventory

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if update_overall_all_on_order_to_be_sum_of_location is not UNSET:
            field_dict["updateOverallAllOnOrderToBeSumOfLocation"] = (
                update_overall_all_on_order_to_be_sum_of_location
            )
        if update_overall_all_on_hand_to_be_sum_of_location is not UNSET:
            field_dict["updateOverallAllOnHandToBeSumOfLocation"] = (
                update_overall_all_on_hand_to_be_sum_of_location
            )
        if inventory is not UNSET:
            field_dict["inventory"] = inventory

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inventory import Inventory

        d = dict(src_dict)
        update_overall_all_on_order_to_be_sum_of_location = d.pop(
            "updateOverallAllOnOrderToBeSumOfLocation", UNSET
        )

        update_overall_all_on_hand_to_be_sum_of_location = d.pop(
            "updateOverallAllOnHandToBeSumOfLocation", UNSET
        )

        def _parse_inventory(data: object) -> list[Inventory] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                inventory_type_0 = []
                _inventory_type_0 = data
                for inventory_type_0_item_data in _inventory_type_0:
                    inventory_type_0_item = Inventory.from_dict(
                        cast(Mapping[str, Any], inventory_type_0_item_data)
                    )

                    inventory_type_0.append(inventory_type_0_item)

                return inventory_type_0
            except:  # noqa: E722
                pass
            return cast(list[Inventory] | None | Unset, data)

        inventory = _parse_inventory(d.pop("inventory", UNSET))

        set_inventory_request = cls(
            update_overall_all_on_order_to_be_sum_of_location=update_overall_all_on_order_to_be_sum_of_location,
            update_overall_all_on_hand_to_be_sum_of_location=update_overall_all_on_hand_to_be_sum_of_location,
            inventory=inventory,
        )

        return set_inventory_request
