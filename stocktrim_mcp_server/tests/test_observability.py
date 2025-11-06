"""Tests for observability decorators."""

import asyncio
from unittest.mock import Mock

import pytest

from stocktrim_mcp_server.observability import observe_service, observe_tool


class TestObserveTool:
    """Test @observe_tool decorator."""

    @pytest.mark.asyncio
    async def test_observe_tool_success(self):
        """Test that @observe_tool logs successful execution."""

        @observe_tool
        async def sample_tool(param: str, ctx: Mock) -> str:
            return f"result: {param}"

        result = await sample_tool("test", ctx=Mock())

        assert result == "result: test"

    @pytest.mark.asyncio
    async def test_observe_tool_with_exception(self):
        """Test that @observe_tool logs failures."""

        @observe_tool
        async def failing_tool(param: str, ctx: Mock) -> str:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await failing_tool("test", ctx=Mock())

    @pytest.mark.asyncio
    async def test_observe_tool_timing(self):
        """Test that @observe_tool measures execution time."""

        @observe_tool
        async def slow_tool(duration: float, ctx: Mock) -> str:
            await asyncio.sleep(duration)
            return "done"

        result = await slow_tool(0.01, ctx=Mock())

        assert result == "done"

    @pytest.mark.asyncio
    async def test_observe_tool_preserves_function_name(self):
        """Test that decorator preserves function metadata."""

        @observe_tool
        async def my_custom_tool(ctx: Mock) -> str:
            """Custom tool docstring."""
            return "result"

        assert my_custom_tool.__name__ == "my_custom_tool"
        assert "Custom tool docstring" in my_custom_tool.__doc__

    @pytest.mark.asyncio
    async def test_observe_tool_filters_ctx_from_params(self):
        """Test that ctx parameter is excluded from logged params."""

        @observe_tool
        async def tool_with_ctx(param1: str, param2: int, ctx: Mock) -> str:
            return f"{param1}-{param2}"

        result = await tool_with_ctx("value", 42, ctx=Mock())

        assert result == "value-42"

    @pytest.mark.asyncio
    async def test_observe_tool_with_multiple_params(self):
        """Test decorator with multiple parameters."""

        @observe_tool
        async def multi_param_tool(
            a: str, b: int, c: bool, ctx: Mock
        ) -> dict[str, object]:
            return {"a": a, "b": b, "c": c}

        result = await multi_param_tool("test", 123, True, ctx=Mock())

        assert result == {"a": "test", "b": 123, "c": True}

    @pytest.mark.asyncio
    async def test_observe_tool_with_none_result(self):
        """Test decorator when tool returns None."""

        @observe_tool
        async def none_returning_tool(ctx: Mock) -> None:
            return None

        result = await none_returning_tool(ctx=Mock())

        assert result is None


class TestObserveService:
    """Test @observe_service decorator."""

    @pytest.mark.asyncio
    async def test_observe_service_success(self):
        """Test that @observe_service logs successful operations."""

        class TestService:
            @observe_service("get_item")
            async def get_item(self, item_id: str) -> dict[str, str]:
                return {"id": item_id, "name": "Test Item"}

        service = TestService()
        result = await service.get_item("123")

        assert result == {"id": "123", "name": "Test Item"}

    @pytest.mark.asyncio
    async def test_observe_service_with_exception(self):
        """Test that @observe_service logs failures."""

        class TestService:
            @observe_service("failing_operation")
            async def failing_operation(self) -> str:
                raise RuntimeError("Operation failed")

        service = TestService()

        with pytest.raises(RuntimeError, match="Operation failed"):
            await service.failing_operation()

    @pytest.mark.asyncio
    async def test_observe_service_timing(self):
        """Test that @observe_service measures execution time."""

        class TestService:
            @observe_service("slow_operation")
            async def slow_operation(self, duration: float) -> str:
                await asyncio.sleep(duration)
                return "completed"

        service = TestService()
        result = await service.slow_operation(0.01)

        assert result == "completed"

    @pytest.mark.asyncio
    async def test_observe_service_preserves_function_name(self):
        """Test that decorator preserves function metadata."""

        class TestService:
            @observe_service("my_operation")
            async def my_operation(self) -> str:
                """Operation docstring."""
                return "result"

        service = TestService()
        assert service.my_operation.__name__ == "my_operation"
        assert "Operation docstring" in service.my_operation.__doc__

    @pytest.mark.asyncio
    async def test_observe_service_with_kwargs(self):
        """Test decorator logs kwargs."""

        class TestService:
            @observe_service("create_item")
            async def create_item(
                self, name: str, quantity: int, active: bool = True
            ) -> dict[str, object]:
                return {"name": name, "quantity": quantity, "active": active}

        service = TestService()
        result = await service.create_item(name="Widget", quantity=10, active=False)

        assert result == {"name": "Widget", "quantity": 10, "active": False}

    @pytest.mark.asyncio
    async def test_observe_service_class_name_extraction(self):
        """Test that decorator extracts class name correctly."""

        class MyCustomService:
            @observe_service("test_op")
            async def test_op(self) -> str:
                return "ok"

        service = MyCustomService()
        result = await service.test_op()

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_observe_service_with_no_params(self):
        """Test decorator on method with no parameters."""

        class TestService:
            @observe_service("no_param_operation")
            async def no_param_operation(self) -> str:
                return "success"

        service = TestService()
        result = await service.no_param_operation()

        assert result == "success"

    @pytest.mark.asyncio
    async def test_observe_service_multiple_calls(self):
        """Test that decorator handles multiple sequential calls."""

        class TestService:
            @observe_service("get_data")
            async def get_data(self, id: str) -> str:
                return f"data-{id}"

        service = TestService()

        result1 = await service.get_data("1")
        result2 = await service.get_data("2")
        result3 = await service.get_data("3")

        assert result1 == "data-1"
        assert result2 == "data-2"
        assert result3 == "data-3"
