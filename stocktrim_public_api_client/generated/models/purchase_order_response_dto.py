import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.purchase_order_status_dto import PurchaseOrderStatusDto
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.purchase_order_line_item import PurchaseOrderLineItem
    from ..models.purchase_order_location import PurchaseOrderLocation
    from ..models.purchase_order_supplier import PurchaseOrderSupplier


T = TypeVar("T", bound="PurchaseOrderResponseDto")


@_attrs_define
class PurchaseOrderResponseDto:
    """
    Attributes:
        order_date (datetime.datetime):
        supplier (PurchaseOrderSupplier):
        purchase_order_line_items (list['PurchaseOrderLineItem']):
        id (Union[Unset, int]):
        message (Union[None, Unset, str]):
        created_date (Union[None, Unset, datetime.datetime]):
        fully_received_date (Union[None, Unset, datetime.datetime]):
        external_id (Union[None, Unset, str]):
        reference_number (Union[None, Unset, str]):
        client_reference_number (Union[None, Unset, str]):
        location (Union[Unset, PurchaseOrderLocation]):
        status (Union[Unset, PurchaseOrderStatusDto]):
    """

    order_date: datetime.datetime
    supplier: "PurchaseOrderSupplier"
    purchase_order_line_items: list["PurchaseOrderLineItem"]
    id: Union[Unset, int] = UNSET
    message: Union[None, Unset, str] = UNSET
    created_date: Union[None, Unset, datetime.datetime] = UNSET
    fully_received_date: Union[None, Unset, datetime.datetime] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    reference_number: Union[None, Unset, str] = UNSET
    client_reference_number: Union[None, Unset, str] = UNSET
    location: Union[Unset, "PurchaseOrderLocation"] = UNSET
    status: Union[Unset, PurchaseOrderStatusDto] = UNSET

    def to_dict(self) -> dict[str, Any]:
        order_date = self.order_date.isoformat()

        supplier = self.supplier.to_dict()

        purchase_order_line_items = []
        for purchase_order_line_items_item_data in self.purchase_order_line_items:
            purchase_order_line_items_item = purchase_order_line_items_item_data.to_dict()
            purchase_order_line_items.append(purchase_order_line_items_item)

        id = self.id

        message: Union[None, Unset, str]
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        created_date: Union[None, Unset, str]
        if isinstance(self.created_date, Unset):
            created_date = UNSET
        elif isinstance(self.created_date, datetime.datetime):
            created_date = self.created_date.isoformat()
        else:
            created_date = self.created_date

        fully_received_date: Union[None, Unset, str]
        if isinstance(self.fully_received_date, Unset):
            fully_received_date = UNSET
        elif isinstance(self.fully_received_date, datetime.datetime):
            fully_received_date = self.fully_received_date.isoformat()
        else:
            fully_received_date = self.fully_received_date

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        reference_number: Union[None, Unset, str]
        if isinstance(self.reference_number, Unset):
            reference_number = UNSET
        else:
            reference_number = self.reference_number

        client_reference_number: Union[None, Unset, str]
        if isinstance(self.client_reference_number, Unset):
            client_reference_number = UNSET
        else:
            client_reference_number = self.client_reference_number

        location: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "orderDate": order_date,
                "supplier": supplier,
                "purchaseOrderLineItems": purchase_order_line_items,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
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
        order_date = isoparse(d.pop("orderDate"))

        supplier = PurchaseOrderSupplier.from_dict(d.pop("supplier"))

        purchase_order_line_items = []
        _purchase_order_line_items = d.pop("purchaseOrderLineItems")
        for purchase_order_line_items_item_data in _purchase_order_line_items:
            purchase_order_line_items_item = PurchaseOrderLineItem.from_dict(purchase_order_line_items_item_data)

            purchase_order_line_items.append(purchase_order_line_items_item)

        id = d.pop("id", UNSET)

        def _parse_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_created_date(data: object) -> Union[None, Unset, datetime.datetime]:
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
            return cast(Union[None, Unset, datetime.datetime], data)

        created_date = _parse_created_date(d.pop("createdDate", UNSET))

        def _parse_fully_received_date(data: object) -> Union[None, Unset, datetime.datetime]:
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
            return cast(Union[None, Unset, datetime.datetime], data)

        fully_received_date = _parse_fully_received_date(d.pop("fullyReceivedDate", UNSET))

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_reference_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reference_number = _parse_reference_number(d.pop("referenceNumber", UNSET))

        def _parse_client_reference_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        client_reference_number = _parse_client_reference_number(d.pop("clientReferenceNumber", UNSET))

        _location = d.pop("location", UNSET)
        location: Union[Unset, PurchaseOrderLocation]
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = PurchaseOrderLocation.from_dict(_location)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PurchaseOrderStatusDto]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = PurchaseOrderStatusDto(_status)

        purchase_order_response_dto = cls(
            order_date=order_date,
            supplier=supplier,
            purchase_order_line_items=purchase_order_line_items,
            id=id,
            message=message,
            created_date=created_date,
            fully_received_date=fully_received_date,
            external_id=external_id,
            reference_number=reference_number,
            client_reference_number=client_reference_number,
            location=location,
            status=status,
        )

        return purchase_order_response_dto
