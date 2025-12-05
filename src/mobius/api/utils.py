"""
API utility functions.

Provides request ID generation and context management for distributed tracing.
"""

import uuid
from contextvars import ContextVar
from mobius.constants import REQUEST_ID_PREFIX

# Context variable for request tracking across async calls
_request_id: ContextVar[str] = ContextVar("request_id", default="")


def generate_request_id() -> str:
    """
    Generate unique request ID for tracing.

    Returns:
        str: Request ID in format "req_<12-char-hex>"
    """
    return f"{REQUEST_ID_PREFIX}{uuid.uuid4().hex[:12]}"


def get_request_id() -> str:
    """
    Get current request ID from context.

    Returns:
        str: Current request ID or empty string if not set
    """
    return _request_id.get()


def set_request_id(request_id: str) -> None:
    """
    Set request ID in context for current request.

    Args:
        request_id: Request ID to set in context
    """
    _request_id.set(request_id)
