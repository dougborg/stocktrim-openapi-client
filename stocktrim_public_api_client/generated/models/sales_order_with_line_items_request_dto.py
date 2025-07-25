import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sales_order_request_dto import SalesOrderRequestDto


T = TypeVar("T", bound="SalesOrderWithLineItemsRequestDto")


@_attrs_define
class SalesOrderWithLineItemsRequestDto:
    """
    Attributes:
        order_date (datetime.datetime):
        location_code (Union[None, Unset, str]):
        location_name (Union[None, Unset, str]):
        customer_code (Union[None, Unset, str]):
        customer_name (Union[None, Unset, str]):
        sale_order_line_items (Union[None, Unset, list['SalesOrderRequestDto']]):
    """

    order_date: datetime.datetime
    location_code: Union[None, Unset, str] = UNSET
    location_name: Union[None, Unset, str] = UNSET
    customer_code: Union[None, Unset, str] = UNSET
    customer_name: Union[None, Unset, str] = UNSET
    sale_order_line_items: Union[None, Unset, list["SalesOrderRequestDto"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        order_date = self.order_date.isoformat()

        location_code: Union[None, Unset, str]
        if isinstance(self.location_code, Unset):
            location_code = UNSET
        else:
            location_code = self.location_code

        location_name: Union[None, Unset, str]
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        customer_code: Union[None, Unset, str]
        if isinstance(self.customer_code, Unset):
            customer_code = UNSET
        else:
            customer_code = self.customer_code

        customer_name: Union[None, Unset, str]
        if isinstance(self.customer_name, Unset):
            customer_name = UNSET
        else:
            customer_name = self.customer_name

        sale_order_line_items: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.sale_order_line_items, Unset):
            sale_order_line_items = UNSET
        elif isinstance(self.sale_order_line_items, list):
            sale_order_line_items = []
            for sale_order_line_items_type_0_item_data in self.sale_order_line_items:
                sale_order_line_items_type_0_item = sale_order_line_items_type_0_item_data.to_dict()
                sale_order_line_items.append(sale_order_line_items_type_0_item)

        else:
            sale_order_line_items = self.sale_order_line_items

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "orderDate": order_date,
            }
        )
        if location_code is not UNSET:
            field_dict["locationCode"] = location_code
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if customer_code is not UNSET:
            field_dict["customerCode"] = customer_code
        if customer_name is not UNSET:
            field_dict["customerName"] = customer_name
        if sale_order_line_items is not UNSET:
            field_dict["saleOrderLineItems"] = sale_order_line_items

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sales_order_request_dto import SalesOrderRequestDto

        d = dict(src_dict)
        order_date = isoparse(d.pop("orderDate"))

        def _parse_location_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_code = _parse_location_code(d.pop("locationCode", UNSET))

        def _parse_location_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        def _parse_customer_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer_code = _parse_customer_code(d.pop("customerCode", UNSET))

        def _parse_customer_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer_name = _parse_customer_name(d.pop("customerName", UNSET))

        def _parse_sale_order_line_items(data: object) -> Union[None, Unset, list["SalesOrderRequestDto"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sale_order_line_items_type_0 = []
                _sale_order_line_items_type_0 = data
                for sale_order_line_items_type_0_item_data in _sale_order_line_items_type_0:
                    sale_order_line_items_type_0_item = SalesOrderRequestDto.from_dict(
                        sale_order_line_items_type_0_item_data
                    )

                    sale_order_line_items_type_0.append(sale_order_line_items_type_0_item)

                return sale_order_line_items_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["SalesOrderRequestDto"]], data)

        sale_order_line_items = _parse_sale_order_line_items(d.pop("saleOrderLineItems", UNSET))

        sales_order_with_line_items_request_dto = cls(
            order_date=order_date,
            location_code=location_code,
            location_name=location_name,
            customer_code=customer_code,
            customer_name=customer_name,
            sale_order_line_items=sale_order_line_items,
        )

        return sales_order_with_line_items_request_dto
