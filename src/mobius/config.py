"""
Centralized configuration management using Pydantic Settings.

Loads configuration from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationError
from typing import Optional
import warnings
import os


class Settings(BaseSettings):
    """
    Application settings with validation.
    
    Uses Gemini 3 dual-model architecture:
    - Reasoning Model (gemini-3-pro-preview): PDF parsing, compliance auditing
    - Vision Model (gemini-3-pro-image-preview): Image generation
    """

    # Modal Secrets / External API Keys
    gemini_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""

    # Gemini Model Configuration
    reasoning_model: str = "gemini-3-pro-preview"
    vision_model: str = "gemini-3-pro-image-preview"

    # Configuration
    max_generation_attempts: int = 3
    compliance_threshold: float = 0.80
    template_threshold: float = 0.95
    job_expiry_hours: int = 24
    webhook_retry_max: int = 5

    # Storage buckets
    brands_bucket: str = "brands"
    assets_bucket: str = "assets"

    # Neo4j Graph Database
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"
    graph_sync_enabled: bool = True
    
    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini_api_key(cls, v: str) -> str:
        """
        Validate that gemini_api_key is present and non-empty.
        
        The Gemini API key is required for all AI operations in the dual-model architecture.
        """
        if not v or v.strip() == "":
            raise ValueError(
                "gemini_api_key is required. Set GEMINI_API_KEY environment variable."
            )
        return v

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
        extra="ignore",  # Ignore extra fields in .env file
    )


# Global settings instance
settings = Settings()
