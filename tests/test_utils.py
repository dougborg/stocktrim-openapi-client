"""Tests for the utils module."""

from http import HTTPStatus
from typing import Any, cast
from unittest.mock import Mock

import pytest

from stocktrim_public_api_client.client_types import UNSET, Response
from stocktrim_public_api_client.utils import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PermissionError,
    ServerError,
    ValidationError,
    get_error_message,
    is_error,
    is_success,
    to_unset,
    unwrap,
    unwrap_unset,
)


class TestExceptionHierarchy:
    """Test the exception hierarchy."""

    def test_all_exceptions_inherit_from_api_error(self):
        """Test that all custom exceptions inherit from APIError."""
        assert issubclass(AuthenticationError, APIError)
        assert issubclass(PermissionError, APIError)
        assert issubclass(NotFoundError, APIError)
        assert issubclass(ValidationError, APIError)
        assert issubclass(ServerError, APIError)

    def test_api_error_attributes(self):
        """Test APIError stores status code and problem details."""
        error = APIError("Test error", HTTPStatus.BAD_REQUEST)
        assert error.status_code == HTTPStatus.BAD_REQUEST
        assert error.problem_details is None
        assert str(error) == "Test error"


class TestUnwrap:
    """Test the unwrap function."""

    def test_unwrap_success_response(self):
        """Test unwrapping a successful response."""
        response: Response[dict[str, Any]] = Response(
            status_code=HTTPStatus.OK,
            content=b"",
            headers={},
            parsed={"id": 1, "name": "Test"},
        )
        result = unwrap(response)
        assert result == {"id": 1, "name": "Test"}

    def test_unwrap_none_parsed_raises_by_default(self):
        """Test unwrapping a response with no parsed data raises error."""
        response: Response[None] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        with pytest.raises(APIError, match="No parsed response data"):
            unwrap(response)

    def test_unwrap_none_parsed_returns_none_when_not_raising(self):
        """Test unwrapping a response with no parsed data returns None when raise_on_error=False."""
        response: Response[None] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        result = unwrap(response, raise_on_error=False)
        assert result is None

    def test_unwrap_401_raises_authentication_error(self):
        """Test 401 status raises AuthenticationError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.UNAUTHORIZED, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(AuthenticationError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 401

    def test_unwrap_403_raises_permission_error(self):
        """Test 403 status raises PermissionError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.FORBIDDEN, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(PermissionError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 403

    def test_unwrap_404_raises_not_found_error(self):
        """Test 404 status raises NotFoundError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(NotFoundError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 404

    def test_unwrap_400_raises_validation_error(self):
        """Test 400 status raises ValidationError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(ValidationError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 400

    def test_unwrap_422_raises_validation_error(self):
        """Test 422 status raises ValidationError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=b"",
            headers={},
            parsed=Mock(),
        )
        with pytest.raises(ValidationError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 422

    def test_unwrap_500_raises_server_error(self):
        """Test 500 status raises ServerError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"",
            headers={},
            parsed=Mock(),
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 500

    def test_unwrap_503_raises_server_error(self):
        """Test 503 status raises ServerError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            content=b"",
            headers={},
            parsed=Mock(),
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 503

    def test_unwrap_error_returns_none_when_not_raising(self):
        """Test error response returns None when raise_on_error=False."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=Mock()
        )
        result = unwrap(response, raise_on_error=False)
        assert result is None

    def test_unwrap_generic_4xx_raises_api_error(self):
        """Test generic 4xx status raises APIError."""
        response: Response[Any] = Response(
            status_code=cast(HTTPStatus, 418),  # Non-standard status code
            content=b"",
            headers={},
            parsed=Mock(),
        )
        with pytest.raises(APIError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 418
        assert not isinstance(
            exc_info.value,
            AuthenticationError | PermissionError | NotFoundError | ValidationError,
        )

    def test_unwrap_500_with_unparseable_body_raises_server_error(self):
        """A 5xx response whose body did not parse (parsed=None) must still
        raise ServerError, not the misleading 'No parsed response data' APIError.

        Regression: StockTrim's Order Plan endpoint occasionally returns 500
        with an HTML stack-trace body the OpenAPI client cannot decode."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"<html>...</html>",
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 500
        assert "No parsed response data" not in str(exc_info.value)

    def test_unwrap_error_message_includes_body_excerpt(self):
        """When parsed=None on an error, surface the raw body in the exception
        message so callers can debug 5xx/415 without diving into transport logs."""
        body = b'{"error":"required field \'location\' missing"}'
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=body,
            headers={"Content-Type": "application/json"},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert "required field 'location' missing" in str(exc_info.value)

    def test_unwrap_error_message_truncates_long_body(self):
        """Very long bodies (HTML stack traces, etc.) get truncated to keep
        log/MCP-error lines manageable, but the truncation marker preserves
        the original length so operators know how much was dropped."""
        long_body = b"x" * 5000
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=long_body,
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        message = str(exc_info.value)
        assert "+4500 chars" in message  # 5000 total - 500 limit
        # Message stays bounded — limit + envelope is < 700 chars.
        assert len(message) < 700

    def test_unwrap_error_message_omits_body_when_empty(self):
        """No body → no trailing colon — keeps the bare 'API error with status N'
        message clean for empty 5xx responses."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"",
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert str(exc_info.value) == "API error with status 500"

    def test_unwrap_error_message_handles_undecodable_body(self):
        """Bodies that aren't valid UTF-8 (binary blobs) fall back to a
        ``<N bytes, undecodable>`` placeholder so the exception text stays
        printable instead of leaking raw bytes or U+FFFD into log lines."""
        # 0xff is an invalid UTF-8 start byte — strict decode fails.
        content = b"\xff\xfe\x00bin"
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=content,
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        assert f"<{len(content)} bytes, undecodable>" in str(exc_info.value)

    def test_unwrap_error_message_escapes_control_chars_in_text_body(self):
        """Valid-UTF-8 bodies with embedded control characters (e.g. NUL from
        a corrupted response) have those chars escaped as ``\\xNN`` so they
        don't break log/MCP-error formatting; legitimate whitespace
        (``\\n``, ``\\r``, ``\\t``) passes through unchanged."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"prefix\x00\x01\nstill text\t!",
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        msg = str(exc_info.value)
        # Control chars escaped:
        assert "\\x00" in msg
        assert "\\x01" in msg
        # Raw control chars NOT present in the message:
        assert "\x00" not in msg
        assert "\x01" not in msg
        # Legitimate whitespace preserved:
        assert "\nstill text\t!" in msg

    def test_unwrap_error_message_bounds_escaped_output_for_all_controls(self):
        """A body composed entirely of control chars expands 4x when escaped
        (each ``\\x00`` becomes the 4-char sequence ``\\x00``). The output
        must still be bounded to roughly ``_BODY_EXCERPT_LIMIT`` characters
        — not 4x that — so log lines stay manageable even in pathological
        cases."""
        from stocktrim_public_api_client.utils import _BODY_EXCERPT_LIMIT

        # 2000 NUL bytes → 8000 chars after naïve full-body escape; bounded
        # impl should stop at the first _BODY_EXCERPT_LIMIT chars of output.
        nul_body = b"\x00" * 2000
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=nul_body,
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        msg = str(exc_info.value)
        # Each NUL escapes to 4 chars, so the budget fits LIMIT/4 source chars.
        # The suffix reports the remaining 2000 - LIMIT/4 dropped chars.
        kept = _BODY_EXCERPT_LIMIT // 4
        assert f"+{2000 - kept} chars" in msg
        # Strict upper bound: escaped excerpt ≤ limit, plus a short suffix
        # (≤ 30 chars: "…[+NNNN chars]"). Total stays well under 4x limit.
        assert len(msg) < _BODY_EXCERPT_LIMIT * 2

    def test_unwrap_error_message_escapes_del_and_c1_controls(self):
        """DEL (``\\x7f``) and the C1 range (``\\x80``-``\\x9f``) are also
        control characters and should be escaped, even though they sit above
        the C0 range. Plain ASCII printables stay unescaped."""
        # Valid UTF-8: \x7f is single-byte ASCII DEL, \xc2\x80 is U+0080 (C1),
        # \xc2\x9f is U+009F (last C1).
        response: Response[Any] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"ok\x7fDEL\xc2\x80C1lo\xc2\x9fhi",
            headers={},
            parsed=None,
        )
        with pytest.raises(ServerError) as exc_info:
            unwrap(response)
        msg = str(exc_info.value)
        assert "\\x7f" in msg
        assert "\\x80" in msg
        assert "\\x9f" in msg
        # Printable ASCII chunks should still be present:
        assert "okDEL" not in msg  # the DEL between them got escaped
        assert "ok\\x7fDEL" in msg

    def test_unwrap_404_with_unparseable_body_raises_not_found_error(self):
        """A 404 with parsed=None should raise NotFoundError, not generic APIError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=None
        )
        with pytest.raises(NotFoundError) as exc_info:
            unwrap(response)
        assert exc_info.value.status_code == 404

    def test_unwrap_2xx_with_no_parsed_body_raises_generic_api_error(self):
        """A 2xx with no parsed body still hits the original APIError path
        (this is the only legitimate use of 'No parsed response data')."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        with pytest.raises(APIError) as exc_info:
            unwrap(response)
        assert "No parsed response data" in str(exc_info.value)


class TestIsSuccess:
    """Test the is_success function."""

    def test_200_is_success(self):
        """Test 200 status is success."""
        response: Response[None] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        assert is_success(response) is True

    def test_201_is_success(self):
        """Test 201 status is success."""
        response: Response[None] = Response(
            status_code=HTTPStatus.CREATED, content=b"", headers={}, parsed=None
        )
        assert is_success(response) is True

    def test_299_is_success(self):
        """Test 299 status is success."""
        response: Response[None] = Response(
            status_code=cast(HTTPStatus, 299),  # Non-standard status code
            content=b"",
            headers={},
            parsed=None,
        )
        assert is_success(response) is True

    def test_300_is_not_success(self):
        """Test 300 status is not success."""
        response: Response[None] = Response(
            status_code=cast(HTTPStatus, 300),  # Non-standard status code
            content=b"",
            headers={},
            parsed=None,
        )
        assert is_success(response) is False

    def test_400_is_not_success(self):
        """Test 400 status is not success."""
        response: Response[None] = Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=None
        )
        assert is_success(response) is False

    def test_500_is_not_success(self):
        """Test 500 status is not success."""
        response: Response[None] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"",
            headers={},
            parsed=None,
        )
        assert is_success(response) is False


class TestIsError:
    """Test the is_error function."""

    def test_200_is_not_error(self):
        """Test 200 status is not error."""
        response: Response[None] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        assert is_error(response) is False

    def test_300_is_not_error(self):
        """Test 300 status is not error."""
        response: Response[None] = Response(
            status_code=cast(HTTPStatus, 300),  # Non-standard status code
            content=b"",
            headers={},
            parsed=None,
        )
        assert is_error(response) is False

    def test_400_is_error(self):
        """Test 400 status is error."""
        response: Response[None] = Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=None
        )
        assert is_error(response) is True

    def test_404_is_error(self):
        """Test 404 status is error."""
        response: Response[None] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=None
        )
        assert is_error(response) is True

    def test_500_is_error(self):
        """Test 500 status is error."""
        response: Response[None] = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b"",
            headers={},
            parsed=None,
        )
        assert is_error(response) is True


class TestGetErrorMessage:
    """Test the get_error_message function."""

    def test_success_returns_none(self):
        """Test successful response returns None."""
        response: Response[None] = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None
        )
        assert get_error_message(response) is None

    def test_error_without_problem_details_returns_status_code(self):
        """Test error without ProblemDetails returns status code."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=Mock()
        )
        message = get_error_message(response)
        assert message == "HTTP 404"

    def test_400_error_returns_message(self):
        """Test 400 error returns message."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=Mock()
        )
        message = get_error_message(response)
        assert message is not None
        assert "400" in message


class TestUnwrapUnset:
    """Test the unwrap_unset helper."""

    def test_value_passes_through(self):
        assert unwrap_unset(42) == 42
        assert unwrap_unset("hello") == "hello"
        assert unwrap_unset(0) == 0
        assert unwrap_unset(False) is False

    def test_unset_without_default_returns_none(self):
        assert unwrap_unset(UNSET) is None

    def test_none_without_default_returns_none(self):
        assert unwrap_unset(None) is None

    def test_unset_with_default_returns_default(self):
        assert unwrap_unset(UNSET, 0) == 0
        assert unwrap_unset(UNSET, "n/a") == "n/a"
        assert unwrap_unset(UNSET, []) == []

    def test_none_with_default_returns_default(self):
        assert unwrap_unset(None, 0) == 0
        assert unwrap_unset(None, "fallback") == "fallback"

    def test_value_with_default_passes_through(self):
        assert unwrap_unset(42, 0) == 42
        assert unwrap_unset("real", "fallback") == "real"

    def test_default_can_have_different_type(self):
        # Common case: int | Unset value with float("inf") default for use as
        # a sort key. The second TypeVar widens the return type to T | D so
        # callers don't need a misleading cast(...) at the call site.
        result = unwrap_unset(UNSET, float("inf"))
        assert result == float("inf")
        # Real-value path still returns the value's own type.
        result_with_value = unwrap_unset(7, float("inf"))
        assert result_with_value == 7


class TestToUnset:
    """Test the to_unset helper."""

    def test_value_passes_through(self):
        assert to_unset(42) == 42
        assert to_unset("hello") == "hello"
        assert to_unset(0) == 0
        assert to_unset(False) is False

    def test_none_becomes_unset(self):
        assert to_unset(None) is UNSET

    def test_round_trip_with_unwrap_unset(self):
        # Pydantic None → UNSET (outbound) → None (inbound) preserves intent.
        assert unwrap_unset(to_unset(None)) is None
        assert unwrap_unset(to_unset(42)) == 42
