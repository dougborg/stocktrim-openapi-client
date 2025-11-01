"""Tests for TRACE-level logging functionality."""

import logging
from unittest.mock import AsyncMock

import httpx
import pytest

from stocktrim_public_api_client import TRACE


class TestTraceLogging:
    """Test TRACE-level logging functionality."""

    def test_trace_constant_exists(self):
        """Test that TRACE constant is defined and has correct value."""
        assert TRACE == 5
        assert logging.getLevelName(TRACE) == "TRACE"

    def test_trace_method_exists(self):
        """Test that logging.Logger has trace() method."""
        logger = logging.getLogger("test")
        assert hasattr(logger, "trace")
        assert callable(logger.trace)

    def test_trace_method_logs_when_enabled(self, caplog):
        """Test that trace() method logs when TRACE level is enabled."""
        logger = logging.getLogger("test_trace_enabled")
        logger.setLevel(TRACE)

        with caplog.at_level(TRACE, logger="test_trace_enabled"):
            logger.trace("Test trace message")  # type: ignore[attr-defined]

        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == TRACE
        assert caplog.records[0].message == "Test trace message"

    def test_trace_method_does_not_log_when_disabled(self, caplog):
        """Test that trace() method doesn't log when TRACE level is disabled."""
        logger = logging.getLogger("test_trace_disabled")
        logger.setLevel(logging.DEBUG)  # Higher than TRACE

        with caplog.at_level(logging.DEBUG, logger="test_trace_disabled"):
            logger.trace("Test trace message")  # type: ignore[attr-defined]

        assert len(caplog.records) == 0

    def test_trace_level_below_debug(self):
        """Test that TRACE level is below DEBUG."""
        assert TRACE < logging.DEBUG
        assert TRACE > logging.NOTSET

    @pytest.mark.asyncio
    async def test_error_logging_transport_logs_success_at_trace(
        self, mock_api_credentials, caplog
    ):
        """Test that ErrorLoggingTransport logs successful responses at TRACE level."""
        from stocktrim_public_api_client.stocktrim_client import ErrorLoggingTransport

        # Create a mock response
        mock_response = httpx.Response(
            200,
            json={"data": [{"id": 1, "name": "Test Product"}]},
        )

        # Mock the wrapped transport
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = mock_response

        # Create logger and set to TRACE level
        logger = logging.getLogger("test_success_logging")
        logger.setLevel(TRACE)

        # Create ErrorLoggingTransport with the logger
        transport = ErrorLoggingTransport(
            wrapped_transport=mock_transport, logger=logger
        )

        # Create a request
        request = httpx.Request(
            "GET", "https://api.test.stocktrim.example.com/api/Products"
        )

        # Handle the request
        with caplog.at_level(TRACE, logger="test_success_logging"):
            response = await transport.handle_async_request(request)

        # Verify response is returned unchanged
        assert response.status_code == 200

        # Verify TRACE logging occurred
        trace_logs = [r for r in caplog.records if r.levelno == TRACE]
        assert len(trace_logs) == 1
        assert "Full response body" in trace_logs[0].message
        assert "GET" in trace_logs[0].message
        assert "200" in trace_logs[0].message
        # Verify JSON is pretty-printed
        assert '"data"' in trace_logs[0].message
        assert '"id": 1' in trace_logs[0].message

    @pytest.mark.asyncio
    async def test_error_logging_transport_no_log_when_trace_disabled(
        self, mock_api_credentials, caplog
    ):
        """Test that ErrorLoggingTransport doesn't log success when TRACE is disabled."""
        from stocktrim_public_api_client.stocktrim_client import ErrorLoggingTransport

        # Create a mock response
        mock_response = httpx.Response(
            200,
            json={"data": [{"id": 1, "name": "Test Product"}]},
        )

        # Mock the wrapped transport
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = mock_response

        # Create logger at DEBUG level (higher than TRACE)
        logger = logging.getLogger("test_no_trace_logging")
        logger.setLevel(logging.DEBUG)

        # Create ErrorLoggingTransport with the logger
        transport = ErrorLoggingTransport(
            wrapped_transport=mock_transport, logger=logger
        )

        # Create a request
        request = httpx.Request(
            "GET", "https://api.test.stocktrim.example.com/api/Products"
        )

        # Handle the request
        with caplog.at_level(logging.DEBUG, logger="test_no_trace_logging"):
            response = await transport.handle_async_request(request)

        # Verify response is returned unchanged
        assert response.status_code == 200

        # Verify NO TRACE logging occurred
        trace_logs = [r for r in caplog.records if r.levelno == TRACE]
        assert len(trace_logs) == 0

    @pytest.mark.asyncio
    async def test_error_logging_transport_logs_non_json_at_trace(
        self, mock_api_credentials, caplog
    ):
        """Test that ErrorLoggingTransport logs non-JSON responses at TRACE level."""
        from stocktrim_public_api_client.stocktrim_client import ErrorLoggingTransport

        # Create a mock response with plain text
        mock_response = httpx.Response(
            200,
            content=b"Plain text response",
            headers={"Content-Type": "text/plain"},
        )

        # Mock the wrapped transport
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = mock_response

        # Create logger and set to TRACE level
        logger = logging.getLogger("test_non_json_logging")
        logger.setLevel(TRACE)

        # Create ErrorLoggingTransport with the logger
        transport = ErrorLoggingTransport(
            wrapped_transport=mock_transport, logger=logger
        )

        # Create a request
        request = httpx.Request(
            "GET", "https://api.test.stocktrim.example.com/api/Test"
        )

        # Handle the request
        with caplog.at_level(TRACE, logger="test_non_json_logging"):
            response = await transport.handle_async_request(request)

        # Verify response is returned unchanged
        assert response.status_code == 200

        # Verify TRACE logging occurred with [raw] tag
        trace_logs = [r for r in caplog.records if r.levelno == TRACE]
        assert len(trace_logs) == 1
        assert "[raw]" in trace_logs[0].message
        assert "Plain text response" in trace_logs[0].message

    @pytest.mark.asyncio
    async def test_error_logging_transport_does_not_log_errors_at_trace(
        self, mock_api_credentials, caplog
    ):
        """Test that ErrorLoggingTransport doesn't log errors at TRACE (only successes)."""
        from stocktrim_public_api_client.stocktrim_client import ErrorLoggingTransport

        # Create a mock error response
        mock_response = httpx.Response(
            404,
            json={"error": "Not found"},
        )

        # Mock the wrapped transport
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = mock_response

        # Create logger and set to TRACE level
        logger = logging.getLogger("test_error_no_trace")
        logger.setLevel(TRACE)

        # Create ErrorLoggingTransport with the logger
        transport = ErrorLoggingTransport(
            wrapped_transport=mock_transport, logger=logger
        )

        # Create a request
        request = httpx.Request(
            "GET", "https://api.test.stocktrim.example.com/api/NotFound"
        )

        # Handle the request
        with caplog.at_level(TRACE, logger="test_error_no_trace"):
            response = await transport.handle_async_request(request)

        # Verify response is returned unchanged
        assert response.status_code == 404

        # Verify NO TRACE logging for success (errors use ERROR level)
        trace_logs = [r for r in caplog.records if r.levelno == TRACE]
        assert len(trace_logs) == 0

        # Verify ERROR logging occurred instead
        error_logs = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_logs) > 0
