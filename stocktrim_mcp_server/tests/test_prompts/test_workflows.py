"""Tests for workflow prompts."""

import pytest

from stocktrim_mcp_server.prompts.workflows import _forecast_accuracy_review


class TestWorkflowPrompts:
    """Tests for workflow prompt registration and structure."""

    def test_prompts_module_exists(self):
        """Test that prompts module can be imported."""
        from stocktrim_mcp_server.prompts import register_all_prompts

        assert callable(register_all_prompts)

    def test_workflow_prompts_module_exists(self):
        """Test that workflow prompts module can be imported."""
        from stocktrim_mcp_server.prompts.workflows import register_workflow_prompts

        assert callable(register_workflow_prompts)


class TestForecastAccuracyReview:
    """Tests for forecast accuracy review prompt."""

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_structure(self):
        """Test prompt returns a string."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_content(self):
        """Test prompt contains expected content."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        prompt_lower = prompt.lower()
        assert "forecasting analyst" in prompt_lower
        assert "accuracy analysis" in prompt_lower
        assert "forecasts_get_for_products" in prompt_lower
        assert "update_forecast_settings" in prompt_lower
        assert "stocktrim://products" in prompt_lower
        assert "stocktrim://reports/inventory-status" in prompt_lower
        assert "90" in prompt
        assert "forecast accuracy review" in prompt_lower

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_with_location(self):
        """Test prompt correctly uses location parameter."""
        prompt = await _forecast_accuracy_review("WAREHOUSE-A", 90, None)

        assert "WAREHOUSE-A" in prompt
        assert "90" in prompt

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_without_location(self):
        """Test prompt correctly handles None location."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        assert "all locations" in prompt.lower()
        assert "90" in prompt

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_custom_lookback(self):
        """Test prompt correctly uses custom lookback_days parameter."""
        prompt = await _forecast_accuracy_review("WAREHOUSE-B", 60, None)

        assert "WAREHOUSE-B" in prompt
        assert "60" in prompt

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_token_size(self):
        """Test prompt stays within token budget."""
        prompt = await _forecast_accuracy_review("WAREHOUSE-A", 90, None)

        # Keep under 5KB total
        assert len(prompt) < 5000, f"Prompt too large: {len(prompt)} bytes"

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_includes_current_date(self):
        """Test prompt includes current date."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        # Should contain a date in YYYY-MM-DD format
        import re

        date_pattern = r"\d{4}-\d{2}-\d{2}"
        assert re.search(date_pattern, prompt) is not None

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_mentions_key_metrics(self):
        """Test prompt mentions key forecast accuracy metrics."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        prompt_lower = prompt.lower()
        # Check for key metrics mentioned
        assert "variance" in prompt_lower
        assert "bias" in prompt_lower
        assert "stockout" in prompt_lower
        assert "overstock" in prompt_lower
        assert "r-squared" in prompt_lower or "r²" in prompt_lower

    @pytest.mark.asyncio
    async def test_forecast_accuracy_review_has_workflow_steps(self):
        """Test prompt includes clear workflow steps."""
        prompt = await _forecast_accuracy_review(None, 90, None)

        # Check for numbered or labeled workflow steps
        assert "Step 1" in prompt
        assert "Step 2" in prompt
        assert "Step 3" in prompt
        assert "Step 4" in prompt
