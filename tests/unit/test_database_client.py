"""
Tests for database client module.

Tests Supabase client initialization and connection pooling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mobius.storage.database import get_supabase_client


@pytest.mark.asyncio
@patch("mobius.storage.database.create_client")
@patch("mobius.storage.database.settings")
async def test_get_supabase_client_creates_client(mock_settings, mock_create_client):
    """Test that get_supabase_client creates a client."""
    mock_settings.supabase_url = "https://test.supabase.co"
    mock_settings.supabase_key = "test-key"
    
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    # Reset the global client
    import mobius.storage.database as db_module
    db_module._client = None
    
    client = get_supabase_client()
    
    assert client is not None
    mock_create_client.assert_called_once_with(
        "https://test.supabase.co",
        "test-key"
    )


@pytest.mark.asyncio
@patch("mobius.storage.database.create_client")
@patch("mobius.storage.database.settings")
async def test_get_supabase_client_reuses_client(mock_settings, mock_create_client):
    """Test that get_supabase_client reuses existing client."""
    mock_settings.supabase_url = "https://test.supabase.co"
    mock_settings.supabase_key = "test-key"
    
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    # Reset the global client
    import mobius.storage.database as db_module
    db_module._client = None
    
    client1 = get_supabase_client()
    client2 = get_supabase_client()
    
    assert client1 is client2
    # Should only be called once
    mock_create_client.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.database.create_client")
@patch("mobius.storage.database.settings")
@patch("mobius.storage.database.logger")
async def test_get_supabase_client_logs_pooler_enabled(
    mock_logger, mock_settings, mock_create_client
):
    """Test that get_supabase_client logs pooler status."""
    mock_settings.supabase_url = "https://test.pooler.supabase.com:6543"
    mock_settings.supabase_key = "test-key"
    
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    # Reset the global client
    import mobius.storage.database as db_module
    db_module._client = None
    
    client = get_supabase_client()
    
    # Verify logger was called with pooler_enabled=True
    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert "pooler_enabled" in call_args[1]
    assert call_args[1]["pooler_enabled"] is True


@pytest.mark.asyncio
@patch("mobius.storage.database.create_client")
@patch("mobius.storage.database.settings")
@patch("mobius.storage.database.logger")
async def test_get_supabase_client_logs_pooler_disabled(
    mock_logger, mock_settings, mock_create_client
):
    """Test that get_supabase_client logs when pooler is not used."""
    mock_settings.supabase_url = "https://test.supabase.co:5432"
    mock_settings.supabase_key = "test-key"
    
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    # Reset the global client
    import mobius.storage.database as db_module
    db_module._client = None
    
    client = get_supabase_client()
    
    # Verify logger was called with pooler_enabled=False
    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert "pooler_enabled" in call_args[1]
    assert call_args[1]["pooler_enabled"] is False
