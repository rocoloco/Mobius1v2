"""
API dependencies for dependency injection.

Provides authentication and authorization dependencies.
Phase 2: Mock implementation for development
Phase 3: Will be replaced with real JWT authentication
"""

from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """
    User model for dependency injection.

    This model is used throughout the API to represent the authenticated user.
    """

    user_id: str
    organization_id: str
    email: Optional[str] = None


async def get_current_user(x_user_id: Optional[str] = None) -> User:
    """
    Mock authentication dependency for Phase 2.

    In Phase 2: Returns user from x-user-id header or test user.
    In Phase 3: Will validate JWT token and return authenticated user.

    This pattern allows all route handlers to use Depends(get_current_user)
    without code changes when real auth is added in Phase 3.

    Args:
        x_user_id: Optional user ID from x-user-id header

    Returns:
        User: User object with user_id and organization_id

    Example Phase 3 implementation:
        async def get_current_user(authorization: str = Header(...)) -> User:
            token = authorization.replace("Bearer ", "")
            payload = verify_jwt(token)
            return User(**payload)
    """
    if x_user_id:
        return User(user_id=x_user_id, organization_id=f"org-{x_user_id[:8]}")

    # Default test user for development
    return User(user_id="test-user-123", organization_id="test-org-456", email="test@example.com")
