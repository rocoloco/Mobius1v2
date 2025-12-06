"""
Comprehensive unit tests for enhanced private learning engine.

Tests real statistical analysis, pattern decay, learning effectiveness,
consent verification, and data minimization.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import uuid
from datetime import datetime, timedelta, timezone

from mobius.learning.private import PrivateLearningEngine
from mobius.models.learning import (
    LearningSettings,
    BrandPattern,
    PrivacyTier
)


class TestColorExtraction:
    """Tests for color preference extraction with real statistical analysis."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_color_extraction_calculates_success_rates(self, mock_get_client):
        """Test that color extraction produces correct success rates."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#FF5733", "#3498DB"]
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#FF5733"]
                    }
                }
            },
            {
                "action": "reject",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#3498DB"]
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#FF5733", "#2ECC71"]
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#2ECC71"]
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#2ECC71"]
                    }
                }
            }
        ]
        
        pattern = await engine._extract_color_preferences("test-brand", feedback_data)
        
        assert pattern is not None
        assert "#FF5733" in pattern.pattern_data["color_preferences"]
        # #FF5733: 3 approved, 0 rejected = 100% success rate
        assert pattern.pattern_data["color_preferences"]["#FF5733"]["success_rate"] == 1.0
        assert pattern.pattern_data["color_preferences"]["#FF5733"]["approved_count"] == 3
        
        # #2ECC71: 3 approved, 0 rejected = 100% success rate
        assert "#2ECC71" in pattern.pattern_data["color_preferences"]
        assert pattern.pattern_data["color_preferences"]["#2ECC71"]["success_rate"] == 1.0
        
        # #3498DB: 1 approved, 1 rejected = 50% success rate (should be excluded as <60%)
        assert "#3498DB" not in pattern.pattern_data["color_preferences"]
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_color_extraction_requires_minimum_samples(self, mock_get_client):
        """Test that color extraction requires minimum 5 approved samples."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#FF5733"]
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "colors_used": ["#FF5733"]
                    }
                }
            }
        ]
        
        pattern = await engine._extract_color_preferences("test-brand", feedback_data)
        
        # Should return None due to insufficient samples
        assert pattern is None
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_color_extraction_filters_low_occurrence_colors(self, mock_get_client):
        """Test that colors with <3 occurrences are filtered out."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#FF5733"]}}},
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#FF5733"]}}},
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#FF5733"]}}},
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#3498DB"]}}},  # Only 2 occurrences
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#3498DB"]}}},
            {"action": "approve", "assets": {"generation_params": {"colors_used": ["#2ECC71"]}}},  # Only 1 occurrence
        ]
        
        pattern = await engine._extract_color_preferences("test-brand", feedback_data)
        
        assert pattern is not None
        # #FF5733 should be included (3 occurrences)
        assert "#FF5733" in pattern.pattern_data["color_preferences"]
        # #3498DB should be excluded (only 2 occurrences)
        assert "#3498DB" not in pattern.pattern_data["color_preferences"]
        # #2ECC71 should be excluded (only 1 occurrence)
        assert "#2ECC71" not in pattern.pattern_data["color_preferences"]


class TestPromptOptimization:
    """Tests for prompt optimization application."""
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_prompt_optimization_adds_style_descriptors(self, mock_get_client):
        """Test that optimization correctly adds learned style descriptors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a logo for tech startup"
        optimization_data = {
            "optimizations": [
                {
                    "type": "add_style_descriptor",
                    "descriptor": "modern",
                    "confidence": 0.82
                }
            ]
        }
        
        optimized = engine._apply_optimization(prompt, optimization_data)
        
        assert "modern" in optimized.lower()
        assert "tech startup" in optimized  # Original intent preserved
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_prompt_optimization_removes_problematic_terms(self, mock_get_client):
        """Test that optimization removes problematic terms."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a vintage logo for tech startup"
        optimization_data = {
            "optimizations": [
                {
                    "type": "remove_problematic_term",
                    "term": "vintage",
                    "confidence": 0.75
                }
            ]
        }
        
        optimized = engine._apply_optimization(prompt, optimization_data)
        
        assert "vintage" not in optimized.lower()
        assert "tech startup" in optimized  # Original intent preserved
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_prompt_optimization_skips_low_confidence(self, mock_get_client):
        """Test that low confidence optimizations are skipped."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a logo"
        optimization_data = {
            "optimizations": [
                {
                    "type": "add_style_descriptor",
                    "descriptor": "modern",
                    "confidence": 0.3  # Below 0.5 threshold
                }
            ]
        }
        
        optimized = engine._apply_optimization(prompt, optimization_data)
        
        # Should not add descriptor due to low confidence
        assert optimized == prompt
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_prompt_optimization_adds_color_suggestions(self, mock_get_client):
        """Test that optimization adds color suggestions when appropriate."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a logo for tech startup"
        optimization_data = {
            "optimizations": [
                {
                    "type": "color_suggestion",
                    "color": "#3498DB",
                    "confidence": 0.70
                }
            ]
        }
        
        optimized = engine._apply_optimization(prompt, optimization_data)
        
        assert "#3498DB" in optimized
        assert "tech startup" in optimized


class TestPatternDecay:
    """Tests for time-based pattern decay."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_pattern_decay_reduces_confidence(self, mock_get_client):
        """Test that old patterns lose confidence over time."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Create patterns with different ages
        old_pattern = {
            "pattern_id": "pattern-1",
            "brand_id": "test-brand",
            "confidence_score": 1.0,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
        }
        
        recent_pattern = {
            "pattern_id": "pattern-2",
            "brand_id": "test-brand",
            "confidence_score": 1.0,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        }
        
        # Mock select all patterns
        mock_select_result = Mock()
        mock_select_result.data = [old_pattern, recent_pattern]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_select_result
        
        # Mock update
        mock_update_result = Mock()
        mock_update_result.data = [{}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Apply decay
        summary = await engine.apply_pattern_decay()
        
        # Should process 2 patterns
        assert summary["patterns_processed"] == 2
        # Should update 1 pattern (old one, recent one is in grace period)
        assert summary["patterns_updated"] == 1
        # After 120 days with 90-day half-life: 0.5^(120/90) ≈ 0.4
        assert summary["oldest_pattern_age_days"] == 120
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_pattern_decay_deletes_very_low_confidence(self, mock_get_client):
        """Test that patterns with very low confidence are deleted."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Create pattern with very low confidence after decay
        very_old_pattern = {
            "pattern_id": "pattern-1",
            "brand_id": "test-brand",
            "confidence_score": 0.2,  # Will decay to <0.1
            "created_at": (datetime.now(timezone.utc) - timedelta(days=270)).isoformat()
        }
        
        mock_select_result = Mock()
        mock_select_result.data = [very_old_pattern]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_select_result
        
        mock_update_result = Mock()
        mock_update_result.data = [{}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        mock_delete_result = Mock()
        mock_delete_result.data = [{}]
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
        
        summary = await engine.apply_pattern_decay()
        
        # Should mark pattern as below threshold
        assert summary["patterns_below_threshold"] == 1


class TestConsentVerification:
    """Tests for consent verification."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_patterns_blocked_without_consent(self, mock_get_client):
        """Test that pattern extraction respects consent settings."""
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
        
        patterns = await engine.extract_patterns("test-brand")
        
        # Should return empty list due to no consent
        assert len(patterns) == 0
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_verify_consent_checks_tier_hierarchy(self, mock_get_client):
        """Test that consent verification respects tier hierarchy."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock settings with PRIVATE tier
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
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_settings_result
        
        # Should allow PRIVATE operations
        assert await engine._verify_consent("test-brand", PrivacyTier.PRIVATE) == True
        
        # Should not allow SHARED operations (requires higher tier)
        assert await engine._verify_consent("test-brand", PrivacyTier.SHARED) == False


class TestLearningEffectiveness:
    """Tests for learning effectiveness calculation."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_learning_effectiveness_calculates_improvement(self, mock_get_client):
        """Test that effectiveness metrics show improvement."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        brand_id = "test-brand"
        learning_active_at = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        
        # Mock brand with learning activated
        mock_brand_result = Mock()
        mock_brand_result.data = [{
            "brand_id": brand_id,
            "learning_active_at": learning_active_at
        }]
        
        # Mock assets before learning (lower scores)
        mock_before_result = Mock()
        mock_before_result.data = [
            {"compliance_score": 75.0} for _ in range(20)
        ]
        
        # Mock assets after learning (higher scores)
        mock_after_result = Mock()
        mock_after_result.data = [
            {"compliance_score": 85.0} for _ in range(35)
        ]
        
        # Setup mock call sequence
        def mock_table_chain(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.lt.return_value = mock_chain
            mock_chain.gte.return_value = mock_chain
            
            # First call: brand query
            if not hasattr(mock_table_chain, 'call_count'):
                mock_table_chain.call_count = 0
            
            mock_table_chain.call_count += 1
            
            if mock_table_chain.call_count == 1:
                mock_chain.execute.return_value = mock_brand_result
            elif mock_table_chain.call_count == 2:
                mock_chain.execute.return_value = mock_before_result
            else:
                mock_chain.execute.return_value = mock_after_result
            
            return mock_chain
        
        mock_client.table.side_effect = mock_table_chain
        
        effectiveness = await engine.get_learning_effectiveness(brand_id)
        
        assert effectiveness["learning_active"] == True
        assert effectiveness["avg_compliance_before_learning"] == 75.0
        assert effectiveness["avg_compliance_after_learning"] == 85.0
        assert effectiveness["improvement_percentage"] > 10.0
        assert effectiveness["statistically_significant"] == True
        assert effectiveness["before_sample_count"] == 20
        assert effectiveness["after_sample_count"] == 35
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_learning_effectiveness_handles_no_learning(self, mock_get_client):
        """Test that effectiveness handles brands without learning activated."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock brand without learning activated
        mock_brand_result = Mock()
        mock_brand_result.data = [{
            "brand_id": "test-brand",
            "learning_active_at": None
        }]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_brand_result
        
        effectiveness = await engine.get_learning_effectiveness("test-brand")
        
        assert effectiveness["learning_active"] == False
        assert "message" in effectiveness


class TestDataMinimization:
    """Tests for GDPR data minimization."""
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_minimize_pattern_data_removes_forbidden_fields(self, mock_get_client):
        """Test that data minimization removes PII and forbidden fields."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        pattern_data = {
            "color_preferences": {"#FF5733": {"success_rate": 0.85}},
            "asset_id": "asset-123",  # FORBIDDEN
            "raw_prompt": "Create a logo",  # FORBIDDEN
            "user_id": "user-456",  # FORBIDDEN
            "analysis_date": "2025-12-05T14:30:45.123456Z"  # TOO PRECISE
        }
        
        minimized = engine._minimize_pattern_data(pattern_data)
        
        # Should keep allowed fields
        assert "color_preferences" in minimized
        
        # Should remove forbidden fields
        assert "asset_id" not in minimized
        assert "raw_prompt" not in minimized
        assert "user_id" not in minimized
        
        # Should truncate timestamp precision
        assert minimized["analysis_date"] == "2025-12-05T14:30:00Z"
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_minimize_pattern_data_rounds_floats(self, mock_get_client):
        """Test that floats are rounded to 2 decimal places."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        pattern_data = {
            "confidence": 0.8567891234,
            "success_rate": 0.7234567
        }
        
        minimized = engine._minimize_pattern_data(pattern_data)
        
        assert minimized["confidence"] == 0.86
        assert minimized["success_rate"] == 0.72
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_minimize_pattern_data_handles_nested_structures(self, mock_get_client):
        """Test that minimization works recursively on nested data."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        pattern_data = {
            "colors": {
                "#FF5733": {
                    "success_rate": 0.8567,
                    "asset_id": "asset-123"  # FORBIDDEN
                }
            }
        }
        
        minimized = engine._minimize_pattern_data(pattern_data)
        
        # Should round nested float
        assert minimized["colors"]["#FF5733"]["success_rate"] == 0.86
        
        # Should remove nested forbidden field
        assert "asset_id" not in minimized["colors"]["#FF5733"]


