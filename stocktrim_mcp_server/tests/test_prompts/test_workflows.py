"""Tests for workflow prompts."""

import pytest

from stocktrim_mcp_server.prompts.workflows import _purchasing_workflow


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
