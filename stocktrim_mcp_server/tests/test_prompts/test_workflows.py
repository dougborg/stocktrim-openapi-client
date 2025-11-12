"""Tests for workflow prompts."""

import pytest

from stocktrim_mcp_server.prompts.workflows import _stockout_prevention


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


class TestStockoutPreventionPrompt:
    """Tests for stockout prevention prompt."""

    @pytest.mark.asyncio
    async def test_stockout_prevention_structure(self):
        """Test prompt returns correct message structure."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert hasattr(messages[0].content, "text")

    @pytest.mark.asyncio
    async def test_stockout_prevention_content(self):
        """Test prompt contains expected content."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        content = messages[0].content.text.lower()
        assert "stockout prevention" in content
        assert "review_urgent_order_requirements" in content
        assert "generate_purchase_orders_from_urgent_items" in content
        assert "forecasts_get_for_products" in content
        assert "stocktrim://reports/inventory-status" in content
        assert "stocktrim://reports/urgent-orders" in content
        assert "warehouse-a" in content
        assert "14" in messages[0].content.text

    @pytest.mark.asyncio
    async def test_stockout_prevention_parameters(self):
        """Test prompt correctly uses parameters."""
        messages = await _stockout_prevention("WAREHOUSE-B", 30, None)

        content = messages[0].content.text
        assert "WAREHOUSE-B" in content
        assert "30" in content

    @pytest.mark.asyncio
    async def test_stockout_prevention_default_parameters(self):
        """Test prompt works with default days_ahead parameter."""
        messages = await _stockout_prevention("WAREHOUSE-C", 14, None)

        content = messages[0].content.text
        assert "WAREHOUSE-C" in content
        assert "14" in content

    @pytest.mark.asyncio
    async def test_stockout_prevention_token_size(self):
        """Test prompt stays within token budget."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        total_size = len(messages[0].content.text)

        # Keep under 5KB total
        assert total_size < 5000, f"Prompt too large: {total_size} bytes"

    @pytest.mark.asyncio
    async def test_stockout_prevention_includes_date(self):
        """Test prompt includes current date."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        content = messages[0].content.text
        assert "Analysis date:" in content

    @pytest.mark.asyncio
    async def test_stockout_prevention_includes_all_steps(self):
        """Test prompt includes all required workflow steps."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        content = messages[0].content.text
        # Check for all required steps
        assert "Step 1: Risk Analysis" in content
        assert "Step 2: Gap Identification" in content
        assert "Step 3: Forecast Review" in content
        assert "Step 4: Preventive Action" in content
        assert "Step 5: Recommendations" in content

    @pytest.mark.asyncio
    async def test_stockout_prevention_includes_best_practices(self):
        """Test prompt includes best practices section."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        content = messages[0].content.text
        assert "Best Practices" in content
        assert "lead times" in content.lower()
        assert "safety stock" in content.lower()

    @pytest.mark.asyncio
    async def test_stockout_prevention_includes_output_format(self):
        """Test prompt includes output format guidance."""
        messages = await _stockout_prevention("WAREHOUSE-A", 14, None)

        content = messages[0].content.text
        assert "Output Format" in content
        assert "Executive Summary" in content
        assert "Risk Categories" in content
