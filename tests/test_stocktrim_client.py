"""Tests for the StockTrim client."""

import os
from unittest.mock import patch

import pytest

from stocktrim_public_api_client import StockTrimClient


class TestStockTrimClient:
    """Test the StockTrimClient class."""

    def test_client_initialization_with_credentials(self, mock_api_credentials):
        """Test client can be initialized with credentials."""
        client = StockTrimClient(**mock_api_credentials)

        assert client.api_auth_id == "test-tenant-id"
        assert client.api_auth_signature == "test-tenant-name"
        assert client.base_url == "https://api.test.stocktrim.example.com"

    def test_client_initialization_from_env(self, mock_env_credentials):
        """Test client can be initialized from environment variables."""
        client = StockTrimClient()

        assert client.api_auth_id == "env-tenant-id"
        assert client.api_auth_signature == "env-tenant-name"

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
            pytest.raises(ValueError, match="StockTrim API credentials are required"),
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

        # Client should be properly closed
        # Note: We can't easily test this without the actual generated client
