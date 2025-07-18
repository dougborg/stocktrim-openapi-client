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