class TestStatisticalSignificance:
    """Tests for statistical significance calculation."""
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_calculate_statistical_significance_requires_minimum_samples(self, mock_get_client):
        """Test that significance requires minimum 5 samples."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        # Less than 5 samples
        significance = engine._calculate_statistical_significance(2, 1, 3)
        assert significance == 0.0
        
        # Exactly 5 samples
        significance = engine._calculate_statistical_significance(4, 1, 5)
        assert significance > 0.0
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_calculate_statistical_significance_considers_sample_size(self, mock_get_client):
        """Test that larger samples increase confidence."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        # Small sample
        small_sig = engine._calculate_statistical_significance(8, 2, 10)
        
        # Large sample with same rate
        large_sig = engine._calculate_statistical_significance(24, 6, 30)
        
        # Larger sample should have higher confidence
        assert large_sig > small_sig
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_calculate_statistical_significance_considers_rate_clarity(self, mock_get_client):
        """Test that clearer patterns (further from 50%) have higher confidence."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        # Clear pattern (90% success)
        clear_sig = engine._calculate_statistical_significance(18, 2, 20)
        
        # Unclear pattern (55% success)
        unclear_sig = engine._calculate_statistical_significance(11, 9, 20)
        
        # Clearer pattern should have higher confidence
        assert clear_sig > unclear_sig


class TestPromptTokenization:
    """Tests for prompt tokenization."""
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_tokenize_prompt_removes_punctuation(self, mock_get_client):
        """Test that tokenization removes punctuation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a modern, minimalist logo!"
        tokens = engine._tokenize_prompt(prompt)
        
        assert "modern" in tokens
        assert "minimalist" in tokens
        assert "logo" in tokens
        # Punctuation should be removed
        assert "!" not in tokens
        assert "," not in tokens
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_tokenize_prompt_filters_stop_words(self, mock_get_client):
        """Test that common stop words are filtered out."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create a logo for the tech startup"
        tokens = engine._tokenize_prompt(prompt)
        
        # Content words should be kept
        assert "create" in tokens
        assert "logo" in tokens
        assert "tech" in tokens
        assert "startup" in tokens
        
        # Stop words should be filtered
        assert "a" not in tokens
        assert "for" not in tokens
        assert "the" not in tokens
    
    @patch("mobius.learning.private.get_supabase_client")
    def test_tokenize_prompt_converts_to_lowercase(self, mock_get_client):
        """Test that all tokens are lowercase."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        prompt = "Create MODERN Logo"
        tokens = engine._tokenize_prompt(prompt)
        
        assert "modern" in tokens
        assert "MODERN" not in tokens
        assert "logo" in tokens
        assert "Logo" not in tokens



