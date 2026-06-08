"""Assembly (BOM hierarchy) operations for purchased-vs-manufactured handling.

Context: when StockTrim holds a multi-level BOM (e.g. complete bike -> frame ->
frame parts), it explodes every level and generates purchase demand for the
deepest components. For assemblies we buy whole (frames), we want explosion to
stop at the assembly: keep its demand (it still rolls up from its parent BOM) and
order it directly, but not generate demand for its sub-parts.

StockTrim exposes no "is manufactured" flag; a product is treated as manufactured
because it is itself a BOM parent. Removing an assembly's own sub-BOM (while
leaving the parent -> assembly link intact) makes it behave as a purchased item.

NOTE: this mechanism (sub-BOM strip) is the primary hypothesis pending live
verification on a real frame SKU (Phase 0 of the plan). If verification shows
``manufacturing_time`` is the actual lever instead, swap the body of
``make_purchased`` — the detection and reconciliation logic is unaffected.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from stocktrim_public_api_client.helpers.base import Base
from stocktrim_public_api_client.utils import unwrap_unset


@dataclass
class BomGraph:
    """A snapshot of the whole BOM graph fetched in a single call.

    Attributes:
        children: Maps a product ID to the component IDs it directly contains.
        parents: All product IDs that are a BOM parent (have a sub-BOM).
        components: All product IDs that appear as a component of something.
    """

    children: dict[str, list[str]]
    parents: set[str]
    components: set[str]


@dataclass
class PurchasedAssemblyResult:
    """Outcome of a :meth:`Assemblies.make_purchased` call for one assembly."""

    product_id: str
    removed_components: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        """True if any sub-BOM rows were removed."""
        return bool(self.removed_components)


@dataclass
class ReconcileSummary:
    """Aggregate outcome of a reconciliation run."""

    detected: list[str]
    results: list[PurchasedAssemblyResult]

    @property
    def changed(self) -> list[PurchasedAssemblyResult]:
        """Results that actually removed sub-BOM rows."""
        return [result for result in self.results if result.changed]

    @property
    def total_removed(self) -> int:
        """Total number of sub-BOM rows removed across all assemblies."""
        return sum(len(result.removed_components) for result in self.results)


class Assemblies(Base):
    """Treat intermediate assemblies as purchased items.

    See module docstring for the rationale. The typical entry point is
    :meth:`reconcile_purchased_assemblies`, which is idempotent and safe to run
    on a schedule after each Katana import.
    """

    async def load_bom_graph(self) -> BomGraph:
        """Fetch the entire BOM graph in one call.

        Returns:
            A :class:`BomGraph` snapshot (children map + parent/component sets).
        """
        children: dict[str, list[str]] = defaultdict(list)
        parents: set[str] = set()
        components: set[str] = set()
        for bom in await self._client.bill_of_materials.get():
            children[bom.product_id].append(bom.component_id)
            parents.add(bom.product_id)
            components.add(bom.component_id)
        return BomGraph(children=dict(children), parents=parents, components=components)

    async def detect_finished_goods(self) -> list[str]:
        """Find top-level finished goods: BOM parents that are never components.

        Returns product IDs that appear as a BOM parent but never as a component
        of anything else (the roots of the tree, e.g. complete bikes). Useful for
        seeding reconciliation without enumerating finished goods by hand.

        Returns:
            Sorted, de-duplicated list of finished-good (root) product IDs.
        """
        graph = await self.load_bom_graph()
        return sorted(graph.parents - graph.components)

    async def detect_purchased_assemblies(
        self,
        finished_good_ids: list[str],
    ) -> list[str]:
        """Find intermediate assemblies in the subtree under the finished goods.

        Walks the BOM tree below each finished good (to any depth) and returns
        every descendant that is itself a BOM parent — i.e. has its own sub-BOM.
        These are the "buy-it-whole" assemblies (e.g. frames) whose sub-BOM
        should be stripped.

        The ``finished_good_ids`` are traversal seeds, not results: a seed is
        returned only if it reappears as a descendant of another node, which can
        happen only in a cyclic graph. In an acyclic tree the finished goods are
        never returned, so their top-level BOM (e.g. bike -> frame) is preserved.
        Cycle-safe (each node is visited at most once).

        Args:
            finished_good_ids: Product IDs of finished goods (e.g. complete bikes).

        Returns:
            Sorted, de-duplicated list of intermediate-assembly product IDs.
        """
        graph = await self.load_bom_graph()
        assemblies: set[str] = set()
        seen: set[str] = set()
        stack = list(finished_good_ids)
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            for child in graph.children.get(node, []):
                if child in graph.parents:
                    assemblies.add(child)
                stack.append(child)
        return sorted(assemblies)

    async def make_purchased(self, product_id: str) -> PurchasedAssemblyResult:
        """Make an assembly behave as purchased by removing its own sub-BOM.

        Deletes every BOM row where ``product_id`` is the parent. The product's
        usage as a component of higher-level BOMs is untouched, so its demand
        still rolls up from those parents. Idempotent: a product with no sub-BOM
        is a no-op.

        Args:
            product_id: The assembly (e.g. frame) to convert to purchased.

        Returns:
            PurchasedAssemblyResult listing the component IDs that were removed.
        """
        boms = self._client.bill_of_materials
        result = PurchasedAssemblyResult(product_id=product_id)
        for row in await boms.get_for_product(product_id):
            await boms.delete(product_id=product_id, component_id=row.component_id)
            result.removed_components.append(row.component_id)
        return result

    async def reconcile_purchased_assemblies(
        self,
        finished_good_ids: list[str] | None = None,
        expand_variants: bool = True,
        run_forecast: bool = True,
    ) -> ReconcileSummary:
        """Detect buy-it-whole assemblies, strip their sub-BOMs, and recalc.

        End-to-end reconciliation:

        1. Detect intermediate assemblies under ``finished_good_ids``.
        2. Optionally expand each detected assembly to all sibling variants that
           share its ``parent_id`` (the variant-relationship selector), so every
           size/colour variant of a frame family is covered.
        3. Strip each target's own sub-BOM (``make_purchased``).
        4. Optionally trigger a forecast recalculation so the order plan reflects
           the change — this supersedes the auto-recalc that StockTrim runs
           immediately after a Katana import.

        Idempotent: re-running after no new drift removes nothing and (if
        ``run_forecast``) simply recomputes the same plan.

        Args:
            finished_good_ids: Product IDs of finished goods (e.g. complete bikes).
                If ``None``, finished goods are auto-detected as BOM roots via
                :meth:`detect_finished_goods`.
            expand_variants: Expand detected assemblies to sibling variants via
                ``parent_id``.
            run_forecast: Trigger ``forecasting.run_calculations()`` at the end.

        Returns:
            ReconcileSummary describing what was detected and removed.
        """
        if finished_good_ids is None:
            finished_good_ids = await self.detect_finished_goods()

        detected = await self.detect_purchased_assemblies(finished_good_ids)
        targets: set[str] = set(detected)

        if expand_variants and detected:
            targets |= await self._expand_variants(detected)

        results = [
            await self.make_purchased(product_id) for product_id in sorted(targets)
        ]

        summary = ReconcileSummary(detected=detected, results=results)

        if run_forecast and summary.changed:
            await self._client.forecasting.run_calculations()

        return summary

    async def _expand_variants(self, assembly_ids: list[str]) -> set[str]:
        """Return all sibling variant IDs sharing a parent with the given assemblies.

        Fetches the catalog once and builds a single ``parent_id -> [product_id]``
        index, so each detected assembly is resolved to its family by one dict
        lookup (O(catalog + assemblies)) rather than a full re-scan per assembly.
        """
        catalog = await self._client.products.get_all_paginated()

        by_id: dict[str, str | None] = {}
        siblings_by_parent: dict[str, list[str]] = defaultdict(list)
        for product in catalog:
            parent_id = unwrap_unset(product.parent_id)
            by_id[product.product_id] = parent_id
            if parent_id is not None:
                siblings_by_parent[parent_id].append(product.product_id)

        variant_ids: set[str] = set()
        for assembly_id in assembly_ids:
            parent_id = by_id.get(assembly_id)
            if parent_id is not None:
                variant_ids.update(siblings_by_parent[parent_id])
        return variant_ids
