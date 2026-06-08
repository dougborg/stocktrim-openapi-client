"""Tests for the BillOfMaterials helper."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from stocktrim_public_api_client.helpers.bill_of_materials import BillOfMaterials


@pytest.mark.asyncio
async def test_get_returns_empty_list_on_404(monkeypatch):
    """StockTrim answers 404 (not 200 + []) when there are no matching BOMs.

    Verified against production, where GET /api/boms 404s. The helper must
    normalize that to an empty list so callers (e.g. the assemblies
    reconciliation) don't crash with NotFoundError on a BOM-less account.
    """
    import stocktrim_public_api_client.generated.api.bill_of_materials.get_api_boms as mod

    response = Mock()
    response.status_code = 404
    monkeypatch.setattr(mod, "asyncio_detailed", AsyncMock(return_value=response))

    boms = BillOfMaterials(Mock())

    assert await boms.get() == []
    assert await boms.get(product_id="WIDGET-001") == []
    assert await boms.get_for_product("WIDGET-001") == []
