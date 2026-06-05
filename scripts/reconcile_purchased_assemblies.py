#!/usr/bin/env python3
"""Reconcile buy-it-whole assemblies (e.g. bike frames) as purchased in StockTrim.

Katana syncs multi-level BOMs (complete bike -> frame -> frame parts) into
StockTrim, which then explodes every level and generates purchase demand for the
deepest components. For assemblies we buy whole (frames), we want explosion to
stop at the assembly: keep its demand (it still rolls up from the parent BOM) and
order it directly, but not order its sub-parts.

This script strips each detected assembly's own sub-BOM (leaving the parent ->
assembly link intact) and then triggers a forecast recalculation, which
supersedes the auto-recalc StockTrim runs immediately after a Katana import.

It is idempotent and intended to run on a schedule whose cadence covers the
Katana import frequency.

Credentials come from the environment (STOCKTRIM_API_AUTH_ID /
STOCKTRIM_API_AUTH_SIGNATURE), as with the other scripts in this directory.

Usage:
    uv run python scripts/reconcile_purchased_assemblies.py [--dry-run]
        [--no-expand-variants] [--no-forecast] [FINISHED_GOOD_ID ...]
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from stocktrim_public_api_client import StockTrimClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "finished_good_ids",
        nargs="*",
        help="Finished-good product IDs to seed from. Defaults to auto-detected "
        "BOM roots.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without deleting BOMs or recalculating.",
    )
    parser.add_argument(
        "--no-expand-variants",
        action="store_true",
        help="Do not expand detected assemblies to sibling variants by parent_id.",
    )
    parser.add_argument(
        "--no-forecast",
        action="store_true",
        help="Do not trigger a forecast recalculation after stripping sub-BOMs.",
    )
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    seed_ids = args.finished_good_ids or None

    async with StockTrimClient() as client:
        assemblies = client.assemblies

        if args.dry_run:
            finished_goods = seed_ids or await assemblies.detect_finished_goods()
            detected = await assemblies.detect_purchased_assemblies(finished_goods)
            logger.info("Finished goods (roots): %d", len(finished_goods))
            logger.info("Intermediate assemblies detected: %s", detected or "none")
            logger.info("Dry run — no BOMs deleted, no recalculation triggered.")
            return

        summary = await assemblies.reconcile_purchased_assemblies(
            finished_good_ids=seed_ids,
            expand_variants=not args.no_expand_variants,
            run_forecast=not args.no_forecast,
        )

    logger.info("Detected assemblies: %s", summary.detected or "none")
    for result in summary.changed:
        logger.info(
            "  %s -> removed %d sub-BOM rows: %s",
            result.product_id,
            len(result.removed_components),
            result.removed_components,
        )
    logger.info(
        "Done: %d assemblies changed, %d sub-BOM rows removed.",
        len(summary.changed),
        summary.total_removed,
    )
    if not args.no_forecast and summary.changed:
        logger.info("Forecast recalculation triggered.")


if __name__ == "__main__":
    asyncio.run(main())
