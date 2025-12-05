"""
Unit tests for error handling.

Tests error response formatting and error classes.
"""

import pytest
from mobius.api.errors import (
    MobiusError,
    ValidationError,
    NotFoundError,
    StorageError,
    GenerationError,
    AuditError,
    ErrorResponse,
    ErrorDetail,
)


def test_mobius_error_structure():
    """Test that MobiusError creates correct error structure."""
    error = MobiusError(
        status_code=500,
        code="TEST_ERROR",
        message="Test error message",
        request_id="req_test123",
        details={"key": "value"},
    )

    assert error.status_code == 500
    assert error.error_response.error.code == "TEST_ERROR"
    assert error.error_response.error.message == "Test error message"
    assert error.error_response.error.request_id == "req_test123"
    assert error.error_response.error.details == {"key": "value"}


def test_mobius_error_to_dict():
    """Test that MobiusError converts to dictionary correctly."""
    error = MobiusError(
        status_code=400,
        code="BAD_REQUEST",
        message="Invalid input",
        request_id="req_abc123",
    )

    error_dict = error.to_dict()

    assert "error" in error_dict
    assert error_dict["error"]["code"] == "BAD_REQUEST"
    assert error_dict["error"]["message"] == "Invalid input"
    assert error_dict["error"]["request_id"] == "req_abc123"
    assert error_dict["error"]["details"] == {}


def test_validation_error():
    """Test ValidationError creates 422 status code."""
    error = ValidationError(
        code="INVALID_INPUT", message="Field is required", request_id="req_val123"
    )

    assert error.status_code == 422
    assert error.error_response.error.code == "INVALID_INPUT"
    assert error.error_response.error.message == "Field is required"


def test_not_found_error():
    """Test NotFoundError creates correct error message."""
    error = NotFoundError(resource="brand", resource_id="brand-123", request_id="req_nf123")

    assert error.status_code == 404
    assert error.error_response.error.code == "BRAND_NOT_FOUND"
    assert "brand-123" in error.error_response.error.message
    assert "does not exist" in error.error_response.error.message


def test_storage_error():
    """Test StorageError creates correct error message."""
    error = StorageError(operation="upload", request_id="req_storage123")

    assert error.status_code == 500
    assert error.error_response.error.code == "STORAGE_ERROR"
    assert "upload" in error.error_response.error.message


def test_generation_error():
    """Test GenerationError creates correct error."""
    error = GenerationError(
        message="Image generation failed", request_id="req_gen123", details={"reason": "timeout"}
    )

    assert error.status_code == 500
    assert error.error_response.error.code == "GENERATION_FAILED"
    assert error.error_response.error.message == "Image generation failed"
    assert error.error_response.error.details == {"reason": "timeout"}


def test_audit_error():
    """Test AuditError creates correct error."""
    error = AuditError(message="Audit service unavailable", request_id="req_audit123")

    assert error.status_code == 500
    assert error.error_response.error.code == "AUDIT_FAILED"
    assert error.error_response.error.message == "Audit service unavailable"


def test_error_detail_model():
    """Test ErrorDetail Pydantic model."""
    detail = ErrorDetail(
        code="TEST_CODE", message="Test message", details={"foo": "bar"}, request_id="req_123"
    )

    assert detail.code == "TEST_CODE"
    assert detail.message == "Test message"
    assert detail.details == {"foo": "bar"}
    assert detail.request_id == "req_123"


def test_error_response_model():
    """Test ErrorResponse Pydantic model."""
    detail = ErrorDetail(
        code="TEST_CODE", message="Test message", details={}, request_id="req_123"
    )
    response = ErrorResponse(error=detail)

    assert response.error.code == "TEST_CODE"
    assert response.error.message == "Test message"


def test_error_with_no_details():
    """Test that errors work correctly without details."""
    error = MobiusError(
        status_code=500, code="ERROR", message="Something went wrong", request_id="req_123"
    )

    error_dict = error.to_dict()
    assert error_dict["error"]["details"] == {}
