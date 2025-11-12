"""Tests for workflow prompts."""

from fastmcp import FastMCP
from mcp.types import PromptMessage


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

    def test_product_lifecycle_review_prompt_registered(self):
        """Test that product_lifecycle_review prompt is registered."""
        from stocktrim_mcp_server.prompts.workflows import register_workflow_prompts

        mcp = FastMCP()
        register_workflow_prompts(mcp)

        # Check that the prompt is registered using internal prompt manager
        prompts = mcp._prompt_manager._prompts
        assert "product_lifecycle_review" in prompts
        assert prompts["product_lifecycle_review"] is not None

    def test_product_lifecycle_review_default_params(self):
        """Test product_lifecycle_review prompt with default parameters."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        # Call with defaults
        messages = product_lifecycle_review()

        # Verify structure
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all(isinstance(msg, PromptMessage) for msg in messages)

        # Verify roles
        assert messages[0].role == "assistant"
        assert messages[1].role == "user"

        # Verify content contains expected elements
        system_content = messages[0].content.text
        user_content = messages[1].content.text

        # System message should contain workflow guidance
        assert "Portfolio Overview" in system_content
        assert "Performance Analysis" in system_content
        assert "Configuration Review" in system_content
        assert "Optimization" in system_content
        assert "list_products" in system_content
        assert "configure_product" in system_content
        assert "forecasts_get_for_products" in system_content
        assert "update_forecast_settings" in system_content

        # User message should contain parameters
        assert "all categories" in user_content
        assert "Include inactive: False" in user_content
        assert "Start with portfolio overview" in user_content

    def test_product_lifecycle_review_with_category(self):
        """Test product_lifecycle_review prompt with specific category."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        messages = product_lifecycle_review(category="Electronics")

        # Verify category is used
        user_content = messages[1].content.text
        assert "Electronics" in user_content
        assert "Category: Electronics" in user_content

    def test_product_lifecycle_review_with_inactive(self):
        """Test product_lifecycle_review prompt with include_inactive flag."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        messages = product_lifecycle_review(include_inactive=True)

        # Verify inactive flag is set
        user_content = messages[1].content.text
        assert "Include inactive: True" in user_content

    def test_product_lifecycle_review_all_params(self):
        """Test product_lifecycle_review prompt with all parameters."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        messages = product_lifecycle_review(category="Hardware", include_inactive=True)

        user_content = messages[1].content.text
        assert "Hardware" in user_content
        assert "Category: Hardware" in user_content
        assert "Include inactive: True" in user_content

    def test_product_lifecycle_review_resources_mentioned(self):
        """Test that prompt mentions expected resources."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        messages = product_lifecycle_review()
        system_content = messages[0].content.text

        # Check for resource URIs mentioned in issue
        assert "stocktrim://products/" in system_content
        assert "stocktrim://reports/inventory-status" in system_content

    def test_product_lifecycle_review_analysis_areas(self):
        """Test that prompt includes all required analysis areas."""
        from stocktrim_mcp_server.prompts.workflows import (
            product_lifecycle_review,
        )

        messages = product_lifecycle_review()
        system_content = messages[0].content.text

        # Check for analysis areas from issue spec
        assert "Slow-moving" in system_content or "slow movers" in system_content
        assert "Overstock" in system_content
        assert "Forecast accuracy" in system_content
        assert "Supplier consolidation" in system_content
        assert "Missing configurations" in system_content
