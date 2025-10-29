from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.product_location import ProductLocation
    from ..models.product_supplier import ProductSupplier


T = TypeVar("T", bound="ProductsResponseDto")


@_attrs_define
class ProductsResponseDto:
    """
    Attributes:
        product_id (str):
        id (int | Unset):
        product_code_readable (None | str | Unset):
        name (None | str | Unset):
        category (None | str | Unset):
        sub_category (None | str | Unset):
        service_level (float | None | Unset):
        lead_time (int | None | Unset):
        stock_on_hand (float | None | Unset):
        stock_on_order (float | None | Unset):
        cost (float | None | Unset):
        price (float | None | Unset):
        supplier_code (None | str | Unset):
        suppliers (list[ProductSupplier] | None | Unset):
        forecast_period (int | None | Unset):
        manufacturing_time (int | None | Unset):
        order_frequency (int | None | Unset):
        minimum_order_quantity (float | None | Unset):
        minimum_shelf_level (float | None | Unset):
        maximum_shelf_level (float | None | Unset):
        batch_size (float | None | Unset):
        barcode (None | str | Unset):
        discontinued (bool | None | Unset):
        unstocked (bool | None | Unset):
        option1 (None | str | Unset):
        option2 (None | str | Unset):
        option3 (None | str | Unset):
        overridden_demand (float | None | Unset):
        overridden_demand_period (int | None | Unset):
        stock_locations (list[ProductLocation] | None | Unset):
        parent_id (None | str | Unset):
        variant_type (None | str | Unset):
        variant (None | str | Unset):
        ignore_seasonality (bool | None | Unset):
        weight (float | None | Unset):
        height (float | None | Unset):
        width (float | None | Unset):
        length (float | None | Unset):
    """

    product_id: str
    id: int | Unset = UNSET
    product_code_readable: None | str | Unset = UNSET
    name: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    sub_category: None | str | Unset = UNSET
    service_level: float | None | Unset = UNSET
    lead_time: int | None | Unset = UNSET
    stock_on_hand: float | None | Unset = UNSET
    stock_on_order: float | None | Unset = UNSET
    cost: float | None | Unset = UNSET
    price: float | None | Unset = UNSET
    supplier_code: None | str | Unset = UNSET
    suppliers: list[ProductSupplier] | None | Unset = UNSET
    forecast_period: int | None | Unset = UNSET
    manufacturing_time: int | None | Unset = UNSET
    order_frequency: int | None | Unset = UNSET
    minimum_order_quantity: float | None | Unset = UNSET
    minimum_shelf_level: float | None | Unset = UNSET
    maximum_shelf_level: float | None | Unset = UNSET
    batch_size: float | None | Unset = UNSET
    barcode: None | str | Unset = UNSET
    discontinued: bool | None | Unset = UNSET
    unstocked: bool | None | Unset = UNSET
    option1: None | str | Unset = UNSET
    option2: None | str | Unset = UNSET
    option3: None | str | Unset = UNSET
    overridden_demand: float | None | Unset = UNSET
    overridden_demand_period: int | None | Unset = UNSET
    stock_locations: list[ProductLocation] | None | Unset = UNSET
    parent_id: None | str | Unset = UNSET
    variant_type: None | str | Unset = UNSET
    variant: None | str | Unset = UNSET
    ignore_seasonality: bool | None | Unset = UNSET
    weight: float | None | Unset = UNSET
    height: float | None | Unset = UNSET
    width: float | None | Unset = UNSET
    length: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        id = self.id

        product_code_readable: None | str | Unset
        if isinstance(self.product_code_readable, Unset):
            product_code_readable = UNSET
        else:
            product_code_readable = self.product_code_readable

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        sub_category: None | str | Unset
        if isinstance(self.sub_category, Unset):
            sub_category = UNSET
        else:
            sub_category = self.sub_category

        service_level: float | None | Unset
        if isinstance(self.service_level, Unset):
            service_level = UNSET
        else:
            service_level = self.service_level

        lead_time: int | None | Unset
        if isinstance(self.lead_time, Unset):
            lead_time = UNSET
        else:
            lead_time = self.lead_time

        stock_on_hand: float | None | Unset
        if isinstance(self.stock_on_hand, Unset):
            stock_on_hand = UNSET
        else:
            stock_on_hand = self.stock_on_hand

        stock_on_order: float | None | Unset
        if isinstance(self.stock_on_order, Unset):
            stock_on_order = UNSET
        else:
            stock_on_order = self.stock_on_order

        cost: float | None | Unset
        if isinstance(self.cost, Unset):
            cost = UNSET
        else:
            cost = self.cost

        price: float | None | Unset
        if isinstance(self.price, Unset):
            price = UNSET
        else:
            price = self.price

        supplier_code: None | str | Unset
        if isinstance(self.supplier_code, Unset):
            supplier_code = UNSET
        else:
            supplier_code = self.supplier_code

        suppliers: list[dict[str, Any]] | None | Unset
        if isinstance(self.suppliers, Unset):
            suppliers = UNSET
        elif isinstance(self.suppliers, list):
            suppliers = []
            for suppliers_type_0_item_data in self.suppliers:
                suppliers_type_0_item = suppliers_type_0_item_data.to_dict()
                suppliers.append(suppliers_type_0_item)

        else:
            suppliers = self.suppliers

        forecast_period: int | None | Unset
        if isinstance(self.forecast_period, Unset):
            forecast_period = UNSET
        else:
            forecast_period = self.forecast_period

        manufacturing_time: int | None | Unset
        if isinstance(self.manufacturing_time, Unset):
            manufacturing_time = UNSET
        else:
            manufacturing_time = self.manufacturing_time

        order_frequency: int | None | Unset
        if isinstance(self.order_frequency, Unset):
            order_frequency = UNSET
        else:
            order_frequency = self.order_frequency

        minimum_order_quantity: float | None | Unset
        if isinstance(self.minimum_order_quantity, Unset):
            minimum_order_quantity = UNSET
        else:
            minimum_order_quantity = self.minimum_order_quantity

        minimum_shelf_level: float | None | Unset
        if isinstance(self.minimum_shelf_level, Unset):
            minimum_shelf_level = UNSET
        else:
            minimum_shelf_level = self.minimum_shelf_level

        maximum_shelf_level: float | None | Unset
        if isinstance(self.maximum_shelf_level, Unset):
            maximum_shelf_level = UNSET
        else:
            maximum_shelf_level = self.maximum_shelf_level

        batch_size: float | None | Unset
        if isinstance(self.batch_size, Unset):
            batch_size = UNSET
        else:
            batch_size = self.batch_size

        barcode: None | str | Unset
        if isinstance(self.barcode, Unset):
            barcode = UNSET
        else:
            barcode = self.barcode

        discontinued: bool | None | Unset
        if isinstance(self.discontinued, Unset):
            discontinued = UNSET
        else:
            discontinued = self.discontinued

        unstocked: bool | None | Unset
        if isinstance(self.unstocked, Unset):
            unstocked = UNSET
        else:
            unstocked = self.unstocked

        option1: None | str | Unset
        if isinstance(self.option1, Unset):
            option1 = UNSET
        else:
            option1 = self.option1

        option2: None | str | Unset
        if isinstance(self.option2, Unset):
            option2 = UNSET
        else:
            option2 = self.option2

        option3: None | str | Unset
        if isinstance(self.option3, Unset):
            option3 = UNSET
        else:
            option3 = self.option3

        overridden_demand: float | None | Unset
        if isinstance(self.overridden_demand, Unset):
            overridden_demand = UNSET
        else:
            overridden_demand = self.overridden_demand

        overridden_demand_period: int | None | Unset
        if isinstance(self.overridden_demand_period, Unset):
            overridden_demand_period = UNSET
        else:
            overridden_demand_period = self.overridden_demand_period

        stock_locations: list[dict[str, Any]] | None | Unset
        if isinstance(self.stock_locations, Unset):
            stock_locations = UNSET
        elif isinstance(self.stock_locations, list):
            stock_locations = []
            for stock_locations_type_0_item_data in self.stock_locations:
                stock_locations_type_0_item = stock_locations_type_0_item_data.to_dict()
                stock_locations.append(stock_locations_type_0_item)

        else:
            stock_locations = self.stock_locations

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        variant_type: None | str | Unset
        if isinstance(self.variant_type, Unset):
            variant_type = UNSET
        else:
            variant_type = self.variant_type

        variant: None | str | Unset
        if isinstance(self.variant, Unset):
            variant = UNSET
        else:
            variant = self.variant

        ignore_seasonality: bool | None | Unset
        if isinstance(self.ignore_seasonality, Unset):
            ignore_seasonality = UNSET
        else:
            ignore_seasonality = self.ignore_seasonality

        weight: float | None | Unset
        if isinstance(self.weight, Unset):
            weight = UNSET
        else:
            weight = self.weight

        height: float | None | Unset
        if isinstance(self.height, Unset):
            height = UNSET
        else:
            height = self.height

        width: float | None | Unset
        if isinstance(self.width, Unset):
            width = UNSET
        else:
            width = self.width

        length: float | None | Unset
        if isinstance(self.length, Unset):
            length = UNSET
        else:
            length = self.length

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "productId": product_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if product_code_readable is not UNSET:
            field_dict["productCodeReadable"] = product_code_readable
        if name is not UNSET:
            field_dict["name"] = name
        if category is not UNSET:
            field_dict["category"] = category
        if sub_category is not UNSET:
            field_dict["subCategory"] = sub_category
        if service_level is not UNSET:
            field_dict["serviceLevel"] = service_level
        if lead_time is not UNSET:
            field_dict["leadTime"] = lead_time
        if stock_on_hand is not UNSET:
            field_dict["stockOnHand"] = stock_on_hand
        if stock_on_order is not UNSET:
            field_dict["stockOnOrder"] = stock_on_order
        if cost is not UNSET:
            field_dict["cost"] = cost
        if price is not UNSET:
            field_dict["price"] = price
        if supplier_code is not UNSET:
            field_dict["supplierCode"] = supplier_code
        if suppliers is not UNSET:
            field_dict["suppliers"] = suppliers
        if forecast_period is not UNSET:
            field_dict["forecastPeriod"] = forecast_period
        if manufacturing_time is not UNSET:
            field_dict["manufacturingTime"] = manufacturing_time
        if order_frequency is not UNSET:
            field_dict["orderFrequency"] = order_frequency
        if minimum_order_quantity is not UNSET:
            field_dict["minimumOrderQuantity"] = minimum_order_quantity
        if minimum_shelf_level is not UNSET:
            field_dict["minimumShelfLevel"] = minimum_shelf_level
        if maximum_shelf_level is not UNSET:
            field_dict["maximumShelfLevel"] = maximum_shelf_level
        if batch_size is not UNSET:
            field_dict["batchSize"] = batch_size
        if barcode is not UNSET:
            field_dict["barcode"] = barcode
        if discontinued is not UNSET:
            field_dict["discontinued"] = discontinued
        if unstocked is not UNSET:
            field_dict["unstocked"] = unstocked
        if option1 is not UNSET:
            field_dict["option1"] = option1
        if option2 is not UNSET:
            field_dict["option2"] = option2
        if option3 is not UNSET:
            field_dict["option3"] = option3
        if overridden_demand is not UNSET:
            field_dict["overriddenDemand"] = overridden_demand
        if overridden_demand_period is not UNSET:
            field_dict["overriddenDemandPeriod"] = overridden_demand_period
        if stock_locations is not UNSET:
            field_dict["stockLocations"] = stock_locations
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if variant_type is not UNSET:
            field_dict["variantType"] = variant_type
        if variant is not UNSET:
            field_dict["variant"] = variant
        if ignore_seasonality is not UNSET:
            field_dict["ignoreSeasonality"] = ignore_seasonality
        if weight is not UNSET:
            field_dict["weight"] = weight
        if height is not UNSET:
            field_dict["height"] = height
        if width is not UNSET:
            field_dict["width"] = width
        if length is not UNSET:
            field_dict["length"] = length

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.product_location import ProductLocation
        from ..models.product_supplier import ProductSupplier

        d = dict(src_dict)
        product_id = d.pop("productId")

        id = d.pop("id", UNSET)

        def _parse_product_code_readable(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        product_code_readable = _parse_product_code_readable(
            d.pop("productCodeReadable", UNSET)
        )

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_sub_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sub_category = _parse_sub_category(d.pop("subCategory", UNSET))

        def _parse_service_level(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        service_level = _parse_service_level(d.pop("serviceLevel", UNSET))

        def _parse_lead_time(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        lead_time = _parse_lead_time(d.pop("leadTime", UNSET))

        def _parse_stock_on_hand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stock_on_hand = _parse_stock_on_hand(d.pop("stockOnHand", UNSET))

        def _parse_stock_on_order(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stock_on_order = _parse_stock_on_order(d.pop("stockOnOrder", UNSET))

        def _parse_cost(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cost = _parse_cost(d.pop("cost", UNSET))

        def _parse_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        price = _parse_price(d.pop("price", UNSET))

        def _parse_supplier_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        supplier_code = _parse_supplier_code(d.pop("supplierCode", UNSET))

        def _parse_suppliers(data: object) -> list[ProductSupplier] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                suppliers_type_0 = []
                _suppliers_type_0 = data
                for suppliers_type_0_item_data in _suppliers_type_0:
                    suppliers_type_0_item = ProductSupplier.from_dict(
                        cast(Mapping[str, Any], suppliers_type_0_item_data)
                    )

                    suppliers_type_0.append(suppliers_type_0_item)

                return suppliers_type_0
            except:  # noqa: E722
                pass
            return cast(list[ProductSupplier] | None | Unset, data)

        suppliers = _parse_suppliers(d.pop("suppliers", UNSET))

        def _parse_forecast_period(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        forecast_period = _parse_forecast_period(d.pop("forecastPeriod", UNSET))

        def _parse_manufacturing_time(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        manufacturing_time = _parse_manufacturing_time(
            d.pop("manufacturingTime", UNSET)
        )

        def _parse_order_frequency(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        order_frequency = _parse_order_frequency(d.pop("orderFrequency", UNSET))

        def _parse_minimum_order_quantity(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        minimum_order_quantity = _parse_minimum_order_quantity(
            d.pop("minimumOrderQuantity", UNSET)
        )

        def _parse_minimum_shelf_level(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        minimum_shelf_level = _parse_minimum_shelf_level(
            d.pop("minimumShelfLevel", UNSET)
        )

        def _parse_maximum_shelf_level(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        maximum_shelf_level = _parse_maximum_shelf_level(
            d.pop("maximumShelfLevel", UNSET)
        )

        def _parse_batch_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        batch_size = _parse_batch_size(d.pop("batchSize", UNSET))

        def _parse_barcode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        barcode = _parse_barcode(d.pop("barcode", UNSET))

        def _parse_discontinued(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        discontinued = _parse_discontinued(d.pop("discontinued", UNSET))

        def _parse_unstocked(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        unstocked = _parse_unstocked(d.pop("unstocked", UNSET))

        def _parse_option1(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        option1 = _parse_option1(d.pop("option1", UNSET))

        def _parse_option2(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        option2 = _parse_option2(d.pop("option2", UNSET))

        def _parse_option3(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        option3 = _parse_option3(d.pop("option3", UNSET))

        def _parse_overridden_demand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        overridden_demand = _parse_overridden_demand(d.pop("overriddenDemand", UNSET))

        def _parse_overridden_demand_period(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        overridden_demand_period = _parse_overridden_demand_period(
            d.pop("overriddenDemandPeriod", UNSET)
        )

        def _parse_stock_locations(
            data: object,
        ) -> list[ProductLocation] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                stock_locations_type_0 = []
                _stock_locations_type_0 = data
                for stock_locations_type_0_item_data in _stock_locations_type_0:
                    stock_locations_type_0_item = ProductLocation.from_dict(
                        cast(Mapping[str, Any], stock_locations_type_0_item_data)
                    )

                    stock_locations_type_0.append(stock_locations_type_0_item)

                return stock_locations_type_0
            except:  # noqa: E722
                pass
            return cast(list[ProductLocation] | None | Unset, data)

        stock_locations = _parse_stock_locations(d.pop("stockLocations", UNSET))

        def _parse_parent_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_id = _parse_parent_id(d.pop("parentId", UNSET))

        def _parse_variant_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        variant_type = _parse_variant_type(d.pop("variantType", UNSET))

        def _parse_variant(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        variant = _parse_variant(d.pop("variant", UNSET))

        def _parse_ignore_seasonality(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        ignore_seasonality = _parse_ignore_seasonality(
            d.pop("ignoreSeasonality", UNSET)
        )

        def _parse_weight(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        weight = _parse_weight(d.pop("weight", UNSET))

        def _parse_height(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        height = _parse_height(d.pop("height", UNSET))

        def _parse_width(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        width = _parse_width(d.pop("width", UNSET))

        def _parse_length(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        length = _parse_length(d.pop("length", UNSET))

        products_response_dto = cls(
            product_id=product_id,
            id=id,
            product_code_readable=product_code_readable,
            name=name,
            category=category,
            sub_category=sub_category,
            service_level=service_level,
            lead_time=lead_time,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
            cost=cost,
            price=price,
            supplier_code=supplier_code,
            suppliers=suppliers,
            forecast_period=forecast_period,
            manufacturing_time=manufacturing_time,
            order_frequency=order_frequency,
            minimum_order_quantity=minimum_order_quantity,
            minimum_shelf_level=minimum_shelf_level,
            maximum_shelf_level=maximum_shelf_level,
            batch_size=batch_size,
            barcode=barcode,
            discontinued=discontinued,
            unstocked=unstocked,
            option1=option1,
            option2=option2,
            option3=option3,
            overridden_demand=overridden_demand,
            overridden_demand_period=overridden_demand_period,
            stock_locations=stock_locations,
            parent_id=parent_id,
            variant_type=variant_type,
            variant=variant,
            ignore_seasonality=ignore_seasonality,
            weight=weight,
            height=height,
            width=width,
            length=length,
        )

        return products_response_dto
