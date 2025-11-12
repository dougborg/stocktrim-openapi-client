"""Tests for workflow prompts."""

import re

import pytest

from stocktrim_mcp_server.prompts.workflows import (
    _forecast_accuracy_review,
    _purchasing_workflow,
    _supplier_performance_review,
)


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


class TestPurchasingWorkflow:
    """Tests for purchasing_workflow prompt."""

    @pytest.mark.asyncio
    async def test_purchasing_workflow_structure(self):
        """Test prompt returns correct message structure."""
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        assert len(messages) == 1  # MCP prompts return single user message
        assert messages[0].role == "user"
        assert hasattr(messages[0], "content")

    @pytest.mark.asyncio
    async def test_purchasing_workflow_content(self):
        """Test prompt contains expected content."""
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        content = messages[0].content.text.lower()
        assert "purchasing analyst" in content
        assert "review_urgent_order_requirements" in content
        assert "generate_purchase_orders_from_urgent_items" in content
        assert "stocktrim://reports/urgent-orders" in content

        user_content = messages[0].content.text
        assert "WAREHOUSE-A" in user_content
        assert "30" in user_content

    @pytest.mark.asyncio
    async def test_purchasing_workflow_parameters(self):
        """Test prompt correctly uses parameters."""
        messages = await _purchasing_workflow("WAREHOUSE-B", 45, None)

        user_content = messages[0].content.text
        assert "WAREHOUSE-B" in user_content
        assert "45" in user_content

    @pytest.mark.asyncio
    async def test_purchasing_workflow_token_size(self):
        """Test prompt stays within token budget."""
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        total_size = len(messages[0].content.text)

        # Keep under 5KB total
        assert total_size < 5000, f"Prompt too large: {total_size} bytes"

    @pytest.mark.asyncio
    async def test_purchasing_workflow_includes_current_date(self):
        """Test prompt includes current date in user message."""
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        user_content = messages[0].content.text
        # Should contain a date in YYYY-MM-DD format
        assert "202" in user_content  # Year should be 202x

    @pytest.mark.asyncio
    async def test_purchasing_workflow_includes_all_sections(self):
        """Test message includes all required sections."""
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        content = messages[0].content.text
        # Check for all major sections
        assert "Your Role" in content
        assert "Process Steps" in content
        assert "Step 1: Analyze Requirements" in content
        assert "Step 2: Group by Supplier" in content
        assert "Step 3: Generate Purchase Orders" in content
        assert "Step 4: Summary and Recommendations" in content
        assert "Best Practices" in content
        assert "Tools Available" in content
        assert "Resources Available" in content
        assert "Output Format" in content

    @pytest.mark.asyncio
    async def test_purchasing_workflow_default_threshold(self):
        """Test prompt works with default threshold."""
        # When called from FastMCP, default is 30
        messages = await _purchasing_workflow("WAREHOUSE-A", 30, None)

        user_content = messages[0].content.text
        assert "30-day threshold" in user_content


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


class TestSupplierPerformanceReview:
    """Tests for supplier_performance_review prompt."""

    @pytest.mark.asyncio
    async def test_supplier_performance_review_structure(self):
        """Test prompt returns correct message structure."""
        messages = await _supplier_performance_review(None, 90, None)

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert hasattr(messages[0].content, "text")

    @pytest.mark.asyncio
    async def test_supplier_performance_review_content(self):
        """Test prompt contains expected content."""
        messages = await _supplier_performance_review(None, 90, None)

        content = messages[0].content.text.lower()
        assert "supply chain analyst" in content
        assert "supplier performance review" in content
        assert "list_purchase_orders" in content
        assert "get_supplier" in content
        assert "stocktrim://reports/supplier-directory" in content
        assert "stocktrim://suppliers/{code}" in content

        # Check for key process steps
        assert "supplier overview" in content
        assert "performance analysis" in content
        assert "trend analysis" in content
        assert "recommendations" in content

        # Check for key metrics
        assert "on-time delivery" in content
        assert "cost" in content or "costs" in content
        assert "lead time" in content

        # Check for parameters
        assert "90" in content
        assert "all suppliers" in content

    @pytest.mark.asyncio
    async def test_supplier_performance_review_specific_supplier(self):
        """Test prompt correctly uses specific supplier parameter."""
        messages = await _supplier_performance_review("SUP-001", 90, None)

        content = messages[0].content.text
        assert "SUP-001" in content
        assert "Specific supplier: SUP-001" in content

    @pytest.mark.asyncio
    async def test_supplier_performance_review_all_suppliers(self):
        """Test prompt correctly handles all suppliers mode."""
        messages = await _supplier_performance_review(None, 90, None)

        content = messages[0].content.text
        assert "All suppliers" in content

    @pytest.mark.asyncio
    async def test_supplier_performance_review_parameters(self):
        """Test prompt correctly uses parameters."""
        messages = await _supplier_performance_review("SUP-002", 60, None)

        content = messages[0].content.text
        assert "SUP-002" in content
        assert "60" in content

    @pytest.mark.asyncio
    async def test_supplier_performance_review_token_size(self):
        """Test prompt stays within token budget."""
        messages = await _supplier_performance_review(None, 90, None)

        content_size = len(messages[0].content.text)

        # Keep under 5KB total
        assert content_size < 5000, f"Prompt too large: {content_size} bytes"

    @pytest.mark.asyncio
    async def test_supplier_performance_review_contains_metrics(self):
        """Test prompt mentions key performance metrics."""
        messages = await _supplier_performance_review(None, 90, None)

        content = messages[0].content.text.lower()
        # Check for important metrics
        assert "delivery" in content
        assert "accuracy" in content
        assert "consolidation" in content
        assert "risk" in content

    @pytest.mark.asyncio
    async def test_supplier_performance_review_output_format(self):
        """Test prompt specifies output format."""
        messages = await _supplier_performance_review(None, 90, None)

        content = messages[0].content.text.lower()
        # Check for output format guidance
        assert "executive summary" in content
        assert "markdown" in content or "report" in content
        assert "recommendations" in content
