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
