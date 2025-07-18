from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.product_location import ProductLocation
    from ..models.product_supplier import ProductSupplier


T = TypeVar("T", bound="ProductsRequestDto")


@_attrs_define
class ProductsRequestDto:
    """
    Attributes:
        product_id (str):
        product_code_readable (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        category (Union[None, Unset, str]):
        sub_category (Union[None, Unset, str]):
        service_level (Union[None, Unset, float]):
        lead_time (Union[None, Unset, int]):
        stock_on_hand (Union[None, Unset, float]):
        stock_on_order (Union[None, Unset, float]):
        cost (Union[None, Unset, float]):
        price (Union[None, Unset, float]):
        supplier_code (Union[None, Unset, str]):
        suppliers (Union[None, Unset, list['ProductSupplier']]):
        forecast_period (Union[None, Unset, int]):
        manufacturing_time (Union[None, Unset, int]):
        order_frequency (Union[None, Unset, int]):
        minimum_order_quantity (Union[None, Unset, float]):
        minimum_shelf_level (Union[None, Unset, float]):
        maximum_shelf_level (Union[None, Unset, float]):
        batch_size (Union[None, Unset, float]):
        discontinued (Union[None, Unset, bool]):
        unstocked (Union[None, Unset, bool]):
        option1 (Union[None, Unset, str]):
        option2 (Union[None, Unset, str]):
        option3 (Union[None, Unset, str]):
        overridden_demand (Union[None, Unset, float]):
        overridden_demand_period (Union[None, Unset, int]):
        stock_locations (Union[None, Unset, list['ProductLocation']]):
        parent_id (Union[None, Unset, str]):
        variant_type (Union[None, Unset, str]):
        variant (Union[None, Unset, str]):
    """

    product_id: str
    product_code_readable: Union[None, Unset, str] = UNSET
    name: Union[None, Unset, str] = UNSET
    category: Union[None, Unset, str] = UNSET
    sub_category: Union[None, Unset, str] = UNSET
    service_level: Union[None, Unset, float] = UNSET
    lead_time: Union[None, Unset, int] = UNSET
    stock_on_hand: Union[None, Unset, float] = UNSET
    stock_on_order: Union[None, Unset, float] = UNSET
    cost: Union[None, Unset, float] = UNSET
    price: Union[None, Unset, float] = UNSET
    supplier_code: Union[None, Unset, str] = UNSET
    suppliers: Union[None, Unset, list["ProductSupplier"]] = UNSET
    forecast_period: Union[None, Unset, int] = UNSET
    manufacturing_time: Union[None, Unset, int] = UNSET
    order_frequency: Union[None, Unset, int] = UNSET
    minimum_order_quantity: Union[None, Unset, float] = UNSET
    minimum_shelf_level: Union[None, Unset, float] = UNSET
    maximum_shelf_level: Union[None, Unset, float] = UNSET
    batch_size: Union[None, Unset, float] = UNSET
    discontinued: Union[None, Unset, bool] = UNSET
    unstocked: Union[None, Unset, bool] = UNSET
    option1: Union[None, Unset, str] = UNSET
    option2: Union[None, Unset, str] = UNSET
    option3: Union[None, Unset, str] = UNSET
    overridden_demand: Union[None, Unset, float] = UNSET
    overridden_demand_period: Union[None, Unset, int] = UNSET
    stock_locations: Union[None, Unset, list["ProductLocation"]] = UNSET
    parent_id: Union[None, Unset, str] = UNSET
    variant_type: Union[None, Unset, str] = UNSET
    variant: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        product_id = self.product_id

        product_code_readable: Union[None, Unset, str]
        if isinstance(self.product_code_readable, Unset):
            product_code_readable = UNSET
        else:
            product_code_readable = self.product_code_readable

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        category: Union[None, Unset, str]
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        sub_category: Union[None, Unset, str]
        if isinstance(self.sub_category, Unset):
            sub_category = UNSET
        else:
            sub_category = self.sub_category

        service_level: Union[None, Unset, float]
        if isinstance(self.service_level, Unset):
            service_level = UNSET
        else:
            service_level = self.service_level

        lead_time: Union[None, Unset, int]
        if isinstance(self.lead_time, Unset):
            lead_time = UNSET
        else:
            lead_time = self.lead_time

        stock_on_hand: Union[None, Unset, float]
        if isinstance(self.stock_on_hand, Unset):
            stock_on_hand = UNSET
        else:
            stock_on_hand = self.stock_on_hand

        stock_on_order: Union[None, Unset, float]
        if isinstance(self.stock_on_order, Unset):
            stock_on_order = UNSET
        else:
            stock_on_order = self.stock_on_order

        cost: Union[None, Unset, float]
        if isinstance(self.cost, Unset):
            cost = UNSET
        else:
            cost = self.cost

        price: Union[None, Unset, float]
        if isinstance(self.price, Unset):
            price = UNSET
        else:
            price = self.price

        supplier_code: Union[None, Unset, str]
        if isinstance(self.supplier_code, Unset):
            supplier_code = UNSET
        else:
            supplier_code = self.supplier_code

        suppliers: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.suppliers, Unset):
            suppliers = UNSET
        elif isinstance(self.suppliers, list):
            suppliers = []
            for suppliers_type_0_item_data in self.suppliers:
                suppliers_type_0_item = suppliers_type_0_item_data.to_dict()
                suppliers.append(suppliers_type_0_item)

        else:
            suppliers = self.suppliers

        forecast_period: Union[None, Unset, int]
        if isinstance(self.forecast_period, Unset):
            forecast_period = UNSET
        else:
            forecast_period = self.forecast_period

        manufacturing_time: Union[None, Unset, int]
        if isinstance(self.manufacturing_time, Unset):
            manufacturing_time = UNSET
        else:
            manufacturing_time = self.manufacturing_time

        order_frequency: Union[None, Unset, int]
        if isinstance(self.order_frequency, Unset):
            order_frequency = UNSET
        else:
            order_frequency = self.order_frequency

        minimum_order_quantity: Union[None, Unset, float]
        if isinstance(self.minimum_order_quantity, Unset):
            minimum_order_quantity = UNSET
        else:
            minimum_order_quantity = self.minimum_order_quantity

        minimum_shelf_level: Union[None, Unset, float]
        if isinstance(self.minimum_shelf_level, Unset):
            minimum_shelf_level = UNSET
        else:
            minimum_shelf_level = self.minimum_shelf_level

        maximum_shelf_level: Union[None, Unset, float]
        if isinstance(self.maximum_shelf_level, Unset):
            maximum_shelf_level = UNSET
        else:
            maximum_shelf_level = self.maximum_shelf_level

        batch_size: Union[None, Unset, float]
        if isinstance(self.batch_size, Unset):
            batch_size = UNSET
        else:
            batch_size = self.batch_size

        discontinued: Union[None, Unset, bool]
        if isinstance(self.discontinued, Unset):
            discontinued = UNSET
        else:
            discontinued = self.discontinued

        unstocked: Union[None, Unset, bool]
        if isinstance(self.unstocked, Unset):
            unstocked = UNSET
        else:
            unstocked = self.unstocked

        option1: Union[None, Unset, str]
        if isinstance(self.option1, Unset):
            option1 = UNSET
        else:
            option1 = self.option1

        option2: Union[None, Unset, str]
        if isinstance(self.option2, Unset):
            option2 = UNSET
        else:
            option2 = self.option2

        option3: Union[None, Unset, str]
        if isinstance(self.option3, Unset):
            option3 = UNSET
        else:
            option3 = self.option3

        overridden_demand: Union[None, Unset, float]
        if isinstance(self.overridden_demand, Unset):
            overridden_demand = UNSET
        else:
            overridden_demand = self.overridden_demand

        overridden_demand_period: Union[None, Unset, int]
        if isinstance(self.overridden_demand_period, Unset):
            overridden_demand_period = UNSET
        else:
            overridden_demand_period = self.overridden_demand_period

        stock_locations: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.stock_locations, Unset):
            stock_locations = UNSET
        elif isinstance(self.stock_locations, list):
            stock_locations = []
            for stock_locations_type_0_item_data in self.stock_locations:
                stock_locations_type_0_item = stock_locations_type_0_item_data.to_dict()
                stock_locations.append(stock_locations_type_0_item)

        else:
            stock_locations = self.stock_locations

        parent_id: Union[None, Unset, str]
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        variant_type: Union[None, Unset, str]
        if isinstance(self.variant_type, Unset):
            variant_type = UNSET
        else:
            variant_type = self.variant_type

        variant: Union[None, Unset, str]
        if isinstance(self.variant, Unset):
            variant = UNSET
        else:
            variant = self.variant

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "productId": product_id,
            }
        )
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.product_location import ProductLocation
        from ..models.product_supplier import ProductSupplier

        d = dict(src_dict)
        product_id = d.pop("productId")

        def _parse_product_code_readable(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        product_code_readable = _parse_product_code_readable(d.pop("productCodeReadable", UNSET))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_category(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_sub_category(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sub_category = _parse_sub_category(d.pop("subCategory", UNSET))

        def _parse_service_level(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        service_level = _parse_service_level(d.pop("serviceLevel", UNSET))

        def _parse_lead_time(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        lead_time = _parse_lead_time(d.pop("leadTime", UNSET))

        def _parse_stock_on_hand(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        stock_on_hand = _parse_stock_on_hand(d.pop("stockOnHand", UNSET))

        def _parse_stock_on_order(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        stock_on_order = _parse_stock_on_order(d.pop("stockOnOrder", UNSET))

        def _parse_cost(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        cost = _parse_cost(d.pop("cost", UNSET))

        def _parse_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        price = _parse_price(d.pop("price", UNSET))

        def _parse_supplier_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        supplier_code = _parse_supplier_code(d.pop("supplierCode", UNSET))

        def _parse_suppliers(data: object) -> Union[None, Unset, list["ProductSupplier"]]:
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
                    suppliers_type_0_item = ProductSupplier.from_dict(suppliers_type_0_item_data)

                    suppliers_type_0.append(suppliers_type_0_item)

                return suppliers_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ProductSupplier"]], data)

        suppliers = _parse_suppliers(d.pop("suppliers", UNSET))

        def _parse_forecast_period(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        forecast_period = _parse_forecast_period(d.pop("forecastPeriod", UNSET))

        def _parse_manufacturing_time(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        manufacturing_time = _parse_manufacturing_time(d.pop("manufacturingTime", UNSET))

        def _parse_order_frequency(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        order_frequency = _parse_order_frequency(d.pop("orderFrequency", UNSET))

        def _parse_minimum_order_quantity(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        minimum_order_quantity = _parse_minimum_order_quantity(d.pop("minimumOrderQuantity", UNSET))

        def _parse_minimum_shelf_level(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        minimum_shelf_level = _parse_minimum_shelf_level(d.pop("minimumShelfLevel", UNSET))

        def _parse_maximum_shelf_level(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        maximum_shelf_level = _parse_maximum_shelf_level(d.pop("maximumShelfLevel", UNSET))

        def _parse_batch_size(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        batch_size = _parse_batch_size(d.pop("batchSize", UNSET))

        def _parse_discontinued(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        discontinued = _parse_discontinued(d.pop("discontinued", UNSET))

        def _parse_unstocked(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        unstocked = _parse_unstocked(d.pop("unstocked", UNSET))

        def _parse_option1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        option1 = _parse_option1(d.pop("option1", UNSET))

        def _parse_option2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        option2 = _parse_option2(d.pop("option2", UNSET))

        def _parse_option3(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        option3 = _parse_option3(d.pop("option3", UNSET))

        def _parse_overridden_demand(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        overridden_demand = _parse_overridden_demand(d.pop("overriddenDemand", UNSET))

        def _parse_overridden_demand_period(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        overridden_demand_period = _parse_overridden_demand_period(d.pop("overriddenDemandPeriod", UNSET))

        def _parse_stock_locations(data: object) -> Union[None, Unset, list["ProductLocation"]]:
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
                    stock_locations_type_0_item = ProductLocation.from_dict(stock_locations_type_0_item_data)

                    stock_locations_type_0.append(stock_locations_type_0_item)

                return stock_locations_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ProductLocation"]], data)

        stock_locations = _parse_stock_locations(d.pop("stockLocations", UNSET))

        def _parse_parent_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_id = _parse_parent_id(d.pop("parentId", UNSET))

        def _parse_variant_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        variant_type = _parse_variant_type(d.pop("variantType", UNSET))

        def _parse_variant(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        variant = _parse_variant(d.pop("variant", UNSET))

        products_request_dto = cls(
            product_id=product_id,
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
        )

        return products_request_dto
