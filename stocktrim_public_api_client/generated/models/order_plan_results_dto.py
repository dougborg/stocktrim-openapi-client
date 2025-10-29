from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ...client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_plan_filter_criteria import OrderPlanFilterCriteria
    from ..models.sku_optimized_results_dto import SkuOptimizedResultsDto


T = TypeVar("T", bound="OrderPlanResultsDto")


@_attrs_define
class OrderPlanResultsDto:
    """
    Attributes:
        results (list[SkuOptimizedResultsDto] | None | Unset):
        filter_criteria (OrderPlanFilterCriteria | Unset):
    """

    results: list[SkuOptimizedResultsDto] | None | Unset = UNSET
    filter_criteria: OrderPlanFilterCriteria | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        results: list[dict[str, Any]] | None | Unset
        if isinstance(self.results, Unset):
            results = UNSET
        elif isinstance(self.results, list):
            results = []
            for results_type_0_item_data in self.results:
                results_type_0_item = results_type_0_item_data.to_dict()
                results.append(results_type_0_item)

        else:
            results = self.results

        filter_criteria: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filter_criteria, Unset):
            filter_criteria = self.filter_criteria.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if results is not UNSET:
            field_dict["results"] = results
        if filter_criteria is not UNSET:
            field_dict["filterCriteria"] = filter_criteria

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_plan_filter_criteria import OrderPlanFilterCriteria
        from ..models.sku_optimized_results_dto import SkuOptimizedResultsDto

        d = dict(src_dict)

        def _parse_results(data: object) -> list[SkuOptimizedResultsDto] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                results_type_0 = []
                _results_type_0 = data
                for results_type_0_item_data in _results_type_0:
                    results_type_0_item = SkuOptimizedResultsDto.from_dict(
                        cast(Mapping[str, Any], results_type_0_item_data)
                    )

                    results_type_0.append(results_type_0_item)

                return results_type_0
            except:  # noqa: E722
                pass
            return cast(list[SkuOptimizedResultsDto] | None | Unset, data)

        results = _parse_results(d.pop("results", UNSET))

        _filter_criteria = d.pop("filterCriteria", UNSET)
        filter_criteria: OrderPlanFilterCriteria | Unset
        if isinstance(_filter_criteria, Unset):
            filter_criteria = UNSET
        else:
            filter_criteria = OrderPlanFilterCriteria.from_dict(
                cast(Mapping[str, Any], _filter_criteria)
            )

        order_plan_results_dto = cls(
            results=results,
            filter_criteria=filter_criteria,
        )

        return order_plan_results_dto
