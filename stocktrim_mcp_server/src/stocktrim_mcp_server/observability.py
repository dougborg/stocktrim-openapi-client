"""Observability utilities for tool invocation tracking.

This module provides decorators and utilities for tracking tool performance,
errors, and usage patterns.
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from stocktrim_mcp_server.logging_config import get_logger

logger = get_logger("observability")

F = TypeVar("F", bound=Callable[..., Any])


def observe_tool(func: F) -> F:
    """Decorator to add observability to MCP tool functions.

    Logs:
    - Tool invocation with parameters
    - Execution duration
    - Success/failure status
    - Error details if failed

    Usage:
        @observe_tool
        @mcp.tool
        async def my_tool(param: str, ctx: Context) -> str:
            return "result"
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        tool_name = func.__name__
        start_time = time.perf_counter()

        # Extract parameters (excluding ctx)
        params = {k: v for k, v in kwargs.items() if k != "ctx"}

        logger.info(
            "tool_invoked",
            tool_name=tool_name,
            params=params,
        )

        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "tool_completed",
                tool_name=tool_name,
                duration_ms=round(duration_ms, 2),
                success=True,
            )

            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.error(
                "tool_failed",
                tool_name=tool_name,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
                success=False,
            )

            raise

    return wrapper  # type: ignore[return-value]


def observe_service(operation: str) -> Callable[[F], F]:
    """Decorator to add observability to service layer operations.

    Args:
        operation: Name of the operation (e.g., "get_product", "create_order")

    Usage:
        @observe_service("get_product")
        async def get(self, product_code: str) -> Product:
            return product
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()

            # Get class name if available
            class_name = args[0].__class__.__name__ if args else "unknown"

            logger.debug(
                "service_operation_started",
                service=class_name,
                operation=operation,
                params=kwargs,
            )

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000

                logger.debug(
                    "service_operation_completed",
                    service=class_name,
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    success=True,
                )

                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000

                logger.error(
                    "service_operation_failed",
                    service=class_name,
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False,
                )

                raise

        return wrapper  # type: ignore[return-value]

    return decorator
