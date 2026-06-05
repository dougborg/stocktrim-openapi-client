"""Tests for the Assemblies helper and product variant expansion.

These cover the "treat bike frames as purchased" reconciliation: detecting
intermediate assemblies in a multi-level BOM (complete bike -> frame -> parts),
stripping the frame's own sub-BOM while preserving the bike -> frame link,
expanding to sibling variants, and triggering a recalc.

Mocks are at the helper boundary (client.bill_of_materials / client.products /
client.forecasting), matching the style used elsewhere in the suite.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_public_api_client.generated.models.bill_of_materials_response_dto import (
    BillOfMaterialsResponseDto,
)
from stocktrim_public_api_client.generated.models.products_response_dto import (
    ProductsResponseDto,
)
from stocktrim_public_api_client.helpers.assemblies import (
    Assemblies,
    PurchasedAssemblyResult,
)
from stocktrim_public_api_client.helpers.products import Products, is_variant_match


def _bom(product_id: str, component_id: str) -> BillOfMaterialsResponseDto:
    return BillOfMaterialsResponseDto(
        product_id=product_id, component_id=component_id, quantity=1.0
    )


def _make_boms_mock(graph: dict[str, list[str]]) -> Mock:
    """Build a mock bill_of_materials helper from a parent -> components graph.

    ``get_for_product(pid)`` returns rows for ``graph[pid]``; ``get()`` (no args)
    returns every edge; ``delete`` is an AsyncMock that mutates the graph so the
    helper is observably idempotent on re-run.
    """
    boms = Mock()

    async def get_for_product(product_id: str) -> list[BillOfMaterialsResponseDto]:
        return [_bom(product_id, c) for c in graph.get(product_id, [])]

    async def get(
        product_id=None, component_id=None
    ) -> list[BillOfMaterialsResponseDto]:
        return [_bom(p, c) for p, comps in graph.items() for c in comps]

    async def delete(product_id: str, component_id: str) -> None:
        graph[product_id] = [c for c in graph.get(product_id, []) if c != component_id]

    boms.get_for_product = AsyncMock(side_effect=get_for_product)
    boms.get = AsyncMock(side_effect=get)
    boms.delete = AsyncMock(side_effect=delete)
    return boms


def _client_with(graph: dict[str, list[str]], catalog=None) -> Mock:
    client = Mock()
    client.bill_of_materials = _make_boms_mock(graph)
    client.forecasting = Mock()
    client.forecasting.run_calculations = AsyncMock()
    products = Mock()
    products.get_all_paginated = AsyncMock(return_value=catalog or [])
    client.products = products
    return client


# Topology used by most tests:
#   BIKE -> FRAME, WHEEL          (complete bike)
#   FRAME -> TUBE, LUG            (frame is itself an assembly -> buy-it-whole)
def _bike_graph() -> dict[str, list[str]]:
    return {
        "BIKE": ["FRAME", "WHEEL"],
        "FRAME": ["TUBE", "LUG"],
    }


@pytest.mark.asyncio
async def test_detect_finished_goods_returns_roots():
    client = _client_with(_bike_graph())
    assemblies = Assemblies(client)

    # BIKE is a parent but never a component -> it is the only root.
    assert await assemblies.detect_finished_goods() == ["BIKE"]


@pytest.mark.asyncio
async def test_detect_purchased_assemblies_finds_frame():
    client = _client_with(_bike_graph())
    assemblies = Assemblies(client)

    # FRAME is a component of BIKE *and* has its own sub-BOM -> intermediate.
    # WHEEL is a component with no sub-BOM -> not an assembly.
    assert await assemblies.detect_purchased_assemblies(["BIKE"]) == ["FRAME"]


@pytest.mark.asyncio
async def test_make_purchased_strips_only_own_sub_bom():
    graph = _bike_graph()
    client = _client_with(graph)
    assemblies = Assemblies(client)

    result = await assemblies.make_purchased("FRAME")

    assert isinstance(result, PurchasedAssemblyResult)
    assert result.changed is True
    assert sorted(result.removed_components) == ["LUG", "TUBE"]
    # FRAME's sub-BOM is gone; the BIKE -> FRAME link is untouched.
    assert graph["FRAME"] == []
    assert graph["BIKE"] == ["FRAME", "WHEEL"]
    client.bill_of_materials.delete.assert_any_call(
        product_id="FRAME", component_id="TUBE"
    )


@pytest.mark.asyncio
async def test_make_purchased_is_idempotent():
    graph = _bike_graph()
    client = _client_with(graph)
    assemblies = Assemblies(client)

    await assemblies.make_purchased("FRAME")
    second = await assemblies.make_purchased("FRAME")

    assert second.changed is False
    assert second.removed_components == []


@pytest.mark.asyncio
async def test_reconcile_strips_frame_and_triggers_recalc():
    graph = _bike_graph()
    client = _client_with(graph)
    assemblies = Assemblies(client)

    summary = await assemblies.reconcile_purchased_assemblies(
        expand_variants=False, run_forecast=True
    )

    assert summary.detected == ["FRAME"]
    assert summary.total_removed == 2
    assert graph["FRAME"] == []
    # BIKE -> FRAME demand path preserved.
    assert graph["BIKE"] == ["FRAME", "WHEEL"]
    client.forecasting.run_calculations.assert_awaited_once()


@pytest.mark.asyncio
async def test_reconcile_skips_recalc_when_nothing_changed():
    # No intermediate assemblies: BIKE -> WHEEL only, WHEEL has no sub-BOM.
    graph = {"BIKE": ["WHEEL"]}
    client = _client_with(graph)
    assemblies = Assemblies(client)

    summary = await assemblies.reconcile_purchased_assemblies(run_forecast=True)

    assert summary.changed == []
    client.forecasting.run_calculations.assert_not_awaited()


@pytest.mark.asyncio
async def test_reconcile_expands_to_sibling_variants():
    # FRAME and FRAME-L are size variants sharing parent FRAME-FAMILY. Only FRAME
    # is referenced by a bike BOM, but expansion should also strip FRAME-L.
    graph = {
        "BIKE": ["FRAME"],
        "FRAME": ["TUBE"],
        "FRAME-L": ["TUBE"],
    }
    catalog = [
        ProductsResponseDto(product_id="FRAME", parent_id="FRAME-FAMILY"),
        ProductsResponseDto(product_id="FRAME-L", parent_id="FRAME-FAMILY"),
        ProductsResponseDto(product_id="WHEEL", parent_id="WHEEL-FAMILY"),
    ]
    client = _client_with(graph, catalog=catalog)
    assemblies = Assemblies(client)

    summary = await assemblies.reconcile_purchased_assemblies(expand_variants=True)

    assert summary.detected == ["FRAME"]
    changed_ids = sorted(r.product_id for r in summary.changed)
    assert changed_ids == ["FRAME", "FRAME-L"]
    assert graph["FRAME"] == []
    assert graph["FRAME-L"] == []


@pytest.mark.asyncio
async def test_find_variants_filters_catalog(monkeypatch):
    catalog = [
        ProductsResponseDto(product_id="FRAME", parent_id="FRAME-FAMILY"),
        ProductsResponseDto(product_id="FRAME-L", parent_id="FRAME-FAMILY"),
        ProductsResponseDto(product_id="WHEEL", parent_id="WHEEL-FAMILY"),
    ]
    products = Products(Mock())
    monkeypatch.setattr(products, "get_all_paginated", AsyncMock(return_value=catalog))

    variants = await products.find_variants(parent_id="FRAME-FAMILY")

    assert sorted(p.product_id for p in variants) == ["FRAME", "FRAME-L"]


@pytest.mark.asyncio
async def test_find_variants_requires_a_filter():
    products = Products(Mock())
    with pytest.raises(ValueError, match="parent_id and/or variant_type"):
        await products.find_variants()


def test_is_variant_match_predicate():
    product = ProductsResponseDto(
        product_id="FRAME", parent_id="FRAME-FAMILY", variant_type="SIZE"
    )
    assert is_variant_match(product, parent_id="FRAME-FAMILY") is True
    assert is_variant_match(product, parent_id="OTHER") is False
    assert is_variant_match(product, variant_type="SIZE") is True
    assert is_variant_match(product, variant_type="COLOR") is False
    # No filters -> vacuously matches.
    assert is_variant_match(product) is True
