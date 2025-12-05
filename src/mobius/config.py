"""
Centralized configuration management using Pydantic Settings.

Loads configuration from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import warnings
import os


class Settings(BaseSettings):
    """Application settings with validation."""

    # Modal Secrets / External API Keys
    fal_api_key: str = ""
    gemini_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""

    # Configuration
    max_generation_attempts: int = 3
    compliance_threshold: float = 0.80
    template_threshold: float = 0.95
    job_expiry_hours: int = 24
    webhook_retry_max: int = 5

    # Storage buckets
    brands_bucket: str = "brands"
    assets_bucket: str = "assets"

    @field_validator("supabase_url")
    @classmethod
    def validate_pooler_url(cls, v: str) -> str:
        """
        Warn if not using pooler URL for serverless compatibility.

        Supabase connection pooling is CRITICAL for Modal serverless deployments.
        Without it, you will exhaust connection limits under load.
        """
        if v and "pooler.supabase.com" not in v and ":6543" not in v:
            warnings.warn(
                "Consider using Supabase pooler URL (port 6543) for serverless. "
                "Direct connections may exhaust connection limits under load. "
                "Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region]."
                "pooler.supabase.com:6543/postgres"
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow environment variables to override .env file
    )


# Global settings instance
settings = Settings()
