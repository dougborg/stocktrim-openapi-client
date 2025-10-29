# Testing Guide

## Overview

The StockTrim client includes comprehensive tests covering transport-layer resilience,
API client functionality, and integration patterns.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_stocktrim_client.py       # Main client tests
├── test_transport_resilience.py   # Transport-layer retry logic
├── test_api_integration.py        # API endpoint integration tests
├── test_model_validation.py       # Data model validation tests
└── test_auth_headers.py          # Authentication header tests
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
uv run poe test

# Run with coverage report
uv run poe test-coverage

# Run specific test types
uv run poe test-unit
uv run poe test-integration
```

### Test Categories

#### Unit Tests

Test individual components in isolation:

```bash
# Run only unit tests
poetry run pytest -m "not integration"

# Test specific modules
poetry run pytest tests/test_stocktrim_client.py
poetry run pytest tests/test_transport_resilience.py
```

#### Integration Tests

Test actual API interactions (require credentials):

```bash
# Run only integration tests
poetry run pytest -m integration

# Requires .env file with:
# STOCKTRIM_API_AUTH_ID=your_tenant_id
# STOCKTRIM_API_AUTH_SIGNATURE=your_tenant_name
```

## Test Configuration

### Environment Setup

```bash
# .env.test (for integration tests)
STOCKTRIM_API_AUTH_ID=test_tenant_id
STOCKTRIM_API_AUTH_SIGNATURE=test_tenant_name
STOCKTRIM_BASE_URL=https://api.stocktrim.com
```

### Pytest Configuration

Located in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--disable-warnings",
]
testpaths = ["tests"]
markers = [
    "integration: marks tests as integration tests requiring API credentials",
    "slow: marks tests as slow running",
]
```

## Writing Tests

### Client Tests Pattern

```python
import pytest
from stocktrim_public_api_client import StockTrimClient

@pytest.mark.asyncio
async def test_client_initialization():
    """Test client can be initialized with credentials."""
    async with StockTrimClient(
        api_auth_id="test_id",
        api_auth_signature="test_signature"
    ) as client:
        assert client.api_auth_id == "test_id"
        assert client.api_auth_signature == "test_signature"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_call_with_auth():
    """Test actual API call with authentication headers."""
    from stocktrim_public_api_client.generated.api.products import get_api_products

    async with StockTrimClient() as client:
        response = await get_api_products.asyncio_detailed(client=client)

        # Handle common responses
        if response.status_code == 200:
            assert response.parsed is not None
        elif response.status_code == 404:
            # No products in test environment is OK
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
```

### Transport Resilience Tests

```python
import httpx
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_retry_on_network_error():
    """Test that network errors trigger retries."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # First call fails, second succeeds
        mock_request.side_effect = [
            httpx.ConnectError("Network error"),
            httpx.Response(200, json={"data": "success"})
        ]

        async with StockTrimClient() as client:
            # Should succeed after retry
            response = await some_api_call(client)
            assert response.status_code == 200
            assert mock_request.call_count == 2
```

### Model Validation Tests

```python
from stocktrim_public_api_client.generated.models import Customer, CustomerDto

def test_customer_dto_structure():
    """Test StockTrim native customer model."""
    customer_dto = CustomerDto(
        code="CUST001",
        name="John Doe",
        email="john@example.com",
        street_address="123 Main St",
        city="Springfield",
        state="IL",
        postal_code="62701"
    )

    assert customer_dto.code == "CUST001"
    assert customer_dto.name == "John Doe"
    # Flat structure for StockTrim native format

def test_customer_integration_structure():
    """Test Square integration customer model."""
    from stocktrim_public_api_client.generated.models import Address

    customer = Customer(
        given_name="John",
        family_name="Doe",
        email_address="john@example.com",
        address=Address(
            address_line_1="123 Main St",
            locality="Springfield",
            administrative_district_level_1="IL",
            postal_code="62701"
        )
    )

    assert customer.given_name == "John"
    assert customer.family_name == "Doe"
    # Nested structure for Square integration format
```

## Mock Strategies

### External API Mocking

