"""Tests for the StockTrim client."""

import logging
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from stocktrim_public_api_client import StockTrimClient
from stocktrim_public_api_client.stocktrim_client import ErrorLoggingTransport


class TestStockTrimClient:
    """Test the StockTrimClient class."""

    def test_client_initialization_with_credentials(self, mock_api_credentials):
        """Test client can be initialized with credentials."""
        client = StockTrimClient(**mock_api_credentials)

        # New architecture: client inherits from AuthenticatedClient
        assert isinstance(client, StockTrimClient)
        assert client.base_url == "https://api.test.stocktrim.example.com"
        assert client.max_retries == 5

    def test_client_initialization_from_env(self, mock_env_credentials):
        """Test client can be initialized from environment variables."""
        client = StockTrimClient()

        # Verify client was created successfully
        assert isinstance(client, StockTrimClient)
        # The mock_env_credentials fixture sets a custom base URL
        assert client.base_url == "https://api.env.stocktrim.example.com"

    def test_client_missing_credentials_raises_error(self):
        """Test client raises error when credentials are missing."""
        # Clear all environment variables including StockTrim credentials
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.dict(
                os.environ,
                {"STOCKTRIM_API_AUTH_ID": "", "STOCKTRIM_API_AUTH_SIGNATURE": ""},
                clear=True,
            ),
            pytest.raises(ValueError, match="API credentials required"),
        ):
            StockTrimClient()

    def test_client_repr(self, stocktrim_client):
        """Test client string representation."""
        repr_str = repr(stocktrim_client)
        assert "StockTrimClient" in repr_str
        assert "base_url" in repr_str
        assert "max_retries" in repr_str

    @pytest.mark.asyncio
    async def test_client_context_manager(self, stocktrim_client):
        """Test client works as async context manager."""
        async with stocktrim_client as client:
            assert client is stocktrim_client
            # New architecture: client IS the authenticated client
            assert isinstance(client, StockTrimClient)

        # Client should be properly closed after context exit
        # The underlying httpx client is closed by the parent class


