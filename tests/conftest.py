"""Test configuration and fixtures for the StockTrim OpenAPI Client test suite."""

import os
from unittest.mock import MagicMock

import httpx
import pytest

from stocktrim_public_api_client import StockTrimClient


@pytest.fixture
def mock_api_credentials():
    """Provide mock API credentials for testing."""
    return {
        "api_auth_id": "test-tenant-id",
        "api_auth_signature": "test-tenant-name",
        "base_url": "https://api.test.stocktrim.example.com",
    }


@pytest.fixture
def stocktrim_client(mock_api_credentials):
    """Create a StockTrimClient for testing."""
    return StockTrimClient(**mock_api_credentials)


@pytest.fixture
def mock_transport_handler():
    """Create a mock transport handler that can be customized per test."""

    def handler(request: httpx.Request) -> httpx.Response:
        # Default successful response
        return httpx.Response(200, json={"data": [{"id": 1, "name": "Test"}]})

    return handler


@pytest.fixture
def mock_transport(mock_transport_handler):
    """Create a MockTransport instance."""
    return httpx.MockTransport(mock_transport_handler)


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx Response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"status": "success", "data": []}
    response.headers = {}
    response.text = '{"status": "success", "data": []}'
    return response


@pytest.fixture
def mock_error_response():
    """Create a mock error response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 500
    response.json.return_value = {"error": "Internal Server Error"}
    response.headers = {}
    response.text = '{"error": "Internal Server Error"}'
    return response


@pytest.fixture
def mock_rate_limit_response():
    """Create a mock rate limit response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 429
    response.json.return_value = {"error": "Rate limit exceeded"}
    response.headers = {"Retry-After": "60"}
    response.text = '{"error": "Rate limit exceeded"}'
    return response


@pytest.fixture(autouse=True)
def clear_env():
    """Clear environment variables before each test."""
    # Store original values
    original_env = {}
    env_vars = [
        "STOCKTRIM_API_AUTH_ID",
        "STOCKTRIM_API_AUTH_SIGNATURE",
        "STOCKTRIM_BASE_URL",
    ]

    for var in env_vars:
        original_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def mock_env_credentials(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("STOCKTRIM_API_AUTH_ID", "env-tenant-id")
    monkeypatch.setenv("STOCKTRIM_API_AUTH_SIGNATURE", "env-tenant-name")
    monkeypatch.setenv("STOCKTRIM_BASE_URL", "https://api.env.stocktrim.example.com")


@pytest.fixture
async def async_stocktrim_client(mock_api_credentials):
    """Create an async StockTrimClient for testing."""
    async with StockTrimClient(**mock_api_credentials) as client:
        yield client


@pytest.fixture
def create_mock_response():
    """Factory fixture to create mock responses with custom data."""

    def _create_response(
        status_code: int = 200,
        json_data: dict | None = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        """Create a mock httpx Response.

        Args:
            status_code: HTTP status code
            json_data: JSON response data
            headers: Response headers

        Returns:
            Mock httpx.Response object
        """
        if json_data is None:
            json_data = {"data": []}
        if headers is None:
            headers = {}

        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data
        response.headers = headers
        response.text = str(json_data)
        response.content = str(json_data).encode()
        return response

    return _create_response


@pytest.fixture
def mock_server_error_response():
    """Create a mock 500 Internal Server Error response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 500
    response.json.return_value = {
        "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An error occurred while processing your request.",
    }
    response.headers = {"Content-Type": "application/problem+json"}
    response.text = '{"type": "...", "title": "Internal Server Error", "status": 500}'
    return response


@pytest.fixture
def mock_authentication_error_response():
    """Create a mock 401 Unauthorized response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.json.return_value = {
        "type": "https://tools.ietf.org/html/rfc7235#section-3.1",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid authentication credentials.",
    }
    response.headers = {"Content-Type": "application/problem+json"}
    response.text = '{"type": "...", "title": "Unauthorized", "status": 401}'
    return response


@pytest.fixture
def mock_validation_error_response():
    """Create a mock 422 Unprocessable Entity response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 422
    response.json.return_value = {
        "type": "https://tools.ietf.org/html/rfc4918#section-11.2",
        "title": "Unprocessable Entity",
        "status": 422,
        "detail": "Validation failed.",
        "errors": {"code": ["Code is required"]},
    }
    response.headers = {"Content-Type": "application/problem+json"}
    response.text = '{"type": "...", "title": "Unprocessable Entity", "status": 422}'
    return response


@pytest.fixture
def mock_not_found_response():
    """Create a mock 404 Not Found response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 404
    response.json.return_value = {
        "type": "https://tools.ietf.org/html/rfc7231#section-6.5.4",
        "title": "Not Found",
        "status": 404,
        "detail": "The requested resource was not found.",
    }
    response.headers = {"Content-Type": "application/problem+json"}
    response.text = '{"type": "...", "title": "Not Found", "status": 404}'
    return response


@pytest.fixture
def stocktrim_client_with_mock_transport(mock_api_credentials, mock_transport):
    """Create a StockTrimClient with mock transport for testing without network calls."""
    client = StockTrimClient(**mock_api_credentials)
    # Replace the transport with mock
    client._client._transport = mock_transport  # type: ignore[union-attr]
    return client
