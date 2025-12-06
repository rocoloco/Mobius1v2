"""
Property-based tests for error response structure.

**Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**

Tests that all error responses follow consistent structure and include request_id.
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


# Property: Error responses include request_id
@given(
    error_code=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Nd")) | st.just("_")),
    error_message=st.text(min_size=1, max_size=200),
    status_code=st.sampled_from([400, 404, 422, 500, 503]),
)
def test_mobius_error_includes_request_id(error_code: str, error_message: str, status_code: int):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**
    
    *For any* MobiusError with any error code, message, and status code,
    the error response should include a request_id field.
    
    **Validates: Requirements 9.4, 9.5**
    
    This property test verifies that all error responses include request_id for tracing.
    """
    request_id = generate_request_id()
    
    error = MobiusError(
        status_code=status_code,
        code=error_code,
        message=error_message,
        request_id=request_id,
    )
    
    # Verify error response structure
    assert hasattr(error, "error_response"), "MobiusError should have error_response attribute"
    
    error_dict = error.error_response.model_dump()
    
    # Verify structure
    assert "error" in error_dict, "Error response should have 'error' key"
    assert "code" in error_dict["error"], "Error should have 'code' field"
    assert "message" in error_dict["error"], "Error should have 'message' field"
    assert "request_id" in error_dict["error"], "Error should have 'request_id' field"
    
    # Verify values
    assert error_dict["error"]["code"] == error_code
    assert error_dict["error"]["message"] == error_message
    assert error_dict["error"]["request_id"] == request_id
    
    # Verify request_id format
    assert error_dict["error"]["request_id"].startswith("req_"), (
        f"Request ID should start with 'req_' prefix, got: {error_dict['error']['request_id']}"
    )


@given(
    error_message=st.text(min_size=1, max_size=200),
)
def test_validation_error_includes_request_id(error_message: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**
    
    *For any* ValidationError with any message, the error response should include a request_id field.
    
    **Validates: Requirements 9.4, 9.5**
    """
    request_id = generate_request_id()
    
    error = ValidationError(
        code="VALIDATION_ERROR",
        message=error_message,
        request_id=request_id,
    )
    
    # Verify status code
    assert error.status_code == 422, "ValidationError should have status code 422"
    
    # Verify error response structure
    error_dict = error.error_response.model_dump()
    assert error_dict["error"]["request_id"] == request_id
    assert error_dict["error"]["request_id"].startswith("req_")


@given(
    resource=st.sampled_from(["brand", "asset", "template", "job"]),
    resource_id=st.text(min_size=1, max_size=50),
)
def test_not_found_error_includes_request_id(resource: str, resource_id: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**
    
    *For any* NotFoundError with any resource type and ID, the error response should include a request_id field.
    
    **Validates: Requirements 9.4, 9.5**
    """
    request_id = generate_request_id()
    
    error = NotFoundError(
        resource=resource,
        resource_id=resource_id,
        request_id=request_id,
    )
    
    # Verify status code
    assert error.status_code == 404, "NotFoundError should have status code 404"
    
    # Verify error response structure
    error_dict = error.error_response.model_dump()
    assert error_dict["error"]["request_id"] == request_id
    assert error_dict["error"]["request_id"].startswith("req_")
    
    # Verify error message includes resource info
    assert resource in error_dict["error"]["message"].lower()
    assert resource_id in error_dict["error"]["message"]


@given(
    operation=st.text(min_size=1, max_size=50),
)
def test_storage_error_includes_request_id(operation: str):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**
    
    *For any* StorageError with any operation, the error response should include a request_id field.
    
    **Validates: Requirements 9.4, 9.5**
    """
    request_id = generate_request_id()
    
    error = StorageError(
        operation=operation,
        request_id=request_id,
    )
    
    # Verify status code
    assert error.status_code == 500, "StorageError should have status code 500"
    
    # Verify error response structure
    error_dict = error.error_response.model_dump()
    assert error_dict["error"]["request_id"] == request_id
    assert error_dict["error"]["request_id"].startswith("req_")
    
    # Verify error message includes operation
    assert operation in error_dict["error"]["message"]


def test_error_response_structure_consistency():
    """
    Verify that all error types follow the same response structure.
    
    This ensures consistency across all error responses in the API.
    """
    request_id = generate_request_id()
    
    errors = [
        MobiusError(400, "TEST_ERROR", "Test message", request_id),
        ValidationError("VALIDATION_ERROR", "Validation failed", request_id),
        NotFoundError("brand", "test-id", request_id),
        StorageError("test_operation", request_id),
    ]
    
    for error in errors:
        error_dict = error.error_response.model_dump()
        
        # All errors should have the same top-level structure
        assert set(error_dict.keys()) == {"error"}, (
            f"Error response should only have 'error' key, got: {error_dict.keys()}"
        )
        
        # All errors should have the same error object structure
        error_obj = error_dict["error"]
        required_fields = {"code", "message", "request_id"}
        assert required_fields.issubset(error_obj.keys()), (
            f"Error object should have fields {required_fields}, got: {error_obj.keys()}"
        )
        
        # All request_ids should follow the same format
        assert error_obj["request_id"].startswith("req_"), (
            f"Request ID should start with 'req_', got: {error_obj['request_id']}"
        )


@given(
    details=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False, allow_infinity=False)),
        min_size=0,
        max_size=5,
    )
)
def test_error_with_details_includes_request_id(details: dict):
    """
    **Feature: mobius-phase-2-refactor, Property (custom): Error responses include request_id**
    
    *For any* error with additional details, the error response should include both
    the details and the request_id field.
    
    **Validates: Requirements 9.4, 9.5**
    """
    request_id = generate_request_id()
    
    error = MobiusError(
        status_code=400,
        code="TEST_ERROR",
        message="Test error with details",
        request_id=request_id,
        details=details,
    )
    
    error_dict = error.error_response.model_dump()
    
    # Verify request_id is present
    assert error_dict["error"]["request_id"] == request_id
    
    # Verify details are present if provided
    if details:
        assert "details" in error_dict["error"], "Error should include details field when provided"
        assert error_dict["error"]["details"] == details


def test_request_id_uniqueness():
    """
    Verify that generated request IDs are unique.
    
    This ensures that each request can be uniquely identified for tracing.
    """
    # Generate multiple request IDs
    request_ids = [generate_request_id() for _ in range(100)]
    
    # All should be unique
    assert len(request_ids) == len(set(request_ids)), (
        "All generated request IDs should be unique"
    )
    
    # All should follow the format
    for request_id in request_ids:
        assert request_id.startswith("req_"), (
            f"Request ID should start with 'req_', got: {request_id}"
        )
        assert len(request_id) > 4, (
            f"Request ID should have content after 'req_' prefix, got: {request_id}"
        )


@given(
    status_code=st.sampled_from([400, 404, 422, 500, 503]),
)
def test_error_status_code_preserved(status_code: int):
    """
    Verify that the HTTP status code is correctly preserved in error objects.
    
    This ensures that errors return the appropriate HTTP status codes.
    """
    request_id = generate_request_id()
    
    error = MobiusError(
        status_code=status_code,
        code="TEST_ERROR",
        message="Test message",
        request_id=request_id,
    )
    
    assert error.status_code == status_code, (
        f"Error status code should be {status_code}, got: {error.status_code}"
    )
