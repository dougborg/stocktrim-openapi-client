"""Tests for workflow prompts."""

import pytest

from stocktrim_mcp_server.prompts.workflows import _supplier_performance_review


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
