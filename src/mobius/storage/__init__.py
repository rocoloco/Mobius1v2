"""
Storage layer for Mobius.

This package contains:
- database.py: Supabase client setup with connection pooling
- brands.py: Brand CRUD operations
- assets.py: Asset CRUD operations
- templates.py: Template CRUD operations
- jobs.py: Job tracking operations
- feedback.py: Feedback storage operations
- files.py: Supabase Storage operations
"""

from .database import get_supabase_client

__all__ = ["get_supabase_client"]
