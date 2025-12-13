"""
Error handling utilities.

Provides structured error responses with consistent formatting.
"""

from functools import wraps
from typing import Optional, Any, Dict, Callable, TypeVar, Awaitable
from pydantic import BaseModel
import structlog

# Type variable for the return type of the wrapped function
T = TypeVar('T')


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


def handle_api_errors(
    logger: Any = None,
    error_message: str = "An unexpected error occurred",
):
    """
    Decorator to standardize error handling for FastAPI endpoint handlers.

    Eliminates duplicate try-except blocks across all endpoints by providing
    consistent error response formatting for both MobiusError and unexpected exceptions.

    Args:
        logger: Optional logger instance. If not provided, creates one.
        error_message: Custom message for unexpected errors.

    Usage:
        @web_app.get("/v1/brands")
        @handle_api_errors(logger=logger)
        async def list_brands():
            # No try-except needed - decorator handles it
            result = await list_brands_handler()
            return result

    Returns:
        - On success: The handler's return value
        - On MobiusError: JSONResponse with structured error (status from error)
        - On Exception: JSONResponse with 500 Internal Server Error
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from fastapi.responses import JSONResponse

            # Use provided logger or create one
            log = logger if logger is not None else structlog.get_logger()

            try:
                return await func(*args, **kwargs)
            except MobiusError as e:
                log.error(
                    "endpoint_error",
                    endpoint=func.__name__,
                    error_code=e.error_response.error.code,
                    error=str(e),
                )
                return JSONResponse(
                    status_code=e.status_code,
                    content={"error": e.error_response.model_dump()}
                )
            except Exception as e:
                log.error(
                    "unexpected_error",
                    endpoint=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": error_message,
                            "details": {"error": str(e)},
                        }
                    }
                )
        return wrapper
    return decorator


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Factory function to create consistent error responses.

    Use this when you need to return an error response manually
    (e.g., in complex control flows where the decorator isn't suitable).

    Args:
        status_code: HTTP status code
        code: Error code for programmatic handling
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        JSONResponse with structured error format
    """
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        }
    )
