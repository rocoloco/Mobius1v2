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

from .database import get_supabase_client, reset_client
from .brands import BrandStorage
from .assets import AssetStorage
from .templates import TemplateStorage
from .jobs import JobStorage
from .feedback import FeedbackStorage, Feedback
from .files import FileStorage

__all__ = [
    "get_supabase_client",
    "reset_client",
    "BrandStorage",
    "AssetStorage",
    "TemplateStorage",
    "JobStorage",
    "FeedbackStorage",
    "Feedback",
    "FileStorage",
]
