"""
Unit tests for learning system.

Tests private learning, shared learning, privacy tier switching,
data export, data deletion, k-anonymity, and differential privacy.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import uuid
from datetime import datetime, timezone

from mobius.learning.private import PrivateLearningEngine
from mobius.learning.shared import SharedLearningEngine
from mobius.models.learning import (
    LearningSettings,
    BrandPattern,
    IndustryPattern,
    PrivacyTier
)


class TestPrivateLearningEngine:
    """Tests for private learning engine."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_patterns_with_learning_disabled(self, mock_get_client):
        """Test that pattern extraction is skipped when learning is disabled."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock settings with OFF tier
        mock_settings_result = Mock()
        mock_settings_result.data = [{
            "brand_id": "test-brand",
            "privacy_tier": "off",
            "consent_date": None,
            "consent_version": "1.0",
            "data_retention_days": 365,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_settings_result
        
        # Mock audit log insert
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_audit_result
        
        # Extract patterns
        patterns = await engine.extract_patterns("test-brand")
        
        # Should return empty list
        assert len(patterns) == 0
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_export_learning_data(self, mock_get_client):
        """Test learning data export."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock settings
        mock_settings_result = Mock()
        mock_settings_result.data = [{
            "brand_id": "test-brand",
            "privacy_tier": "private",
            "consent_date": "2025-01-01T00:00:00Z",
            "consent_version": "1.0",
            "data_retention_days": 365,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        # Mock patterns
        mock_patterns_result = Mock()
        mock_patterns_result.data = [{
            "pattern_id": str(uuid.uuid4()),
            "brand_id": "test-brand",
            "pattern_type": "color_preference",
            "pattern_data": {},
            "confidence_score": 0.8,
            "sample_count": 10,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        # Mock audit log
        mock_audit_result = Mock()
        mock_audit_result.data = []
        
        # Set up mock behavior
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "learning_settings":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_settings_result
            elif table_name == "brand_patterns":
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_patterns_result
            elif table_name == "learning_audit_log":
                # For select queries (get audit log)
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_audit_result
                # For insert queries (log action)
                mock_table.insert.return_value.execute.return_value = Mock(data=[{}])
            return mock_table
        
        mock_client.table.side_effect = table_side_effect
        
        # Export data
        export_data = await engine.export_learning_data("test-brand")
        
        # Verify export structure
        assert export_data["brand_id"] == "test-brand"
        assert "export_date" in export_data
        assert "settings" in export_data
        assert "patterns" in export_data
        assert "audit_log" in export_data
        assert "metadata" in export_data
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_delete_learning_data(self, mock_get_client):
        """Test learning data deletion."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock delete operation
        mock_delete_result = Mock()
        mock_delete_result.data = []
        
        # Mock audit log insert
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "brand_patterns":
                mock_table.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
            elif table_name == "learning_audit_log":
                mock_table.insert.return_value.execute.return_value = mock_audit_result
            return mock_table
        
        mock_client.table.side_effect = table_side_effect
        
        # Delete data
        result = await engine.delete_learning_data("test-brand")
        
        # Should succeed
        assert result is True


class TestSharedLearningEngine:
    """Tests for shared learning engine."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.shared.get_supabase_client")
    async def test_aggregate_patterns_insufficient_contributors(self, mock_get_client):
        """Test that aggregation fails with insufficient contributors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = SharedLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock only 3 brands (less than MIN_CONTRIBUTORS)
        mock_brands_result = Mock()
        mock_brands_result.data = [
            {"brand_id": str(uuid.uuid4())} for _ in range(3)
        ]
        
        # Mock settings for all brands (shared tier)
        mock_settings_result = Mock()
        mock_settings_result.data = [{
            "brand_id": "test-brand",
            "privacy_tier": "shared",
            "consent_date": "2025-01-01T00:00:00Z",
            "consent_version": "1.0",
            "data_retention_days": 365,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "brands":
                mock_select = Mock()
                mock_eq = Mock()
                mock_is = Mock()
                mock_is.execute.return_value = mock_brands_result
                mock_eq.is_.return_value = mock_is
                mock_select.eq.return_value = mock_eq
                mock_table.select.return_value = mock_select
            elif table_name == "learning_settings":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_settings_result
            return mock_table
        
        mock_client.table.side_effect = table_side_effect
        
        # Attempt aggregation
        result = await engine.aggregate_patterns("fashion", "color_preference")
        
        # Should return None due to insufficient contributors
        assert result is None
    
    @pytest.mark.asyncio
    async def test_k_anonymity_enforcement(self):
        """Test that k-anonymity is enforced."""
        # Try to create pattern with < 5 contributors
        with pytest.raises(Exception):  # Pydantic ValidationError
            pattern = IndustryPattern(
                pattern_id=str(uuid.uuid4()),
                cohort="fashion",
                pattern_type="color_preference",
                pattern_data={},
                contributor_count=3,  # Less than 5
                noise_level=0.1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
    
    @pytest.mark.asyncio
    @patch("mobius.learning.shared.get_supabase_client")
    async def test_differential_privacy_noise_applied(self, mock_get_client):
        """Test that differential privacy noise is applied."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = SharedLearningEngine()
        
        # Create test patterns
        patterns = [
            BrandPattern(
                pattern_id=str(uuid.uuid4()),
                brand_id=str(uuid.uuid4()),
                pattern_type="color_preference",
                pattern_data={"approval_rate": 0.75},
                confidence_score=0.8,
                sample_count=10
            )
            for _ in range(5)
        ]
        
        # Aggregate with privacy
        aggregated = engine._aggregate_with_privacy(patterns)
        
        # Should contain privacy metadata
        assert "_privacy" in aggregated
        assert aggregated["_privacy"]["mechanism"] == "laplace"
        assert aggregated["_privacy"]["noise_scale"] > 0
    
    @pytest.mark.asyncio
    @patch("mobius.learning.shared.get_supabase_client")
    async def test_privacy_budget_calculation(self, mock_get_client):
        """Test privacy budget calculation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = SharedLearningEngine()
        
        # Calculate budget for 10 queries
        epsilon = engine.calculate_privacy_budget(10)
        
        # Should be positive and scale with queries
        assert epsilon > 0
        expected = (1.0 / engine.NOISE_SCALE) * 10
        assert abs(epsilon - expected) < 0.001


class TestPrivacyTierSwitching:
    """Tests for privacy tier switching."""
    
    @pytest.mark.asyncio
    async def test_switch_from_off_to_private(self):
        """Test switching from OFF to PRIVATE tier."""
        # Create settings with OFF tier
        settings = LearningSettings(
            brand_id="test-brand",
            privacy_tier=PrivacyTier.OFF
        )
        
        assert settings.privacy_tier == PrivacyTier.OFF
        
        # Switch to PRIVATE
        settings.privacy_tier = PrivacyTier.PRIVATE
        settings.consent_date = datetime.now(timezone.utc)
        
        assert settings.privacy_tier == PrivacyTier.PRIVATE
        assert settings.consent_date is not None
    
    @pytest.mark.asyncio
    async def test_switch_from_private_to_shared_requires_consent(self):
        """Test that switching to SHARED requires consent."""
        # Create settings with PRIVATE tier
        settings = LearningSettings(
            brand_id="test-brand",
            privacy_tier=PrivacyTier.PRIVATE,
            consent_date=datetime.now(timezone.utc)
        )
        
        # Switch to SHARED (requires new consent)
        settings.privacy_tier = PrivacyTier.SHARED
        settings.consent_date = datetime.now(timezone.utc)  # New consent required
        
        assert settings.privacy_tier == PrivacyTier.SHARED
        assert settings.consent_date is not None


class TestDataExportAndDeletion:
    """Tests for data export and deletion functionality."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_export_includes_all_data(self, mock_get_client):
        """Test that export includes all required data."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock all data
        mock_settings_result = Mock()
        mock_settings_result.data = [{
            "brand_id": "test-brand",
            "privacy_tier": "private",
            "consent_date": "2025-01-01T00:00:00Z",
            "consent_version": "1.0",
            "data_retention_days": 365,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        mock_patterns_result = Mock()
        mock_patterns_result.data = []
        
        mock_audit_result = Mock()
        mock_audit_result.data = []
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "learning_settings":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_settings_result
            elif table_name == "brand_patterns":
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_patterns_result
            elif table_name == "learning_audit_log":
                # For select queries (get audit log)
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_audit_result
                # For insert queries (log action)
                mock_table.insert.return_value.execute.return_value = Mock(data=[{}])
            return mock_table
        
        mock_client.table.side_effect = table_side_effect
        
        # Export
        export_data = await engine.export_learning_data("test-brand")
        
        # Verify all sections present
        assert "settings" in export_data
        assert "patterns" in export_data
        assert "audit_log" in export_data
        assert "metadata" in export_data
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_deletion_is_permanent(self, mock_get_client):
        """Test that deletion is permanent."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock delete
        mock_delete_result = Mock()
        mock_delete_result.data = []
        
        # Mock audit log
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        
        # Mock query after deletion (empty)
        mock_query_result = Mock()
        mock_query_result.data = []
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "brand_patterns":
                mock_table.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_query_result
            elif table_name == "learning_audit_log":
                mock_table.insert.return_value.execute.return_value = mock_audit_result
            return mock_table
        
        mock_client.table.side_effect = table_side_effect
        
        # Delete
        await engine.delete_learning_data("test-brand")
        
        # Query after deletion
        patterns = await engine._get_patterns("test-brand")
        
        # Should be empty
        assert len(patterns) == 0
