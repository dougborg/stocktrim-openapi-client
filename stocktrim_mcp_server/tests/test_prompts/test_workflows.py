"""Tests for workflow prompts."""


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
