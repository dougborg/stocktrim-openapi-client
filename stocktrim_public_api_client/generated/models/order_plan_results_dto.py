from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_plan_filter_criteria import OrderPlanFilterCriteria
    from ..models.sku_optimized_results_dto import SkuOptimizedResultsDto


T = TypeVar("T", bound="OrderPlanResultsDto")


@_attrs_define
class OrderPlanResultsDto:
    """
    Attributes:
        results (Union[None, Unset, list['SkuOptimizedResultsDto']]):
        filter_criteria (Union[Unset, OrderPlanFilterCriteria]):
    """

    results: Union[None, Unset, list["SkuOptimizedResultsDto"]] = UNSET
    filter_criteria: Union[Unset, "OrderPlanFilterCriteria"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        results: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.results, Unset):
            results = UNSET
        elif isinstance(self.results, list):
            results = []
            for results_type_0_item_data in self.results:
                results_type_0_item = results_type_0_item_data.to_dict()
                results.append(results_type_0_item)

        else:
            results = self.results

        filter_criteria: Union[Unset, dict[str, Any]] = UNSET
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

        def _parse_results(data: object) -> Union[None, Unset, list["SkuOptimizedResultsDto"]]:
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
                    results_type_0_item = SkuOptimizedResultsDto.from_dict(results_type_0_item_data)

                    results_type_0.append(results_type_0_item)

                return results_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["SkuOptimizedResultsDto"]], data)

        results = _parse_results(d.pop("results", UNSET))

        _filter_criteria = d.pop("filterCriteria", UNSET)
        filter_criteria: Union[Unset, OrderPlanFilterCriteria]
        if isinstance(_filter_criteria, Unset):
            filter_criteria = UNSET
        else:
            filter_criteria = OrderPlanFilterCriteria.from_dict(_filter_criteria)

        order_plan_results_dto = cls(
            results=results,
            filter_criteria=filter_criteria,
        )

        return order_plan_results_dto