class TestErrorLoggingTransport:
    """Test the ErrorLoggingTransport logging functionality."""

    @pytest.fixture
    def mock_transport(self):
        """Create a mock AsyncHTTPTransport."""
        transport = AsyncMock(spec=httpx.AsyncHTTPTransport)
        return transport

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = MagicMock(spec=logging.Logger)
        logger.isEnabledFor = MagicMock(return_value=True)
        return logger

    @pytest.fixture
    def logging_transport(self, mock_transport, mock_logger):
        """Create ErrorLoggingTransport with mocked dependencies."""
        return ErrorLoggingTransport(
            wrapped_transport=mock_transport, logger=mock_logger
        )

    @pytest.fixture
    def mock_request(self):
        """Create a mock HTTP request."""
        request = MagicMock(spec=httpx.Request)
        request.method = "GET"
        request.url = "https://api.stocktrim.com/api/Products"
        request.headers = {
            "user-agent": "test-client",
            "api-auth-id": "secret-id",
            "api-auth-signature": "secret-signature",
        }
        return request

    def create_mock_response(
        self, status_code: int, json_data=None, text=None, request=None
    ):
        """Create a mock HTTP response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.request = request or MagicMock(spec=httpx.Request)

        if json_data is not None:
            response.json = MagicMock(return_value=json_data)
            response.text = str(json_data)
        elif text is not None:
            response.json = MagicMock(side_effect=ValueError("Not JSON"))
            response.text = text
        else:
            response.json = MagicMock(return_value=None)
            response.text = "null"

        # Mock aread for streaming responses
        response.aread = AsyncMock()
        return response

    @pytest.mark.asyncio
    async def test_log_request_sanitizes_auth_headers(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test that request logging excludes auth headers."""
        await logging_transport._log_request(mock_request)

        # Verify debug was called
        assert mock_logger.debug.called
        call_args = mock_logger.debug.call_args

        # Check that auth headers were sanitized
        extra_data = call_args.kwargs.get("extra", {})
        headers = extra_data.get("headers", {})
        assert "user-agent" in headers
        assert "api-auth-id" not in headers
        assert "api-auth-signature" not in headers

    @pytest.mark.asyncio
    async def test_log_success_response_info_level(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test that successful responses are logged at INFO level."""
        response = self.create_mock_response(
            200, json_data={"id": 123}, request=mock_request
        )

        await logging_transport._log_success_response(response, mock_request, 100.5)

        # Verify INFO log was called with status and timing
        mock_logger.info.assert_called_once()
        info_message = mock_logger.info.call_args[0][0]
        assert "GET" in info_message
        assert "200" in info_message
        assert "100ms" in info_message or "101ms" in info_message

    @pytest.mark.asyncio
    async def test_log_success_response_debug_body_list(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test DEBUG logging shows list length for array responses."""
        response = self.create_mock_response(
            200, json_data=[{"id": 1}, {"id": 2}, {"id": 3}], request=mock_request
        )
        mock_logger.isEnabledFor.return_value = True

        await logging_transport._log_success_response(response, mock_request, 50.0)

        # Verify DEBUG log shows list length
        debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
        assert any("list[3] items" in call for call in debug_calls)

    @pytest.mark.asyncio
    async def test_log_success_response_null_warning(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test that null responses trigger a WARNING about potential TypeErrors."""
        response = self.create_mock_response(200, json_data=None, request=mock_request)
        mock_logger.isEnabledFor.return_value = True

        await logging_transport._log_success_response(response, mock_request, 75.0)

        # Verify WARNING was logged about null response
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "null" in warning_message.lower()
        assert "TypeError" in warning_message

    @pytest.mark.asyncio
    async def test_log_success_response_dict_excerpt(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test DEBUG logging shows dict excerpt for object responses."""
        large_dict = {"key": "value" * 100}  # Large response
        response = self.create_mock_response(
            200, json_data=large_dict, request=mock_request
        )
        mock_logger.isEnabledFor.return_value = True

        await logging_transport._log_success_response(response, mock_request, 50.0)

        # Verify DEBUG log shows truncated body
        debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
        assert any("Response body:" in call and "..." in call for call in debug_calls)

    @pytest.mark.asyncio
    async def test_log_client_error_with_json(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test 4xx error logging with JSON response."""
        error_data = {"type": "about:blank", "title": "Not Found", "status": 404}
        response = self.create_mock_response(
            404, json_data=error_data, request=mock_request
        )

        await logging_transport._log_client_error(response, mock_request, 125.5)

        # Verify ERROR was logged with error details and timing
        mock_logger.error.assert_called()
        error_message = mock_logger.error.call_args[0][0]
        assert "404" in error_message
        assert "125ms" in error_message or "126ms" in error_message

    @pytest.mark.asyncio
    async def test_log_client_error_non_json(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test 4xx error logging with non-JSON response."""
        response = self.create_mock_response(
            400, text="Bad Request", request=mock_request
        )

        await logging_transport._log_client_error(response, mock_request, 50.0)

        # Verify ERROR was logged with text response
        mock_logger.error.assert_called()
        error_message = mock_logger.error.call_args[0][0]
        assert "400" in error_message
        assert "50ms" in error_message

    @pytest.mark.asyncio
    async def test_log_server_error_with_json(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test 5xx error logging with JSON response."""
        error_data = {"error": "Internal Server Error"}
        response = self.create_mock_response(
            500, json_data=error_data, request=mock_request
        )

        await logging_transport._log_server_error(response, mock_request, 200.0)

        # Verify ERROR was logged with server error details
        mock_logger.error.assert_called()
        error_message = mock_logger.error.call_args[0][0]
        assert "500" in error_message
        assert "Server error" in error_message
        assert "200ms" in error_message

    @pytest.mark.asyncio
    async def test_log_server_error_non_json(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test 5xx error logging with non-JSON response."""
        response = self.create_mock_response(
            503, text="Service Unavailable", request=mock_request
        )

        await logging_transport._log_server_error(response, mock_request, 300.0)

        # Verify ERROR was logged with text response
        mock_logger.error.assert_called()
        error_message = mock_logger.error.call_args[0][0]
        assert "503" in error_message
        assert "300ms" in error_message

    @pytest.mark.asyncio
    async def test_handle_async_request_routes_2xx(
        self, logging_transport, mock_request, mock_transport, mock_logger
    ):
        """Test that 2xx responses are routed to success logging."""
        response = self.create_mock_response(
            200, json_data={"result": "ok"}, request=mock_request
        )
        mock_transport.handle_async_request.return_value = response

        result = await logging_transport.handle_async_request(mock_request)

        assert result == response
        mock_logger.info.assert_called()  # Should log at INFO level

    @pytest.mark.asyncio
    async def test_handle_async_request_routes_4xx(
        self, logging_transport, mock_request, mock_transport, mock_logger
    ):
        """Test that 4xx responses are routed to client error logging."""
        response = self.create_mock_response(
            404, json_data={"error": "Not found"}, request=mock_request
        )
        mock_transport.handle_async_request.return_value = response

        result = await logging_transport.handle_async_request(mock_request)

        assert result == response
        mock_logger.error.assert_called()  # Should log at ERROR level

    @pytest.mark.asyncio
    async def test_handle_async_request_routes_5xx(
        self, logging_transport, mock_request, mock_transport, mock_logger
    ):
        """Test that 5xx responses are routed to server error logging."""
        response = self.create_mock_response(
            500, json_data={"error": "Server error"}, request=mock_request
        )
        mock_transport.handle_async_request.return_value = response

        result = await logging_transport.handle_async_request(mock_request)

        assert result == response
        mock_logger.error.assert_called()  # Should log at ERROR level

    @pytest.mark.asyncio
    async def test_logging_respects_debug_level(
        self, logging_transport, mock_request, mock_logger
    ):
        """Test that DEBUG-level logging is skipped when DEBUG is disabled."""
        mock_logger.isEnabledFor.return_value = False
        response = self.create_mock_response(
            200, json_data={"data": "test"}, request=mock_request
        )

        await logging_transport._log_success_response(response, mock_request, 50.0)

        # INFO should still be called
        mock_logger.info.assert_called()
        # But DEBUG details should not be logged
        assert mock_logger.debug.call_count == 0
