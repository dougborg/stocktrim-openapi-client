"""Tests for utility functions in the StockTrim MCP Server."""

from enum import IntEnum

from stocktrim_mcp_server.utils import get_status_name, unset_to_none
from stocktrim_public_api_client.client_types import UNSET


class SampleStatus(IntEnum):
    """Sample IntEnum for testing status handling."""

    DRAFT = 0
    APPROVED = 1
    SENT = 2
    RECEIVED = 3


class TestUnsetToNone:
    """Tests for unset_to_none utility function."""

    def test_unset_converts_to_none(self):
        """Test that UNSET is converted to None."""
        result = unset_to_none(UNSET)
        assert result is None

    def test_string_value_preserved(self):
        """Test that string values are preserved."""
        result = unset_to_none("test")
        assert result == "test"

    def test_integer_value_preserved(self):
        """Test that integer values are preserved."""
        result = unset_to_none(123)
        assert result == 123

    def test_none_value_preserved(self):
        """Test that None values are preserved."""
        result = unset_to_none(None)
        assert result is None


class TestGetStatusName:
    """Tests for get_status_name utility function."""

    def test_valid_status_returns_name(self):
        """Test that valid IntEnum status returns its name."""
        result = get_status_name(SampleStatus.DRAFT)
        assert result == "DRAFT"

        result = get_status_name(SampleStatus.APPROVED)
        assert result == "APPROVED"

    def test_none_returns_none(self):
        """Test that None returns None."""
        result = get_status_name(None)
        assert result is None

    def test_unset_returns_none(self):
        """Test that UNSET returns None."""
        result = get_status_name(UNSET)
        assert result is None

    def test_zero_value_status(self):
        """Test that status with value 0 is handled correctly."""
        # This is important because DRAFT = 0, and we need to ensure
        # the check doesn't fail on falsy values
        result = get_status_name(SampleStatus.DRAFT)
        assert result == "DRAFT"

    def test_all_enum_values(self):
        """Test all enum values in the sample status."""
        statuses = [
            (SampleStatus.DRAFT, "DRAFT"),
            (SampleStatus.APPROVED, "APPROVED"),
            (SampleStatus.SENT, "SENT"),
            (SampleStatus.RECEIVED, "RECEIVED"),
        ]

        for status, expected_name in statuses:
            result = get_status_name(status)
            assert result == expected_name, (
                f"Status {status} should return {expected_name}"
            )
