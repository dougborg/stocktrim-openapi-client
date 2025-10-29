"""Tests for the utils module."""

from http import HTTPStatus
from typing import Any, cast
from unittest.mock import Mock

import pytest

from stocktrim_public_api_client.client_types import Response
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
    unwrap,
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
        assert cast(AuthenticationError, exc_info.value).status_code == 401

    def test_unwrap_403_raises_permission_error(self):
        """Test 403 status raises PermissionError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.FORBIDDEN, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(PermissionError) as exc_info:
            unwrap(response)
        assert cast(PermissionError, exc_info.value).status_code == 403

    def test_unwrap_404_raises_not_found_error(self):
        """Test 404 status raises NotFoundError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(NotFoundError) as exc_info:
            unwrap(response)
        assert cast(NotFoundError, exc_info.value).status_code == 404

    def test_unwrap_400_raises_validation_error(self):
        """Test 400 status raises ValidationError."""
        response: Response[Any] = Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=Mock()
        )
        with pytest.raises(ValidationError) as exc_info:
            unwrap(response)
        assert cast(ValidationError, exc_info.value).status_code == 400

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
        assert cast(ValidationError, exc_info.value).status_code == 422

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
        assert cast(ServerError, exc_info.value).status_code == 500

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
        assert cast(ServerError, exc_info.value).status_code == 503

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
        assert cast(APIError, exc_info.value).status_code == 418
        assert not isinstance(
            exc_info.value,
            AuthenticationError | PermissionError | NotFoundError | ValidationError,
        )


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
