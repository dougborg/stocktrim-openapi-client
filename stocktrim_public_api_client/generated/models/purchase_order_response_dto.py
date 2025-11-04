from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ...client_types import UNSET, Unset
from ..models.purchase_order_status_dto import PurchaseOrderStatusDto

if TYPE_CHECKING:
    from ..models.purchase_order_line_item import PurchaseOrderLineItem
    from ..models.purchase_order_location import PurchaseOrderLocation
    from ..models.purchase_order_supplier import PurchaseOrderSupplier


T = TypeVar("T", bound="PurchaseOrderResponseDto")


@_attrs_define
class PurchaseOrderResponseDto:
    """
    Attributes:
        supplier (PurchaseOrderSupplier):
        purchase_order_line_items (list[PurchaseOrderLineItem]):
        id (int | Unset):
        message (None | str | Unset):
        order_date (datetime.datetime | None | Unset):
        created_date (datetime.datetime | None | Unset):
        fully_received_date (datetime.datetime | None | Unset):
        external_id (None | str | Unset):
        reference_number (None | str | Unset):
        client_reference_number (None | str | Unset):
        location (None | PurchaseOrderLocation | Unset):
        status (PurchaseOrderStatusDto | Unset): Purchase order status (0=Draft, 1=Approved, 2=Sent, 3=Received)
    """

    supplier: PurchaseOrderSupplier
    purchase_order_line_items: list[PurchaseOrderLineItem]
    id: int | Unset = UNSET
    message: None | str | Unset = UNSET
    order_date: datetime.datetime | None | Unset = UNSET
    created_date: datetime.datetime | None | Unset = UNSET
    fully_received_date: datetime.datetime | None | Unset = UNSET
    external_id: None | str | Unset = UNSET
    reference_number: None | str | Unset = UNSET
    client_reference_number: None | str | Unset = UNSET
    location: None | PurchaseOrderLocation | Unset = UNSET
    status: PurchaseOrderStatusDto | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.purchase_order_location import PurchaseOrderLocation

        supplier = self.supplier.to_dict()

        purchase_order_line_items = []
        for purchase_order_line_items_item_data in self.purchase_order_line_items:
            purchase_order_line_items_item = (
                purchase_order_line_items_item_data.to_dict()
            )
            purchase_order_line_items.append(purchase_order_line_items_item)

        id = self.id

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        order_date: None | str | Unset
        if isinstance(self.order_date, Unset):
            order_date = UNSET
        elif isinstance(self.order_date, datetime.datetime):
            order_date = self.order_date.isoformat()
        else:
            order_date = self.order_date

        created_date: None | str | Unset
        if isinstance(self.created_date, Unset):
            created_date = UNSET
        elif isinstance(self.created_date, datetime.datetime):
            created_date = self.created_date.isoformat()
        else:
            created_date = self.created_date

        fully_received_date: None | str | Unset
        if isinstance(self.fully_received_date, Unset):
            fully_received_date = UNSET
        elif isinstance(self.fully_received_date, datetime.datetime):
            fully_received_date = self.fully_received_date.isoformat()
        else:
            fully_received_date = self.fully_received_date

        external_id: None | str | Unset
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        reference_number: None | str | Unset
        if isinstance(self.reference_number, Unset):
            reference_number = UNSET
        else:
            reference_number = self.reference_number

        client_reference_number: None | str | Unset
        if isinstance(self.client_reference_number, Unset):
            client_reference_number = UNSET
        else:
            client_reference_number = self.client_reference_number

        location: dict[str, Any] | None | Unset
        if isinstance(self.location, Unset):
            location = UNSET
        elif isinstance(self.location, PurchaseOrderLocation):
            location = self.location.to_dict()
        else:
            location = self.location

        status: int | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "supplier": supplier,
                "purchaseOrderLineItems": purchase_order_line_items,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if order_date is not UNSET:
            field_dict["orderDate"] = order_date
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if fully_received_date is not UNSET:
            field_dict["fullyReceivedDate"] = fully_received_date
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if reference_number is not UNSET:
            field_dict["referenceNumber"] = reference_number
        if client_reference_number is not UNSET:
            field_dict["clientReferenceNumber"] = client_reference_number
        if location is not UNSET:
            field_dict["location"] = location
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.purchase_order_line_item import PurchaseOrderLineItem
        from ..models.purchase_order_location import PurchaseOrderLocation
        from ..models.purchase_order_supplier import PurchaseOrderSupplier

        d = dict(src_dict)
        supplier = PurchaseOrderSupplier.from_dict(d.pop("supplier"))

        purchase_order_line_items = []
        _purchase_order_line_items = d.pop("purchaseOrderLineItems")
        for purchase_order_line_items_item_data in _purchase_order_line_items:
            purchase_order_line_items_item = PurchaseOrderLineItem.from_dict(
                cast(Mapping[str, Any], purchase_order_line_items_item_data)
            )

            purchase_order_line_items.append(purchase_order_line_items_item)

        id = d.pop("id", UNSET)

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_order_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_date_type_0 = isoparse(data)

                return order_date_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        order_date = _parse_order_date(d.pop("orderDate", UNSET))

        def _parse_created_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_date_type_0 = isoparse(data)

                return created_date_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_date = _parse_created_date(d.pop("createdDate", UNSET))

        def _parse_fully_received_date(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                fully_received_date_type_0 = isoparse(data)

                return fully_received_date_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        fully_received_date = _parse_fully_received_date(
            d.pop("fullyReceivedDate", UNSET)
        )

        def _parse_external_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_reference_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reference_number = _parse_reference_number(d.pop("referenceNumber", UNSET))

        def _parse_client_reference_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        client_reference_number = _parse_client_reference_number(
            d.pop("clientReferenceNumber", UNSET)
        )

        def _parse_location(data: object) -> None | PurchaseOrderLocation | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                location_type_1 = PurchaseOrderLocation.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return location_type_1
            except:  # noqa: E722
                pass
            return cast(None | PurchaseOrderLocation | Unset, data)

        location = _parse_location(d.pop("location", UNSET))

        _status = d.pop("status", UNSET)
        status: PurchaseOrderStatusDto | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = PurchaseOrderStatusDto(_status)

        purchase_order_response_dto = cls(
            supplier=supplier,
            purchase_order_line_items=purchase_order_line_items,
            id=id,
            message=message,
            order_date=order_date,
            created_date=created_date,
            fully_received_date=fully_received_date,
            external_id=external_id,
            reference_number=reference_number,
            client_reference_number=client_reference_number,
            location=location,
            status=status,
        )

        return purchase_order_response_dto
