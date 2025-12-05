"""
Error handling utilities.

Provides structured error responses with consistent formatting.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: ErrorDetail


class MobiusError(Exception):
    """
    Base exception for Mobius API errors.

    All Mobius errors follow a consistent structure with:
    - HTTP status code
    - Error code (for programmatic handling)
    - Human-readable message
    - Request ID (for tracing)
    - Optional details dictionary
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        request_id: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_response = ErrorResponse(
            error=ErrorDetail(
                code=code, message=message, details=details or {}, request_id=request_id
            )
        )
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return self.error_response.model_dump()


class ValidationError(MobiusError):
    """
    Validation error (422 Unprocessable Entity).

    Used when request data fails validation.
    """

    def __init__(
        self, code: str, message: str, request_id: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(422, code, message, request_id, details)


class NotFoundError(MobiusError):
    """
    Resource not found error (404 Not Found).

    Used when a requested resource does not exist.
    """

    def __init__(self, resource: str, resource_id: str, request_id: str):
        super().__init__(
            404,
            f"{resource.upper()}_NOT_FOUND",
            f"{resource} with ID {resource_id} does not exist",
            request_id,
        )


class StorageError(MobiusError):
    """
    Storage operation error (500 Internal Server Error).

    Used when file storage or database operations fail.
    """

    def __init__(
        self, operation: str, request_id: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            500, "STORAGE_ERROR", f"Storage operation failed: {operation}", request_id, details
        )


class GenerationError(MobiusError):
    """
    Image generation error (500 Internal Server Error).

    Used when image generation service fails.
    """

    def __init__(self, message: str, request_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(500, "GENERATION_FAILED", message, request_id, details)


class AuditError(MobiusError):
    """
    Compliance audit error (500 Internal Server Error).

    Used when compliance audit service fails.
    """

    def __init__(self, message: str, request_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(500, "AUDIT_FAILED", message, request_id, details)
