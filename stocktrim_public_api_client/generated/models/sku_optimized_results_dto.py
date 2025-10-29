from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ...client_types import UNSET, Unset

T = TypeVar("T", bound="SkuOptimizedResultsDto")


@_attrs_define
class SkuOptimizedResultsDto:
    """
    Attributes:
        id (int | Unset):
        sku_property_id (int | None | Unset):
        sku_id (int | None | Unset):
        location_id (int | None | Unset):
        channel_id (int | None | Unset):
        sku_grouping_id (int | None | Unset):
        sku_optimized_results_group_id (int | None | Unset):
        tenant_id (None | Unset | UUID):
        calculated_date_time (datetime.datetime | Unset):
        effective_to_date_time (datetime.datetime | None | Unset):
        reorder_point (float | None | Unset):
        order_quantity (float | None | Unset):
        lead_demand (float | None | Unset):
        forecast_period_demand (float | None | Unset):
        overridden_future_demand_effective_from_now (float | None | Unset):
        safety_stock_level (float | None | Unset):
        economic_order_quantity (float | None | Unset):
        optimial_stock_cycle (float | None | Unset):
        lead_time_days (int | None | Unset):
        reorder_frequency_days (int | None | Unset):
        order_count (int | Unset):
        latest_order_date (datetime.datetime | None | Unset):
        first_purchase_date (datetime.datetime | None | Unset):
        minimum_order_quantity (int | None | Unset):
        batch_size (int | None | Unset):
        stock_on_hand (float | None | Unset):
        stock_on_order (float | None | Unset):
        finished_good_stock_on_hand (float | None | Unset):
        finished_good_quantity_used (float | None | Unset):
        component_stock_on_hand (float | None | Unset):
        days_until_replenishment_due (int | None | Unset):
        days_until_stock_out (int | None | Unset):
        is_uncertain (bool | Unset):
        orders_in_previous_lead_time (float | Unset):
        avg_daily_orders_last_120_days (float | Unset):
        lead_demand_prediction_based_on_average (float | None | Unset):
        lead_demand_prediction_based_on_linear_regression (float | None | Unset):
        lead_demand_prediction_based_on_2_nd_order_polynomial_regression (float | None | Unset):
        lead_demand_prediction_based_on_last_month (float | None | Unset):
        lead_demand_prediction_based_on_previous_leadtime_days (float | None | Unset):
        standard_dev (float | None | Unset):
        service_factor (float | None | Unset):
        max_r_squared (float | None | Unset):
        min_r_squared (float | None | Unset):
        max_range (float | None | Unset):
        parent_quantity (float | None | Unset):
        most_accurate_algorithm_type_id (int | None | Unset):
        error_text (None | str | Unset):
        category (None | str | Unset):
        sub_category (None | str | Unset):
        brand (None | str | Unset):
        product_type (None | str | Unset):
        option1 (None | str | Unset):
        option2 (None | str | Unset):
        option3 (None | str | Unset):
        size (None | str | Unset):
        product_code (None | str | Unset):
        name (None | str | Unset):
        sku_cost (float | None | Unset):
        sku_price (float | None | Unset):
        is_discontinued (bool | Unset):
        is_unstocked (bool | Unset):
        product_of_count (int | Unset):
        component_of_count (int | Unset):
        customer_count (int | Unset):
        location_count (int | Unset):
        location_name (None | str | Unset):
        show_forecast_for_all_locations (bool | Unset):
        manufacturing_time (float | None | Unset):
        minimum_shelf_level (float | None | Unset):
        maximum_shelf_level (float | None | Unset):
        service_level (float | None | Unset):
        weight (float | None | Unset):
        height (float | None | Unset):
        width (float | None | Unset):
        length (float | None | Unset):
        dimensions_cubic_meters (float | None | Unset):
        external_id (None | str | Unset):
        sku_code (None | str | Unset):
        external_id_parent (None | str | Unset):
        sku_code_parent (None | str | Unset):
        child_variants_count (int | Unset):
    """

    id: int | Unset = UNSET
    sku_property_id: int | None | Unset = UNSET
    sku_id: int | None | Unset = UNSET
    location_id: int | None | Unset = UNSET
    channel_id: int | None | Unset = UNSET
    sku_grouping_id: int | None | Unset = UNSET
    sku_optimized_results_group_id: int | None | Unset = UNSET
    tenant_id: None | Unset | UUID = UNSET
    calculated_date_time: datetime.datetime | Unset = UNSET
    effective_to_date_time: datetime.datetime | None | Unset = UNSET
    reorder_point: float | None | Unset = UNSET
    order_quantity: float | None | Unset = UNSET
    lead_demand: float | None | Unset = UNSET
    forecast_period_demand: float | None | Unset = UNSET
    overridden_future_demand_effective_from_now: float | None | Unset = UNSET
    safety_stock_level: float | None | Unset = UNSET
    economic_order_quantity: float | None | Unset = UNSET
    optimial_stock_cycle: float | None | Unset = UNSET
    lead_time_days: int | None | Unset = UNSET
    reorder_frequency_days: int | None | Unset = UNSET
    order_count: int | Unset = UNSET
    latest_order_date: datetime.datetime | None | Unset = UNSET
    first_purchase_date: datetime.datetime | None | Unset = UNSET
    minimum_order_quantity: int | None | Unset = UNSET
    batch_size: int | None | Unset = UNSET
    stock_on_hand: float | None | Unset = UNSET
    stock_on_order: float | None | Unset = UNSET
    finished_good_stock_on_hand: float | None | Unset = UNSET
    finished_good_quantity_used: float | None | Unset = UNSET
    component_stock_on_hand: float | None | Unset = UNSET
    days_until_replenishment_due: int | None | Unset = UNSET
    days_until_stock_out: int | None | Unset = UNSET
    is_uncertain: bool | Unset = UNSET
    orders_in_previous_lead_time: float | Unset = UNSET
    avg_daily_orders_last_120_days: float | Unset = UNSET
    lead_demand_prediction_based_on_average: float | None | Unset = UNSET
    lead_demand_prediction_based_on_linear_regression: float | None | Unset = UNSET
    lead_demand_prediction_based_on_2_nd_order_polynomial_regression: (
        float | None | Unset
    ) = UNSET
    lead_demand_prediction_based_on_last_month: float | None | Unset = UNSET
    lead_demand_prediction_based_on_previous_leadtime_days: float | None | Unset = UNSET
    standard_dev: float | None | Unset = UNSET
    service_factor: float | None | Unset = UNSET
    max_r_squared: float | None | Unset = UNSET
    min_r_squared: float | None | Unset = UNSET
    max_range: float | None | Unset = UNSET
    parent_quantity: float | None | Unset = UNSET
    most_accurate_algorithm_type_id: int | None | Unset = UNSET
    error_text: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    sub_category: None | str | Unset = UNSET
    brand: None | str | Unset = UNSET
    product_type: None | str | Unset = UNSET
    option1: None | str | Unset = UNSET
    option2: None | str | Unset = UNSET
    option3: None | str | Unset = UNSET
    size: None | str | Unset = UNSET
    product_code: None | str | Unset = UNSET
    name: None | str | Unset = UNSET
    sku_cost: float | None | Unset = UNSET
    sku_price: float | None | Unset = UNSET
    is_discontinued: bool | Unset = UNSET
    is_unstocked: bool | Unset = UNSET
    product_of_count: int | Unset = UNSET
    component_of_count: int | Unset = UNSET
    customer_count: int | Unset = UNSET
    location_count: int | Unset = UNSET
    location_name: None | str | Unset = UNSET
    show_forecast_for_all_locations: bool | Unset = UNSET
    manufacturing_time: float | None | Unset = UNSET
    minimum_shelf_level: float | None | Unset = UNSET
    maximum_shelf_level: float | None | Unset = UNSET
    service_level: float | None | Unset = UNSET
    weight: float | None | Unset = UNSET
    height: float | None | Unset = UNSET
    width: float | None | Unset = UNSET
    length: float | None | Unset = UNSET
    dimensions_cubic_meters: float | None | Unset = UNSET
    external_id: None | str | Unset = UNSET
    sku_code: None | str | Unset = UNSET
    external_id_parent: None | str | Unset = UNSET
    sku_code_parent: None | str | Unset = UNSET
    child_variants_count: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        sku_property_id: int | None | Unset
        if isinstance(self.sku_property_id, Unset):
            sku_property_id = UNSET
        else:
            sku_property_id = self.sku_property_id

        sku_id: int | None | Unset
        if isinstance(self.sku_id, Unset):
            sku_id = UNSET
        else:
            sku_id = self.sku_id

        location_id: int | None | Unset
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        channel_id: int | None | Unset
        if isinstance(self.channel_id, Unset):
            channel_id = UNSET
        else:
            channel_id = self.channel_id

        sku_grouping_id: int | None | Unset
        if isinstance(self.sku_grouping_id, Unset):
            sku_grouping_id = UNSET
        else:
            sku_grouping_id = self.sku_grouping_id

        sku_optimized_results_group_id: int | None | Unset
        if isinstance(self.sku_optimized_results_group_id, Unset):
            sku_optimized_results_group_id = UNSET
        else:
            sku_optimized_results_group_id = self.sku_optimized_results_group_id

        tenant_id: None | str | Unset
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        elif isinstance(self.tenant_id, UUID):
            tenant_id = str(self.tenant_id)
        else:
            tenant_id = self.tenant_id

        calculated_date_time: str | Unset = UNSET
        if not isinstance(self.calculated_date_time, Unset):
            calculated_date_time = self.calculated_date_time.isoformat()

        effective_to_date_time: None | str | Unset
        if isinstance(self.effective_to_date_time, Unset):
            effective_to_date_time = UNSET
        elif isinstance(self.effective_to_date_time, datetime.datetime):
            effective_to_date_time = self.effective_to_date_time.isoformat()
        else:
            effective_to_date_time = self.effective_to_date_time

        reorder_point: float | None | Unset
        if isinstance(self.reorder_point, Unset):
            reorder_point = UNSET
        else:
            reorder_point = self.reorder_point

        order_quantity: float | None | Unset
        if isinstance(self.order_quantity, Unset):
            order_quantity = UNSET
        else:
            order_quantity = self.order_quantity

        lead_demand: float | None | Unset
        if isinstance(self.lead_demand, Unset):
            lead_demand = UNSET
        else:
            lead_demand = self.lead_demand

        forecast_period_demand: float | None | Unset
        if isinstance(self.forecast_period_demand, Unset):
            forecast_period_demand = UNSET
        else:
            forecast_period_demand = self.forecast_period_demand

        overridden_future_demand_effective_from_now: float | None | Unset
        if isinstance(self.overridden_future_demand_effective_from_now, Unset):
            overridden_future_demand_effective_from_now = UNSET
        else:
            overridden_future_demand_effective_from_now = (
                self.overridden_future_demand_effective_from_now
            )

        safety_stock_level: float | None | Unset
        if isinstance(self.safety_stock_level, Unset):
            safety_stock_level = UNSET
        else:
            safety_stock_level = self.safety_stock_level

        economic_order_quantity: float | None | Unset
        if isinstance(self.economic_order_quantity, Unset):
            economic_order_quantity = UNSET
        else:
            economic_order_quantity = self.economic_order_quantity

        optimial_stock_cycle: float | None | Unset
        if isinstance(self.optimial_stock_cycle, Unset):
            optimial_stock_cycle = UNSET
        else:
            optimial_stock_cycle = self.optimial_stock_cycle

        lead_time_days: int | None | Unset
        if isinstance(self.lead_time_days, Unset):
            lead_time_days = UNSET
        else:
            lead_time_days = self.lead_time_days

        reorder_frequency_days: int | None | Unset
        if isinstance(self.reorder_frequency_days, Unset):
            reorder_frequency_days = UNSET
        else:
            reorder_frequency_days = self.reorder_frequency_days

        order_count = self.order_count

        latest_order_date: None | str | Unset
        if isinstance(self.latest_order_date, Unset):
            latest_order_date = UNSET
        elif isinstance(self.latest_order_date, datetime.datetime):
            latest_order_date = self.latest_order_date.isoformat()
        else:
            latest_order_date = self.latest_order_date

        first_purchase_date: None | str | Unset
        if isinstance(self.first_purchase_date, Unset):
            first_purchase_date = UNSET
        elif isinstance(self.first_purchase_date, datetime.datetime):
            first_purchase_date = self.first_purchase_date.isoformat()
        else:
            first_purchase_date = self.first_purchase_date

        minimum_order_quantity: int | None | Unset
        if isinstance(self.minimum_order_quantity, Unset):
            minimum_order_quantity = UNSET
        else:
            minimum_order_quantity = self.minimum_order_quantity

        batch_size: int | None | Unset
        if isinstance(self.batch_size, Unset):
            batch_size = UNSET
        else:
            batch_size = self.batch_size

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

        finished_good_stock_on_hand: float | None | Unset
        if isinstance(self.finished_good_stock_on_hand, Unset):
            finished_good_stock_on_hand = UNSET
        else:
            finished_good_stock_on_hand = self.finished_good_stock_on_hand

        finished_good_quantity_used: float | None | Unset
        if isinstance(self.finished_good_quantity_used, Unset):
            finished_good_quantity_used = UNSET
        else:
            finished_good_quantity_used = self.finished_good_quantity_used

        component_stock_on_hand: float | None | Unset
        if isinstance(self.component_stock_on_hand, Unset):
            component_stock_on_hand = UNSET
        else:
            component_stock_on_hand = self.component_stock_on_hand

        days_until_replenishment_due: int | None | Unset
        if isinstance(self.days_until_replenishment_due, Unset):
            days_until_replenishment_due = UNSET
        else:
            days_until_replenishment_due = self.days_until_replenishment_due

        days_until_stock_out: int | None | Unset
        if isinstance(self.days_until_stock_out, Unset):
            days_until_stock_out = UNSET
        else:
            days_until_stock_out = self.days_until_stock_out

        is_uncertain = self.is_uncertain

        orders_in_previous_lead_time = self.orders_in_previous_lead_time

        avg_daily_orders_last_120_days = self.avg_daily_orders_last_120_days

        lead_demand_prediction_based_on_average: float | None | Unset
        if isinstance(self.lead_demand_prediction_based_on_average, Unset):
            lead_demand_prediction_based_on_average = UNSET
        else:
            lead_demand_prediction_based_on_average = (
                self.lead_demand_prediction_based_on_average
            )

        lead_demand_prediction_based_on_linear_regression: float | None | Unset
        if isinstance(self.lead_demand_prediction_based_on_linear_regression, Unset):
            lead_demand_prediction_based_on_linear_regression = UNSET
        else:
            lead_demand_prediction_based_on_linear_regression = (
                self.lead_demand_prediction_based_on_linear_regression
            )

        lead_demand_prediction_based_on_2_nd_order_polynomial_regression: (
            float | None | Unset
        )
        if isinstance(
            self.lead_demand_prediction_based_on_2_nd_order_polynomial_regression, Unset
        ):
            lead_demand_prediction_based_on_2_nd_order_polynomial_regression = UNSET
        else:
            lead_demand_prediction_based_on_2_nd_order_polynomial_regression = (
                self.lead_demand_prediction_based_on_2_nd_order_polynomial_regression
            )

        lead_demand_prediction_based_on_last_month: float | None | Unset
        if isinstance(self.lead_demand_prediction_based_on_last_month, Unset):
            lead_demand_prediction_based_on_last_month = UNSET
        else:
            lead_demand_prediction_based_on_last_month = (
                self.lead_demand_prediction_based_on_last_month
            )

        lead_demand_prediction_based_on_previous_leadtime_days: float | None | Unset
        if isinstance(
            self.lead_demand_prediction_based_on_previous_leadtime_days, Unset
        ):
            lead_demand_prediction_based_on_previous_leadtime_days = UNSET
        else:
            lead_demand_prediction_based_on_previous_leadtime_days = (
                self.lead_demand_prediction_based_on_previous_leadtime_days
            )

        standard_dev: float | None | Unset
        if isinstance(self.standard_dev, Unset):
            standard_dev = UNSET
        else:
            standard_dev = self.standard_dev

        service_factor: float | None | Unset
        if isinstance(self.service_factor, Unset):
            service_factor = UNSET
        else:
            service_factor = self.service_factor

        max_r_squared: float | None | Unset
        if isinstance(self.max_r_squared, Unset):
            max_r_squared = UNSET
        else:
            max_r_squared = self.max_r_squared

        min_r_squared: float | None | Unset
        if isinstance(self.min_r_squared, Unset):
            min_r_squared = UNSET
        else:
            min_r_squared = self.min_r_squared

        max_range: float | None | Unset
        if isinstance(self.max_range, Unset):
            max_range = UNSET
        else:
            max_range = self.max_range

        parent_quantity: float | None | Unset
        if isinstance(self.parent_quantity, Unset):
            parent_quantity = UNSET
        else:
            parent_quantity = self.parent_quantity

        most_accurate_algorithm_type_id: int | None | Unset
        if isinstance(self.most_accurate_algorithm_type_id, Unset):
            most_accurate_algorithm_type_id = UNSET
        else:
            most_accurate_algorithm_type_id = self.most_accurate_algorithm_type_id

        error_text: None | str | Unset
        if isinstance(self.error_text, Unset):
            error_text = UNSET
        else:
            error_text = self.error_text

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

        brand: None | str | Unset
        if isinstance(self.brand, Unset):
            brand = UNSET
        else:
            brand = self.brand

        product_type: None | str | Unset
        if isinstance(self.product_type, Unset):
            product_type = UNSET
        else:
            product_type = self.product_type

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

        size: None | str | Unset
        if isinstance(self.size, Unset):
            size = UNSET
        else:
            size = self.size

        product_code: None | str | Unset
        if isinstance(self.product_code, Unset):
            product_code = UNSET
        else:
            product_code = self.product_code

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        sku_cost: float | None | Unset
        if isinstance(self.sku_cost, Unset):
            sku_cost = UNSET
        else:
            sku_cost = self.sku_cost

        sku_price: float | None | Unset
        if isinstance(self.sku_price, Unset):
            sku_price = UNSET
        else:
            sku_price = self.sku_price

        is_discontinued = self.is_discontinued

        is_unstocked = self.is_unstocked

        product_of_count = self.product_of_count

        component_of_count = self.component_of_count

        customer_count = self.customer_count

        location_count = self.location_count

        location_name: None | str | Unset
        if isinstance(self.location_name, Unset):
            location_name = UNSET
        else:
            location_name = self.location_name

        show_forecast_for_all_locations = self.show_forecast_for_all_locations

        manufacturing_time: float | None | Unset
        if isinstance(self.manufacturing_time, Unset):
            manufacturing_time = UNSET
        else:
            manufacturing_time = self.manufacturing_time

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

        service_level: float | None | Unset
        if isinstance(self.service_level, Unset):
            service_level = UNSET
        else:
            service_level = self.service_level

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

        dimensions_cubic_meters: float | None | Unset
        if isinstance(self.dimensions_cubic_meters, Unset):
            dimensions_cubic_meters = UNSET
        else:
            dimensions_cubic_meters = self.dimensions_cubic_meters

        external_id: None | str | Unset
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        sku_code: None | str | Unset
        if isinstance(self.sku_code, Unset):
            sku_code = UNSET
        else:
            sku_code = self.sku_code

        external_id_parent: None | str | Unset
        if isinstance(self.external_id_parent, Unset):
            external_id_parent = UNSET
        else:
            external_id_parent = self.external_id_parent

        sku_code_parent: None | str | Unset
        if isinstance(self.sku_code_parent, Unset):
            sku_code_parent = UNSET
        else:
            sku_code_parent = self.sku_code_parent

        child_variants_count = self.child_variants_count

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if sku_property_id is not UNSET:
            field_dict["skuPropertyId"] = sku_property_id
        if sku_id is not UNSET:
            field_dict["skuId"] = sku_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if channel_id is not UNSET:
            field_dict["channelId"] = channel_id
        if sku_grouping_id is not UNSET:
            field_dict["skuGroupingId"] = sku_grouping_id
        if sku_optimized_results_group_id is not UNSET:
            field_dict["skuOptimizedResultsGroupId"] = sku_optimized_results_group_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if calculated_date_time is not UNSET:
            field_dict["calculatedDateTime"] = calculated_date_time
        if effective_to_date_time is not UNSET:
            field_dict["effectiveToDateTime"] = effective_to_date_time
        if reorder_point is not UNSET:
            field_dict["reorderPoint"] = reorder_point
        if order_quantity is not UNSET:
            field_dict["orderQuantity"] = order_quantity
        if lead_demand is not UNSET:
            field_dict["leadDemand"] = lead_demand
        if forecast_period_demand is not UNSET:
            field_dict["forecastPeriodDemand"] = forecast_period_demand
        if overridden_future_demand_effective_from_now is not UNSET:
            field_dict["overriddenFutureDemandEffectiveFromNow"] = (
                overridden_future_demand_effective_from_now
            )
        if safety_stock_level is not UNSET:
            field_dict["safetyStockLevel"] = safety_stock_level
        if economic_order_quantity is not UNSET:
            field_dict["economicOrderQuantity"] = economic_order_quantity
        if optimial_stock_cycle is not UNSET:
            field_dict["optimialStockCycle"] = optimial_stock_cycle
        if lead_time_days is not UNSET:
            field_dict["leadTimeDays"] = lead_time_days
        if reorder_frequency_days is not UNSET:
            field_dict["reorderFrequencyDays"] = reorder_frequency_days
        if order_count is not UNSET:
            field_dict["orderCount"] = order_count
        if latest_order_date is not UNSET:
            field_dict["latestOrderDate"] = latest_order_date
        if first_purchase_date is not UNSET:
            field_dict["firstPurchaseDate"] = first_purchase_date
        if minimum_order_quantity is not UNSET:
            field_dict["minimumOrderQuantity"] = minimum_order_quantity
        if batch_size is not UNSET:
            field_dict["batchSize"] = batch_size
        if stock_on_hand is not UNSET:
            field_dict["stockOnHand"] = stock_on_hand
        if stock_on_order is not UNSET:
            field_dict["stockOnOrder"] = stock_on_order
        if finished_good_stock_on_hand is not UNSET:
            field_dict["finishedGoodStockOnHand"] = finished_good_stock_on_hand
        if finished_good_quantity_used is not UNSET:
            field_dict["finishedGoodQuantityUsed"] = finished_good_quantity_used
        if component_stock_on_hand is not UNSET:
            field_dict["componentStockOnHand"] = component_stock_on_hand
        if days_until_replenishment_due is not UNSET:
            field_dict["daysUntilReplenishmentDue"] = days_until_replenishment_due
        if days_until_stock_out is not UNSET:
            field_dict["daysUntilStockOut"] = days_until_stock_out
        if is_uncertain is not UNSET:
            field_dict["isUncertain"] = is_uncertain
        if orders_in_previous_lead_time is not UNSET:
            field_dict["ordersInPreviousLeadTime"] = orders_in_previous_lead_time
        if avg_daily_orders_last_120_days is not UNSET:
            field_dict["avgDailyOrdersLast120Days"] = avg_daily_orders_last_120_days
        if lead_demand_prediction_based_on_average is not UNSET:
            field_dict["leadDemandPredictionBasedOnAverage"] = (
                lead_demand_prediction_based_on_average
            )
        if lead_demand_prediction_based_on_linear_regression is not UNSET:
            field_dict["leadDemandPredictionBasedOnLinearRegression"] = (
                lead_demand_prediction_based_on_linear_regression
            )
        if (
            lead_demand_prediction_based_on_2_nd_order_polynomial_regression
            is not UNSET
        ):
            field_dict["leadDemandPredictionBasedOn2ndOrderPolynomialRegression"] = (
                lead_demand_prediction_based_on_2_nd_order_polynomial_regression
            )
        if lead_demand_prediction_based_on_last_month is not UNSET:
            field_dict["leadDemandPredictionBasedOnLastMonth"] = (
                lead_demand_prediction_based_on_last_month
            )
        if lead_demand_prediction_based_on_previous_leadtime_days is not UNSET:
            field_dict["leadDemandPredictionBasedOnPreviousLeadtimeDays"] = (
                lead_demand_prediction_based_on_previous_leadtime_days
            )
        if standard_dev is not UNSET:
            field_dict["standardDev"] = standard_dev
        if service_factor is not UNSET:
            field_dict["serviceFactor"] = service_factor
        if max_r_squared is not UNSET:
            field_dict["maxRSquared"] = max_r_squared
        if min_r_squared is not UNSET:
            field_dict["minRSquared"] = min_r_squared
        if max_range is not UNSET:
            field_dict["maxRange"] = max_range
        if parent_quantity is not UNSET:
            field_dict["parentQuantity"] = parent_quantity
        if most_accurate_algorithm_type_id is not UNSET:
            field_dict["mostAccurateAlgorithmTypeId"] = most_accurate_algorithm_type_id
        if error_text is not UNSET:
            field_dict["errorText"] = error_text
        if category is not UNSET:
            field_dict["category"] = category
        if sub_category is not UNSET:
            field_dict["subCategory"] = sub_category
        if brand is not UNSET:
            field_dict["brand"] = brand
        if product_type is not UNSET:
            field_dict["productType"] = product_type
        if option1 is not UNSET:
            field_dict["option1"] = option1
        if option2 is not UNSET:
            field_dict["option2"] = option2
        if option3 is not UNSET:
            field_dict["option3"] = option3
        if size is not UNSET:
            field_dict["size"] = size
        if product_code is not UNSET:
            field_dict["productCode"] = product_code
        if name is not UNSET:
            field_dict["name"] = name
        if sku_cost is not UNSET:
            field_dict["skuCost"] = sku_cost
        if sku_price is not UNSET:
            field_dict["skuPrice"] = sku_price
        if is_discontinued is not UNSET:
            field_dict["isDiscontinued"] = is_discontinued
        if is_unstocked is not UNSET:
            field_dict["isUnstocked"] = is_unstocked
        if product_of_count is not UNSET:
            field_dict["productOfCount"] = product_of_count
        if component_of_count is not UNSET:
            field_dict["componentOfCount"] = component_of_count
        if customer_count is not UNSET:
            field_dict["customerCount"] = customer_count
        if location_count is not UNSET:
            field_dict["locationCount"] = location_count
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if show_forecast_for_all_locations is not UNSET:
            field_dict["showForecastForAllLocations"] = show_forecast_for_all_locations
        if manufacturing_time is not UNSET:
            field_dict["manufacturingTime"] = manufacturing_time
        if minimum_shelf_level is not UNSET:
            field_dict["minimumShelfLevel"] = minimum_shelf_level
        if maximum_shelf_level is not UNSET:
            field_dict["maximumShelfLevel"] = maximum_shelf_level
        if service_level is not UNSET:
            field_dict["serviceLevel"] = service_level
        if weight is not UNSET:
            field_dict["weight"] = weight
        if height is not UNSET:
            field_dict["height"] = height
        if width is not UNSET:
            field_dict["width"] = width
        if length is not UNSET:
            field_dict["length"] = length
        if dimensions_cubic_meters is not UNSET:
            field_dict["dimensionsCubicMeters"] = dimensions_cubic_meters
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if sku_code is not UNSET:
            field_dict["skuCode"] = sku_code
        if external_id_parent is not UNSET:
            field_dict["externalIdParent"] = external_id_parent
        if sku_code_parent is not UNSET:
            field_dict["skuCodeParent"] = sku_code_parent
        if child_variants_count is not UNSET:
            field_dict["childVariantsCount"] = child_variants_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        def _parse_sku_property_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        sku_property_id = _parse_sku_property_id(d.pop("skuPropertyId", UNSET))

        def _parse_sku_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        sku_id = _parse_sku_id(d.pop("skuId", UNSET))

        def _parse_location_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        location_id = _parse_location_id(d.pop("locationId", UNSET))

        def _parse_channel_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        channel_id = _parse_channel_id(d.pop("channelId", UNSET))

        def _parse_sku_grouping_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        sku_grouping_id = _parse_sku_grouping_id(d.pop("skuGroupingId", UNSET))

        def _parse_sku_optimized_results_group_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        sku_optimized_results_group_id = _parse_sku_optimized_results_group_id(
            d.pop("skuOptimizedResultsGroupId", UNSET)
        )

        def _parse_tenant_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                tenant_id_type_0 = UUID(data)

                return tenant_id_type_0
            except:  # noqa: E722
                pass
            return cast(None | Unset | UUID, data)

        tenant_id = _parse_tenant_id(d.pop("tenantId", UNSET))

        _calculated_date_time = d.pop("calculatedDateTime", UNSET)
        calculated_date_time: datetime.datetime | Unset
        if isinstance(_calculated_date_time, Unset):
            calculated_date_time = UNSET
        else:
            calculated_date_time = isoparse(_calculated_date_time)

        def _parse_effective_to_date_time(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                effective_to_date_time_type_0 = isoparse(data)

                return effective_to_date_time_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        effective_to_date_time = _parse_effective_to_date_time(
            d.pop("effectiveToDateTime", UNSET)
        )

        def _parse_reorder_point(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        reorder_point = _parse_reorder_point(d.pop("reorderPoint", UNSET))

        def _parse_order_quantity(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        order_quantity = _parse_order_quantity(d.pop("orderQuantity", UNSET))

        def _parse_lead_demand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand = _parse_lead_demand(d.pop("leadDemand", UNSET))

        def _parse_forecast_period_demand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        forecast_period_demand = _parse_forecast_period_demand(
            d.pop("forecastPeriodDemand", UNSET)
        )

        def _parse_overridden_future_demand_effective_from_now(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        overridden_future_demand_effective_from_now = (
            _parse_overridden_future_demand_effective_from_now(
                d.pop("overriddenFutureDemandEffectiveFromNow", UNSET)
            )
        )

        def _parse_safety_stock_level(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        safety_stock_level = _parse_safety_stock_level(d.pop("safetyStockLevel", UNSET))

        def _parse_economic_order_quantity(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        economic_order_quantity = _parse_economic_order_quantity(
            d.pop("economicOrderQuantity", UNSET)
        )

        def _parse_optimial_stock_cycle(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        optimial_stock_cycle = _parse_optimial_stock_cycle(
            d.pop("optimialStockCycle", UNSET)
        )

        def _parse_lead_time_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        lead_time_days = _parse_lead_time_days(d.pop("leadTimeDays", UNSET))

        def _parse_reorder_frequency_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        reorder_frequency_days = _parse_reorder_frequency_days(
            d.pop("reorderFrequencyDays", UNSET)
        )

        order_count = d.pop("orderCount", UNSET)

        def _parse_latest_order_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                latest_order_date_type_0 = isoparse(data)

                return latest_order_date_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        latest_order_date = _parse_latest_order_date(d.pop("latestOrderDate", UNSET))

        def _parse_first_purchase_date(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                first_purchase_date_type_0 = isoparse(data)

                return first_purchase_date_type_0
            except:  # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        first_purchase_date = _parse_first_purchase_date(
            d.pop("firstPurchaseDate", UNSET)
        )

        def _parse_minimum_order_quantity(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        minimum_order_quantity = _parse_minimum_order_quantity(
            d.pop("minimumOrderQuantity", UNSET)
        )

        def _parse_batch_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        batch_size = _parse_batch_size(d.pop("batchSize", UNSET))

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

        def _parse_finished_good_stock_on_hand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        finished_good_stock_on_hand = _parse_finished_good_stock_on_hand(
            d.pop("finishedGoodStockOnHand", UNSET)
        )

        def _parse_finished_good_quantity_used(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        finished_good_quantity_used = _parse_finished_good_quantity_used(
            d.pop("finishedGoodQuantityUsed", UNSET)
        )

        def _parse_component_stock_on_hand(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        component_stock_on_hand = _parse_component_stock_on_hand(
            d.pop("componentStockOnHand", UNSET)
        )

        def _parse_days_until_replenishment_due(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days_until_replenishment_due = _parse_days_until_replenishment_due(
            d.pop("daysUntilReplenishmentDue", UNSET)
        )

        def _parse_days_until_stock_out(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days_until_stock_out = _parse_days_until_stock_out(
            d.pop("daysUntilStockOut", UNSET)
        )

        is_uncertain = d.pop("isUncertain", UNSET)

        orders_in_previous_lead_time = d.pop("ordersInPreviousLeadTime", UNSET)

        avg_daily_orders_last_120_days = d.pop("avgDailyOrdersLast120Days", UNSET)

        def _parse_lead_demand_prediction_based_on_average(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand_prediction_based_on_average = (
            _parse_lead_demand_prediction_based_on_average(
                d.pop("leadDemandPredictionBasedOnAverage", UNSET)
            )
        )

        def _parse_lead_demand_prediction_based_on_linear_regression(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand_prediction_based_on_linear_regression = (
            _parse_lead_demand_prediction_based_on_linear_regression(
                d.pop("leadDemandPredictionBasedOnLinearRegression", UNSET)
            )
        )

        def _parse_lead_demand_prediction_based_on_2_nd_order_polynomial_regression(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand_prediction_based_on_2_nd_order_polynomial_regression = (
            _parse_lead_demand_prediction_based_on_2_nd_order_polynomial_regression(
                d.pop("leadDemandPredictionBasedOn2ndOrderPolynomialRegression", UNSET)
            )
        )

        def _parse_lead_demand_prediction_based_on_last_month(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand_prediction_based_on_last_month = (
            _parse_lead_demand_prediction_based_on_last_month(
                d.pop("leadDemandPredictionBasedOnLastMonth", UNSET)
            )
        )

        def _parse_lead_demand_prediction_based_on_previous_leadtime_days(
            data: object,
        ) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lead_demand_prediction_based_on_previous_leadtime_days = (
            _parse_lead_demand_prediction_based_on_previous_leadtime_days(
                d.pop("leadDemandPredictionBasedOnPreviousLeadtimeDays", UNSET)
            )
        )

        def _parse_standard_dev(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        standard_dev = _parse_standard_dev(d.pop("standardDev", UNSET))

        def _parse_service_factor(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        service_factor = _parse_service_factor(d.pop("serviceFactor", UNSET))

        def _parse_max_r_squared(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_r_squared = _parse_max_r_squared(d.pop("maxRSquared", UNSET))

        def _parse_min_r_squared(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_r_squared = _parse_min_r_squared(d.pop("minRSquared", UNSET))

        def _parse_max_range(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_range = _parse_max_range(d.pop("maxRange", UNSET))

        def _parse_parent_quantity(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        parent_quantity = _parse_parent_quantity(d.pop("parentQuantity", UNSET))

        def _parse_most_accurate_algorithm_type_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        most_accurate_algorithm_type_id = _parse_most_accurate_algorithm_type_id(
            d.pop("mostAccurateAlgorithmTypeId", UNSET)
        )

        def _parse_error_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_text = _parse_error_text(d.pop("errorText", UNSET))

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

        def _parse_brand(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        brand = _parse_brand(d.pop("brand", UNSET))

        def _parse_product_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        product_type = _parse_product_type(d.pop("productType", UNSET))

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

        def _parse_size(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        size = _parse_size(d.pop("size", UNSET))

        def _parse_product_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        product_code = _parse_product_code(d.pop("productCode", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_sku_cost(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        sku_cost = _parse_sku_cost(d.pop("skuCost", UNSET))

        def _parse_sku_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        sku_price = _parse_sku_price(d.pop("skuPrice", UNSET))

        is_discontinued = d.pop("isDiscontinued", UNSET)

        is_unstocked = d.pop("isUnstocked", UNSET)

        product_of_count = d.pop("productOfCount", UNSET)

        component_of_count = d.pop("componentOfCount", UNSET)

        customer_count = d.pop("customerCount", UNSET)

        location_count = d.pop("locationCount", UNSET)

        def _parse_location_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location_name = _parse_location_name(d.pop("locationName", UNSET))

        show_forecast_for_all_locations = d.pop("showForecastForAllLocations", UNSET)

        def _parse_manufacturing_time(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        manufacturing_time = _parse_manufacturing_time(
            d.pop("manufacturingTime", UNSET)
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

        def _parse_service_level(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        service_level = _parse_service_level(d.pop("serviceLevel", UNSET))

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

        def _parse_dimensions_cubic_meters(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        dimensions_cubic_meters = _parse_dimensions_cubic_meters(
            d.pop("dimensionsCubicMeters", UNSET)
        )

        def _parse_external_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_sku_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sku_code = _parse_sku_code(d.pop("skuCode", UNSET))

        def _parse_external_id_parent(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_id_parent = _parse_external_id_parent(d.pop("externalIdParent", UNSET))

        def _parse_sku_code_parent(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sku_code_parent = _parse_sku_code_parent(d.pop("skuCodeParent", UNSET))

        child_variants_count = d.pop("childVariantsCount", UNSET)

        sku_optimized_results_dto = cls(
            id=id,
            sku_property_id=sku_property_id,
            sku_id=sku_id,
            location_id=location_id,
            channel_id=channel_id,
            sku_grouping_id=sku_grouping_id,
            sku_optimized_results_group_id=sku_optimized_results_group_id,
            tenant_id=tenant_id,
            calculated_date_time=calculated_date_time,
            effective_to_date_time=effective_to_date_time,
            reorder_point=reorder_point,
            order_quantity=order_quantity,
            lead_demand=lead_demand,
            forecast_period_demand=forecast_period_demand,
            overridden_future_demand_effective_from_now=overridden_future_demand_effective_from_now,
            safety_stock_level=safety_stock_level,
            economic_order_quantity=economic_order_quantity,
            optimial_stock_cycle=optimial_stock_cycle,
            lead_time_days=lead_time_days,
            reorder_frequency_days=reorder_frequency_days,
            order_count=order_count,
            latest_order_date=latest_order_date,
            first_purchase_date=first_purchase_date,
            minimum_order_quantity=minimum_order_quantity,
            batch_size=batch_size,
            stock_on_hand=stock_on_hand,
            stock_on_order=stock_on_order,
            finished_good_stock_on_hand=finished_good_stock_on_hand,
            finished_good_quantity_used=finished_good_quantity_used,
            component_stock_on_hand=component_stock_on_hand,
            days_until_replenishment_due=days_until_replenishment_due,
            days_until_stock_out=days_until_stock_out,
            is_uncertain=is_uncertain,
            orders_in_previous_lead_time=orders_in_previous_lead_time,
            avg_daily_orders_last_120_days=avg_daily_orders_last_120_days,
            lead_demand_prediction_based_on_average=lead_demand_prediction_based_on_average,
            lead_demand_prediction_based_on_linear_regression=lead_demand_prediction_based_on_linear_regression,
            lead_demand_prediction_based_on_2_nd_order_polynomial_regression=lead_demand_prediction_based_on_2_nd_order_polynomial_regression,
            lead_demand_prediction_based_on_last_month=lead_demand_prediction_based_on_last_month,
            lead_demand_prediction_based_on_previous_leadtime_days=lead_demand_prediction_based_on_previous_leadtime_days,
            standard_dev=standard_dev,
            service_factor=service_factor,
            max_r_squared=max_r_squared,
            min_r_squared=min_r_squared,
            max_range=max_range,
            parent_quantity=parent_quantity,
            most_accurate_algorithm_type_id=most_accurate_algorithm_type_id,
            error_text=error_text,
            category=category,
            sub_category=sub_category,
            brand=brand,
            product_type=product_type,
            option1=option1,
            option2=option2,
            option3=option3,
            size=size,
            product_code=product_code,
            name=name,
            sku_cost=sku_cost,
            sku_price=sku_price,
            is_discontinued=is_discontinued,
            is_unstocked=is_unstocked,
            product_of_count=product_of_count,
            component_of_count=component_of_count,
            customer_count=customer_count,
            location_count=location_count,
            location_name=location_name,
            show_forecast_for_all_locations=show_forecast_for_all_locations,
            manufacturing_time=manufacturing_time,
            minimum_shelf_level=minimum_shelf_level,
            maximum_shelf_level=maximum_shelf_level,
            service_level=service_level,
            weight=weight,
            height=height,
            width=width,
            length=length,
            dimensions_cubic_meters=dimensions_cubic_meters,
            external_id=external_id,
            sku_code=sku_code,
            external_id_parent=external_id_parent,
            sku_code_parent=sku_code_parent,
            child_variants_count=child_variants_count,
        )

        return sku_optimized_results_dto