```python
import pytest
from unittest.mock import AsyncMock, patch
import httpx

@pytest.fixture
def mock_successful_response():
    """Mock a successful API response."""
    response = AsyncMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"data": "test"}
    response.headers = {"content-type": "application/json"}
    return response

@pytest.fixture
def mock_error_response():
    """Mock an error API response."""
    response = AsyncMock(spec=httpx.Response)
    response.status_code = 500
    response.json.return_value = {"error": "Server error"}
    return response

@pytest.mark.asyncio
async def test_api_error_handling(mock_error_response):
    """Test handling of API errors."""
    with patch('httpx.AsyncClient.request', return_value=mock_error_response):
        async with StockTrimClient() as client:
            response = await api_call(client)
            assert response.status_code == 500
```

### Transport Layer Mocking

```python
@pytest.mark.asyncio
async def test_transport_retry_logic():
    """Test transport layer retry behavior."""
    from stocktrim_public_api_client.stocktrim_client import ResilientAsyncTransport

    # Mock underlying transport
    mock_transport = AsyncMock()
    mock_transport.arequest.side_effect = [
        httpx.ConnectError("Connection failed"),
        httpx.Response(200, json={"success": True})
    ]

    transport = ResilientAsyncTransport(mock_transport)

    # Should retry and succeed
    response = await transport.arequest(
        method="GET",
        url="https://api.stocktrim.com/test"
    )

    assert response.status_code == 200
    assert mock_transport.arequest.call_count == 2
```

## Test Data Management

### Using Fixtures

```python
@pytest.fixture
def sample_customer_dto():
    """Provide sample StockTrim customer data."""
    return CustomerDto(
        code="TEST001",
        name="Test Customer",
        email="test@example.com",
        phone="555-1234",
        street_address="123 Test St",
        city="Test City",
        state="TS",
        postal_code="12345"
    )

@pytest.fixture
def sample_customer_square():
    """Provide sample Square customer data."""
    return Customer(
        given_name="Test",
        family_name="Customer",
        email_address="test@example.com",
        phone_number="555-1234",
        address=Address(
            address_line_1="123 Test St",
            locality="Test City",
            administrative_district_level_1="TS",
            postal_code="12345"
        )
    )
```

### Test Database Cleanup

For integration tests that modify data:

```python
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Clean up test data after each test."""
    yield  # Run the test

    # Cleanup logic
    async with StockTrimClient() as client:
        # Delete test customers, products, etc.
        pass
```

## Coverage Configuration

Coverage settings in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["stocktrim_public_api_client"]
omit = [
    "*/generated/*",  # Exclude generated OpenAPI client
    "*/tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:

- Pull requests
- Pushes to main branch
- Python versions: 3.11, 3.12, 3.13

### Quality Gates

All tests must pass before merging:

```bash
# Quality pipeline
uv run poe ci

# Which runs:
# - uv run poe lint          # Type checking
# - uv run poe format-check  # Formatting validation
# - uv run poe test          # Test suite
```

## Debugging Tests

### Verbose Output

```bash
# Run tests with detailed output
poetry run pytest -v

# Show print statements
poetry run pytest -s

# Stop on first failure
poetry run pytest -x

# Run specific test
poetry run pytest tests/test_stocktrim_client.py::test_client_initialization -v
```

### Debug Integration Issues

```bash
# Run integration tests with debug logging
PYTHONPATH=. poetry run pytest -m integration -v -s --log-cli-level=DEBUG
```

### IDE Integration

For PyCharm/VSCode:

1. Set Python interpreter to Poetry virtual environment
1. Set test framework to pytest
1. Set working directory to project root
1. Add environment variables for integration tests

## Best Practices

### Test Organization

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test API interactions, require credentials
- **Mock external dependencies**: Don't hit real APIs in unit tests
- **Use fixtures**: Share common test data and setup

### Assertion Patterns

```python
# ✅ Good - specific assertions
assert response.status_code == 200
assert len(response.parsed) > 0
assert customer.code == "CUST001"

# ❌ Avoid - vague assertions
assert response  # What does this test?
assert data      # Too generic
```

### Error Testing

```python
# ✅ Good - test specific error scenarios
with pytest.raises(ValueError, match="Invalid auth signature"):
    StockTrimClient(api_auth_signature="")

# ✅ Good - test error recovery
async with StockTrimClient() as client:
    response = await api_call(client)
    if response.status_code != 200:
        # Handle error appropriately for the context
        assert response.status_code in [404, 401, 500]
```

This testing guide ensures comprehensive coverage of the StockTrim client's
functionality while maintaining clear separation between unit and integration tests.