class TestOptimizePrompt:
    """Tests for prompt optimization with learned patterns."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_optimize_prompt_applies_patterns(self, mock_get_client):
        """Test that optimize_prompt applies learned patterns."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock settings with PRIVATE tier
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
        
        # Mock patterns with prompt optimization
        mock_patterns_result = Mock()
        mock_patterns_result.data = [{
            "pattern_id": "pattern-1",
            "brand_id": "test-brand",
            "pattern_type": "prompt_optimization",
            "pattern_data": {
                "optimizations": [
                    {
                        "type": "add_style_descriptor",
                        "descriptor": "modern",
                        "confidence": 0.85
                    }
                ]
            },
            "confidence_score": 0.85,
            "sample_count": 50,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        
        # Mock audit log insert
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        
        # Setup mock call sequence
        def mock_table_chain(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.insert.return_value = mock_chain
            
            if not hasattr(mock_table_chain, 'call_count'):
                mock_table_chain.call_count = 0
            
            mock_table_chain.call_count += 1
            
            if mock_table_chain.call_count == 1:
                # First call: get settings
                mock_chain.execute.return_value = mock_settings_result
            elif mock_table_chain.call_count == 2:
                # Second call: get patterns
                mock_chain.execute.return_value = mock_patterns_result
            else:
                # Third call: audit log
                mock_chain.execute.return_value = mock_audit_result
            
            return mock_chain
        
        mock_client.table.side_effect = mock_table_chain
        
        base_prompt = "Create a logo for tech startup"
        optimized = await engine.optimize_prompt("test-brand", base_prompt)
        
        # Should add "modern" descriptor
        assert "modern" in optimized.lower()
        assert "tech startup" in optimized
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_optimize_prompt_skips_when_learning_disabled(self, mock_get_client):
        """Test that optimization is skipped when learning is OFF."""
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
        
        base_prompt = "Create a logo"
        optimized = await engine.optimize_prompt("test-brand", base_prompt)
        
        # Should return unchanged prompt
        assert optimized == base_prompt
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_optimize_prompt_handles_no_patterns(self, mock_get_client):
        """Test that optimization handles brands with no learned patterns."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock settings with PRIVATE tier
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
        
        # Mock empty patterns
        mock_patterns_result = Mock()
        mock_patterns_result.data = []
        
        def mock_table_chain(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            
            if not hasattr(mock_table_chain, 'call_count'):
                mock_table_chain.call_count = 0
            
            mock_table_chain.call_count += 1
            
            if mock_table_chain.call_count == 1:
                mock_chain.execute.return_value = mock_settings_result
            else:
                mock_chain.execute.return_value = mock_patterns_result
            
            return mock_chain
        
        mock_client.table.side_effect = mock_table_chain
        
        base_prompt = "Create a logo"
        optimized = await engine.optimize_prompt("test-brand", base_prompt)
        
        # Should return unchanged prompt
        assert optimized == base_prompt


class TestDeleteLearningData:
    """Tests for GDPR right to deletion."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_delete_learning_data_removes_patterns(self, mock_get_client):
        """Test that delete_learning_data removes all brand patterns."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock audit log insert
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        
        # Mock pattern deletion
        mock_delete_result = Mock()
        mock_delete_result.data = [{}]
        
        def mock_table_chain(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.insert.return_value = mock_chain
            mock_chain.delete.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            
            if not hasattr(mock_table_chain, 'call_count'):
                mock_table_chain.call_count = 0
            
            mock_table_chain.call_count += 1
            
            if mock_table_chain.call_count == 1:
                # First call: audit log
                mock_chain.execute.return_value = mock_audit_result
            else:
                # Second call: delete patterns
                mock_chain.execute.return_value = mock_delete_result
            
            return mock_chain
        
        mock_client.table.side_effect = mock_table_chain
        
        result = await engine.delete_learning_data("test-brand")
        
        assert result == True
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_delete_learning_data_logs_action(self, mock_get_client):
        """Test that deletion is logged to audit log."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        mock_client = Mock()
        engine.client = mock_client
        
        # Mock audit log insert
        mock_audit_result = Mock()
        mock_audit_result.data = [{}]
        
        # Mock pattern deletion
        mock_delete_result = Mock()
        mock_delete_result.data = [{}]
        
        call_counter = {'count': 0}
        
        def mock_table_chain(*args, **kwargs):
            mock_chain = Mock()
            mock_chain.insert.return_value = mock_chain
            mock_chain.delete.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            
            call_counter['count'] += 1
            mock_chain.execute.return_value = mock_audit_result if call_counter['count'] == 1 else mock_delete_result
            
            return mock_chain
        
        mock_client.table.side_effect = mock_table_chain
        
        await engine.delete_learning_data("test-brand")
        
        # Verify audit log was called
        assert mock_client.table.call_count >= 1


class TestExtractStylePreferences:
    """Tests for style preference extraction."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_style_preferences_analyzes_params(self, mock_get_client):
        """Test that style extraction analyzes generation parameters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro",
                        "style": "modern",
                        "aspect_ratio": "16:9"
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro",
                        "style": "modern",
                        "aspect_ratio": "16:9"
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro",
                        "style": "minimalist",
                        "aspect_ratio": "1:1"
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-dev",
                        "style": "modern",
                        "aspect_ratio": "16:9"
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro",
                        "style": "modern",
                        "aspect_ratio": "16:9"
                    }
                }
            }
        ]
        
        pattern = await engine._extract_style_preferences("test-brand", feedback_data)
        
        assert pattern is not None
        assert pattern.pattern_type == "style_preference"
        assert "style_preferences" in pattern.pattern_data
        
        # flux-pro should be most common model
        assert "model" in pattern.pattern_data["style_preferences"]
        assert "flux-pro" in pattern.pattern_data["style_preferences"]["model"]
        
        # modern should be most common style
        assert "style" in pattern.pattern_data["style_preferences"]
        assert "modern" in pattern.pattern_data["style_preferences"]["style"]
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_style_preferences_requires_minimum_samples(self, mock_get_client):
        """Test that style extraction requires minimum 5 approved samples."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro"
                    }
                }
            },
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "model": "flux-pro"
                    }
                }
            }
        ]
        
        pattern = await engine._extract_style_preferences("test-brand", feedback_data)
        
        # Should return None due to insufficient samples
        assert pattern is None


class TestExtractPromptPatterns:
    """Tests for prompt pattern extraction."""
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_prompt_patterns_identifies_successful_terms(self, mock_get_client):
        """Test that prompt extraction identifies successful terms."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = []
        
        # Add 15 approved with "modern"
        for _ in range(15):
            feedback_data.append({
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "prompt": "Create a modern logo for tech startup"
                    }
                }
            })
        
        # Add 2 rejected with "modern"
        for _ in range(2):
            feedback_data.append({
                "action": "reject",
                "assets": {
                    "generation_params": {
                        "prompt": "Create a modern logo for tech startup"
                    }
                }
            })
        
        # Add 2 approved with "vintage"
        for _ in range(2):
            feedback_data.append({
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "prompt": "Create a vintage logo"
                    }
                }
            })
        
        # Add 8 rejected with "vintage"
        for _ in range(8):
            feedback_data.append({
                "action": "reject",
                "assets": {
                    "generation_params": {
                        "prompt": "Create a vintage logo"
                    }
                }
            })
        
        pattern = await engine._extract_prompt_patterns("test-brand", feedback_data)
        
        assert pattern is not None
        assert pattern.pattern_type == "prompt_optimization"
        assert "optimizations" in pattern.pattern_data
        
        # Should identify "modern" as successful (15/17 = 88%)
        modern_opts = [opt for opt in pattern.pattern_data["optimizations"] 
                      if opt.get("descriptor") == "modern" or opt.get("element") == "modern"]
        assert len(modern_opts) > 0
        
        # Should identify "vintage" as problematic (2/10 = 20%)
        vintage_opts = [opt for opt in pattern.pattern_data["optimizations"] 
                       if opt.get("term") == "vintage"]
        assert len(vintage_opts) > 0
    
    @pytest.mark.asyncio
    @patch("mobius.learning.private.get_supabase_client")
    async def test_extract_prompt_patterns_requires_minimum_samples(self, mock_get_client):
        """Test that prompt extraction requires minimum 10 approved samples."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        engine = PrivateLearningEngine()
        
        feedback_data = [
            {
                "action": "approve",
                "assets": {
                    "generation_params": {
                        "prompt": "Create a logo"
                    }
                }
            } for _ in range(5)
        ]
        
        pattern = await engine._extract_prompt_patterns("test-brand", feedback_data)
        
        # Should return None due to insufficient samples
        assert pattern is None
