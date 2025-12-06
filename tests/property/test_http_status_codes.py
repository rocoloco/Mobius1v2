"""
Property-based tests for HTTP status code consistency.

**Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**

Tests that all API operations return appropriate HTTP status codes.
"""

from hypothesis import given, strategies as st
import pytest
from mobius.api.errors import (
    MobiusError,
    ValidationError,
    NotFoundError,
    StorageError,
)
from mobius.api.utils import generate_request_id


# Property: Appropriate status codes returned
def test_validation_error_returns_422():
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* ValidationError, the HTTP status code should be 422 (Unprocessable Entity).
    
    **Validates: Requirements 9.3**
    
    This test verifies that validation errors return the correct HTTP status code.
    """
    request_id = generate_request_id()
    
    error = ValidationError(
        code="VALIDATION_ERROR",
        message="Validation failed",
        request_id=request_id,
    )
    
    assert error.status_code == 422, (
        f"ValidationError should return status code 422, got: {error.status_code}"
    )


def test_not_found_error_returns_404():
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* NotFoundError, the HTTP status code should be 404 (Not Found).
    
    **Validates: Requirements 9.3**
    
    This test verifies that not found errors return the correct HTTP status code.
    """
    request_id = generate_request_id()
    
    error = NotFoundError(
        resource="brand",
        resource_id="test-id",
        request_id=request_id,
    )
    
    assert error.status_code == 404, (
        f"NotFoundError should return status code 404, got: {error.status_code}"
    )


def test_storage_error_returns_500():
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* StorageError, the HTTP status code should be 500 (Internal Server Error).
    
    **Validates: Requirements 9.3**
    
    This test verifies that storage errors return the correct HTTP status code.
    """
    request_id = generate_request_id()
    
    error = StorageError(
        operation="test_operation",
        request_id=request_id,
    )
    
    assert error.status_code == 500, (
        f"StorageError should return status code 500, got: {error.status_code}"
    )


@given(
    status_code=st.sampled_from([400, 404, 422, 500, 503]),
)
def test_mobius_error_preserves_status_code(status_code: int):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* MobiusError with a specified status code, the error should preserve
    that status code.
    
    **Validates: Requirements 9.3**
    
    This property test verifies that custom status codes are preserved.
    """
    request_id = generate_request_id()
    
    error = MobiusError(
        status_code=status_code,
        code="TEST_ERROR",
        message="Test message",
        request_id=request_id,
    )
    
    assert error.status_code == status_code, (
        f"MobiusError should preserve status code {status_code}, got: {error.status_code}"
    )


def test_error_type_status_code_mapping():
    """
    Verify that each error type has the correct default status code.
    
    This ensures consistency in error handling across the API.
    """
    request_id = generate_request_id()
    
    # Define expected status codes for each error type
    error_mappings = [
        (ValidationError("TEST", "Test", request_id), 422),
        (NotFoundError("brand", "test-id", request_id), 404),
        (StorageError("test_op", request_id), 500),
    ]
    
    for error, expected_status in error_mappings:
        assert error.status_code == expected_status, (
            f"{error.__class__.__name__} should have status code {expected_status}, "
            f"got: {error.status_code}"
        )


@given(
    resource=st.sampled_from(["brand", "asset", "template", "job", "feedback"]),
    resource_id=st.text(min_size=1, max_size=50),
)
def test_not_found_error_always_404(resource: str, resource_id: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* resource type and resource ID, NotFoundError should always return 404.
    
    **Validates: Requirements 9.3**
    """
    request_id = generate_request_id()
    
    error = NotFoundError(
        resource=resource,
        resource_id=resource_id,
        request_id=request_id,
    )
    
    assert error.status_code == 404, (
        f"NotFoundError for {resource} should return 404, got: {error.status_code}"
    )


@given(
    code=st.text(min_size=1, max_size=50),
    message=st.text(min_size=1, max_size=200),
)
def test_validation_error_always_422(code: str, message: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* validation error code and message, ValidationError should always return 422.
    
    **Validates: Requirements 9.3**
    """
    request_id = generate_request_id()
    
    error = ValidationError(
        code=code,
        message=message,
        request_id=request_id,
    )
    
    assert error.status_code == 422, (
        f"ValidationError should return 422, got: {error.status_code}"
    )


@given(
    operation=st.text(min_size=1, max_size=50),
)
def test_storage_error_always_500(operation: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* storage operation, StorageError should always return 500.
    
    **Validates: Requirements 9.3**
    """
    request_id = generate_request_id()
    
    error = StorageError(
        operation=operation,
        request_id=request_id,
    )
    
    assert error.status_code == 500, (
        f"StorageError should return 500, got: {error.status_code}"
    )


def test_status_code_ranges():
    """
    Verify that status codes fall into appropriate ranges.
    
    - 4xx: Client errors
    - 5xx: Server errors
    """
    request_id = generate_request_id()
    
    # Client errors (4xx)
    client_errors = [
        ValidationError("TEST", "Test", request_id),
        NotFoundError("brand", "test-id", request_id),
    ]
    
    for error in client_errors:
        assert 400 <= error.status_code < 500, (
            f"{error.__class__.__name__} should return 4xx status code, "
            f"got: {error.status_code}"
        )
    
    # Server errors (5xx)
    server_errors = [
        StorageError("test_op", request_id),
    ]
    
    for error in server_errors:
        assert 500 <= error.status_code < 600, (
            f"{error.__class__.__name__} should return 5xx status code, "
            f"got: {error.status_code}"
        )


def test_http_status_code_semantics():
    """
    Verify that status codes follow HTTP semantics.
    
    - 404: Resource not found
    - 422: Validation/semantic error
    - 500: Internal server error
    """
    request_id = generate_request_id()
    
    # 404: Resource not found
    not_found = NotFoundError("brand", "test-id", request_id)
    assert not_found.status_code == 404
    assert "not" in not_found.error_response.model_dump()["error"]["message"].lower()
    
    # 422: Validation error
    validation = ValidationError("VALIDATION_ERROR", "Invalid input", request_id)
    assert validation.status_code == 422
    
    # 500: Internal server error
    storage = StorageError("database_operation", request_id)
    assert storage.status_code == 500


@given(
    status_code=st.integers(min_value=400, max_value=599),
)
def test_custom_status_codes_in_valid_range(status_code: int):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Appropriate status codes returned**
    
    *For any* custom status code in the 4xx-5xx range, MobiusError should accept it.
    
    **Validates: Requirements 9.3**
    """
    request_id = generate_request_id()
    
    error = MobiusError(
        status_code=status_code,
        code="CUSTOM_ERROR",
        message="Custom error message",
        request_id=request_id,
    )
    
    assert error.status_code == status_code
    assert 400 <= error.status_code < 600, (
        f"Error status codes should be in 4xx-5xx range, got: {error.status_code}"
    )


def test_success_status_codes_not_used_for_errors():
    """
    Verify that error classes don't use success status codes (2xx, 3xx).
    
    Errors should only use 4xx (client error) or 5xx (server error) codes.
    """
    request_id = generate_request_id()
    
    # All error types should use 4xx or 5xx codes
    errors = [
        ValidationError("TEST", "Test", request_id),
        NotFoundError("brand", "test-id", request_id),
        StorageError("test_op", request_id),
    ]
    
    for error in errors:
        assert error.status_code >= 400, (
            f"{error.__class__.__name__} should not use success status codes (2xx/3xx), "
            f"got: {error.status_code}"
        )
