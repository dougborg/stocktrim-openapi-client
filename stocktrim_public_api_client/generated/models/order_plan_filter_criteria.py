from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.current_status_enum import CurrentStatusEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderPlanFilterCriteria")


@_attrs_define
class OrderPlanFilterCriteria:
    """
    Attributes:
        exclude_manufactured (Union[None, Unset, bool]):
        current_status (Union[Unset, CurrentStatusEnum]):
        location_id (Union[None, Unset, int]):
        location (Union[None, Unset, str]):
        customer_id (Union[None, Unset, int]):
        customer (Union[None, Unset, str]):
        supplier_id (Union[None, Unset, int]):
        supplier (Union[None, Unset, str]):
        category (Union[None, Unset, str]):
        search_string (Union[None, Unset, str]):
        sort_order (Union[None, Unset, str]):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        has_next_page (Union[None, Unset, bool]):
    """

    exclude_manufactured: Union[None, Unset, bool] = UNSET
    current_status: Union[Unset, CurrentStatusEnum] = UNSET
    location_id: Union[None, Unset, int] = UNSET
    location: Union[None, Unset, str] = UNSET
    customer_id: Union[None, Unset, int] = UNSET
    customer: Union[None, Unset, str] = UNSET
    supplier_id: Union[None, Unset, int] = UNSET
    supplier: Union[None, Unset, str] = UNSET
    category: Union[None, Unset, str] = UNSET
    search_string: Union[None, Unset, str] = UNSET
    sort_order: Union[None, Unset, str] = UNSET
    page: Union[Unset, int] = UNSET
    per_page: Union[Unset, int] = UNSET
    has_next_page: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> dict[str, Any]:
        exclude_manufactured: Union[None, Unset, bool]
        if isinstance(self.exclude_manufactured, Unset):
            exclude_manufactured = UNSET
        else:
            exclude_manufactured = self.exclude_manufactured

        current_status: Union[Unset, str] = UNSET
        if not isinstance(self.current_status, Unset):
            current_status = self.current_status.value

        location_id: Union[None, Unset, int]
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        location: Union[None, Unset, str]
        if isinstance(self.location, Unset):
            location = UNSET
        else:
            location = self.location

        customer_id: Union[None, Unset, int]
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        else:
            customer_id = self.customer_id

        customer: Union[None, Unset, str]
        if isinstance(self.customer, Unset):
            customer = UNSET
        else:
            customer = self.customer

        supplier_id: Union[None, Unset, int]
        if isinstance(self.supplier_id, Unset):
            supplier_id = UNSET
        else:
            supplier_id = self.supplier_id

        supplier: Union[None, Unset, str]
        if isinstance(self.supplier, Unset):
            supplier = UNSET
        else:
            supplier = self.supplier

        category: Union[None, Unset, str]
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        search_string: Union[None, Unset, str]
        if isinstance(self.search_string, Unset):
            search_string = UNSET
        else:
            search_string = self.search_string

        sort_order: Union[None, Unset, str]
        if isinstance(self.sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = self.sort_order

        page = self.page

        per_page = self.per_page

        has_next_page: Union[None, Unset, bool]
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

        def _parse_exclude_manufactured(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        exclude_manufactured = _parse_exclude_manufactured(d.pop("excludeManufactured", UNSET))

        _current_status = d.pop("currentStatus", UNSET)
        current_status: Union[Unset, CurrentStatusEnum]
        if isinstance(_current_status, Unset):
            current_status = UNSET
        else:
            current_status = CurrentStatusEnum(_current_status)

        def _parse_location_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        location_id = _parse_location_id(d.pop("locationId", UNSET))

        def _parse_location(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location = _parse_location(d.pop("location", UNSET))

        def _parse_customer_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        customer_id = _parse_customer_id(d.pop("customerId", UNSET))

        def _parse_customer(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer = _parse_customer(d.pop("customer", UNSET))

        def _parse_supplier_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        supplier_id = _parse_supplier_id(d.pop("supplierId", UNSET))

        def _parse_supplier(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        supplier = _parse_supplier(d.pop("supplier", UNSET))

        def _parse_category(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_search_string(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        search_string = _parse_search_string(d.pop("searchString", UNSET))

        def _parse_sort_order(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sort_order = _parse_sort_order(d.pop("sortOrder", UNSET))

        page = d.pop("page", UNSET)

        per_page = d.pop("perPage", UNSET)

        def _parse_has_next_page(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

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
