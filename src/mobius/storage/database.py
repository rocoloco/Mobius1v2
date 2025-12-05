"""
Database client with connection pooling.

Provides Supabase client configured for serverless deployments.
"""

from supabase import create_client, Client
from mobius.config import settings
import structlog

logger = structlog.get_logger()

_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Get Supabase client configured for serverless.

    IMPORTANT: Use the pooler URL (port 6543), not direct connection (port 5432).
    Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

    This is critical for Modal's serverless architecture where many function instances
    may run concurrently. Direct connections will exhaust connection limits under load.

    The config.py Settings class validates the URL and warns if pooler is not used.

    Returns:
        Client: Configured Supabase client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not configured
    """
    global _client

    if _client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be configured. "
                "Set them in environment variables or .env file."
            )

        _client = create_client(settings.supabase_url, settings.supabase_key)

        # Log connection info (without exposing credentials)
        pooler_enabled = ":6543" in settings.supabase_url or "pooler" in settings.supabase_url
        logger.info(
            "supabase_client_initialized",
            pooler_enabled=pooler_enabled,
            url_contains_pooler="pooler" in settings.supabase_url,
        )

        if not pooler_enabled:
            logger.warning(
                "supabase_direct_connection_detected",
                message="Using direct connection instead of pooler. "
                "This may cause connection exhaustion under load. "
                "Consider using the pooler URL (port 6543).",
            )

    return _client


def reset_client() -> None:
    """
    Reset the global client instance.

    Useful for testing or when configuration changes.
    """
    global _client
    _client = None
