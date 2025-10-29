from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset
from ..models.current_status_enum import CurrentStatusEnum

T = TypeVar("T", bound="OrderPlanFilterCriteria")


@_attrs_define
class OrderPlanFilterCriteria:
    """
    Attributes:
        exclude_manufactured (bool | None | Unset):
        current_status (CurrentStatusEnum | Unset):
        location_id (int | None | Unset):
        location (None | str | Unset):
        customer_id (int | None | Unset):
        customer (None | str | Unset):
        supplier_id (int | None | Unset):
        supplier (None | str | Unset):
        category (None | str | Unset):
        search_string (None | str | Unset):
        sort_order (None | str | Unset):
        page (int | Unset):
        per_page (int | Unset):
        has_next_page (bool | None | Unset):
    """

    exclude_manufactured: bool | None | Unset = UNSET
    current_status: CurrentStatusEnum | Unset = UNSET
    location_id: int | None | Unset = UNSET
    location: None | str | Unset = UNSET
    customer_id: int | None | Unset = UNSET
    customer: None | str | Unset = UNSET
    supplier_id: int | None | Unset = UNSET
    supplier: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    search_string: None | str | Unset = UNSET
    sort_order: None | str | Unset = UNSET
    page: int | Unset = UNSET
    per_page: int | Unset = UNSET
    has_next_page: bool | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        exclude_manufactured: bool | None | Unset
        if isinstance(self.exclude_manufactured, Unset):
            exclude_manufactured = UNSET
        else:
            exclude_manufactured = self.exclude_manufactured

        current_status: str | Unset = UNSET
        if not isinstance(self.current_status, Unset):
            current_status = self.current_status.value

        location_id: int | None | Unset
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        location: None | str | Unset
        if isinstance(self.location, Unset):
            location = UNSET
        else:
            location = self.location

        customer_id: int | None | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        else:
            customer_id = self.customer_id

        customer: None | str | Unset
        if isinstance(self.customer, Unset):
            customer = UNSET
        else:
            customer = self.customer

        supplier_id: int | None | Unset
        if isinstance(self.supplier_id, Unset):
            supplier_id = UNSET
        else:
            supplier_id = self.supplier_id

        supplier: None | str | Unset
        if isinstance(self.supplier, Unset):
            supplier = UNSET
        else:
            supplier = self.supplier

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        search_string: None | str | Unset
        if isinstance(self.search_string, Unset):
            search_string = UNSET
        else:
            search_string = self.search_string

        sort_order: None | str | Unset
        if isinstance(self.sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = self.sort_order

        page = self.page

        per_page = self.per_page

        has_next_page: bool | None | Unset
        if isinstance(self.has_next_page, Unset):
            has_next_page = UNSET
        else:
            has_next_page = self.has_next_page

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if exclude_manufactured is not UNSET:
            field_dict["excludeManufactured"] = exclude_manufactured
        if current_status is not UNSET:
            field_dict["currentStatus"] = current_status
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location is not UNSET:
            field_dict["location"] = location
        if customer_id is not UNSET:
            field_dict["customerId"] = customer_id
        if customer is not UNSET:
            field_dict["customer"] = customer
        if supplier_id is not UNSET:
            field_dict["supplierId"] = supplier_id
        if supplier is not UNSET:
            field_dict["supplier"] = supplier
        if category is not UNSET:
            field_dict["category"] = category
        if search_string is not UNSET:
            field_dict["searchString"] = search_string
        if sort_order is not UNSET:
            field_dict["sortOrder"] = sort_order
        if page is not UNSET:
            field_dict["page"] = page
        if per_page is not UNSET:
            field_dict["perPage"] = per_page
        if has_next_page is not UNSET:
            field_dict["hasNextPage"] = has_next_page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_exclude_manufactured(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        exclude_manufactured = _parse_exclude_manufactured(
            d.pop("excludeManufactured", UNSET)
        )

        _current_status = d.pop("currentStatus", UNSET)
        current_status: CurrentStatusEnum | Unset
        if isinstance(_current_status, Unset):
            current_status = UNSET
        else:
            current_status = CurrentStatusEnum(_current_status)

        def _parse_location_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        location_id = _parse_location_id(d.pop("locationId", UNSET))

        def _parse_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location = _parse_location(d.pop("location", UNSET))

        def _parse_customer_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        customer_id = _parse_customer_id(d.pop("customerId", UNSET))

        def _parse_customer(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer = _parse_customer(d.pop("customer", UNSET))

        def _parse_supplier_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        supplier_id = _parse_supplier_id(d.pop("supplierId", UNSET))

        def _parse_supplier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier = _parse_supplier(d.pop("supplier", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_search_string(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search_string = _parse_search_string(d.pop("searchString", UNSET))

        def _parse_sort_order(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sort_order = _parse_sort_order(d.pop("sortOrder", UNSET))

        page = d.pop("page", UNSET)

        per_page = d.pop("perPage", UNSET)

        def _parse_has_next_page(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        has_next_page = _parse_has_next_page(d.pop("hasNextPage", UNSET))

        order_plan_filter_criteria = cls(
            exclude_manufactured=exclude_manufactured,
            current_status=current_status,
            location_id=location_id,
            location=location,
            customer_id=customer_id,
            customer=customer,
            supplier_id=supplier_id,
            supplier=supplier,
            category=category,
            search_string=search_string,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
            has_next_page=has_next_page,
        )

        return order_plan_filter_criteria
