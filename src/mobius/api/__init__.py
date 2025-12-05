"""
API layer for Mobius.

This package contains:
- app.py: Modal app definition
- routes.py: Endpoint route handlers
- schemas.py: Pydantic request/response schemas
- errors.py: Error handling utilities
- utils.py: Request ID and helper functions
- dependencies.py: Auth dependencies (mock for Phase 2)
"""

from .errors import MobiusError, ValidationError, NotFoundError, StorageError
from .utils import generate_request_id, get_request_id, set_request_id

__all__ = [
    "MobiusError",
    "ValidationError",
    "NotFoundError",
    "StorageError",
    "generate_request_id",
    "get_request_id",
    "set_request_id",
]
