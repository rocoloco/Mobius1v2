"""
Learning transparency dashboard implementation.

This module provides the data and logic for the learning transparency dashboard,
which shows users what patterns were learned, data sources, impact metrics,
and provides one-click disable/delete options.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import structlog

from mobius.models.learning import LearningSettings, BrandPattern, PrivacyTier
from mobius.storage.learning import LearningStorage
from mobius.storage.brands import BrandStorage
from mobius.learning.shared import SharedLearningEngine

logger = structlog.get_logger()


class LearningDashboard:
    """
    Learning transparency dashboard.
    
    Provides radical transparency about what the system has learned,
    where the data came from, and what impact it has had.
    """
    
    def __init__(self):
        self.learning_storage = LearningStorage()
        self.brand_storage = BrandStorage()
        self.shared_engine = SharedLearningEngine()
    
    async def get_dashboard_data(self, brand_id: str) -> Dict[str, Any]:
        """
        Get complete dashboard data for a brand.
        
        Args:
            brand_id: Brand to get dashboard for
            
        Returns:
            Dictionary containing all dashboard data
        """
        logger.info("generating_dashboard_data", brand_id=brand_id)
        
        # Get brand
        brand = await self.brand_storage.get_brand(brand_id)
        if not brand:
            raise ValueError(f"Brand {brand_id} not found")
        
        # Get settings
        settings = await self.learning_storage.get_settings(brand_id)
        if not settings:
            settings = LearningSettings(brand_id=brand_id, privacy_tier=PrivacyTier.PRIVATE)
        
        # Get patterns
        patterns = await self.learning_storage.get_brand_patterns(brand_id)
        
        # Get audit log
        audit_log = await self.learning_storage.get_audit_log(brand_id, limit=50)
        
        # Build dashboard sections
        dashboard = {
            "overview": await self._build_overview(brand, settings, patterns),
            "patterns_learned": await self._build_patterns_section(patterns),
            "data_sources": await self._build_data_sources_section(brand, settings),
            "impact_metrics": await self._build_impact_metrics(brand, patterns),
            "audit_log": await self._build_audit_log_section(audit_log),
            "actions": self._build_actions_section(settings)
        }
        
        return dashboard
    
    async def _build_overview(
        self,
        brand: Any,
        settings: LearningSettings,
        patterns: List[BrandPattern]
    ) -> Dict[str, Any]:
        """Build overview section."""
        return {
            "brand_name": brand.name,
            "privacy_tier": settings.privacy_tier.value,
            "privacy_tier_description": self._get_privacy_tier_description(settings.privacy_tier),
            "learning_active": brand.learning_active,
            "patterns_count": len(patterns),
            "feedback_count": brand.feedback_count,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    async def _build_patterns_section(
        self,
        patterns: List[BrandPattern]
    ) -> List[Dict[str, Any]]:
        """Build patterns learned section."""
        return [
            {
                "type": pattern.pattern_type,
                "type_display": self._format_pattern_type(pattern.pattern_type),
                "description": self._generate_pattern_description(pattern),
                "confidence": pattern.confidence_score,
                "confidence_display": f"{pattern.confidence_score * 100:.1f}%",
                "sample_count": pattern.sample_count,
                "created_at": pattern.created_at.isoformat(),
                "details": self._format_pattern_details(pattern)
            }
            for pattern in patterns
        ]
    
    async def _build_data_sources_section(
        self,
        brand: Any,
        settings: LearningSettings
    ) -> Dict[str, Any]:
        """Build data sources section."""
        if settings.privacy_tier == PrivacyTier.OFF:
            return {
                "mode": "off",
                "description": "Learning is disabled",
                "details": "No data is being collected or processed for learning"
            }
        
        elif settings.privacy_tier == PrivacyTier.PRIVATE:
            return {
                "mode": "private",
                "description": "Your brand only",
                "details": f"Learning from {brand.feedback_count} feedback events from your brand. "
                          "No data is shared with other brands.",
                "privacy_guarantee": "Complete data isolation"
            }
        
        else:  # SHARED
            # Get industry pattern info
            if brand.cohort:
                industry_patterns = await self.shared_engine.get_industry_patterns(brand.cohort)
                if industry_patterns:
                    avg_contributors = sum(p.contributor_count for p in industry_patterns) / len(industry_patterns)
                    return {
                        "mode": "shared",
                        "description": f"~{int(avg_contributors)} brands in {brand.cohort} industry",
                        "details": f"Contributing to anonymized industry patterns with "
                                  f"{int(avg_contributors)} other brands in {brand.cohort}.",
                        "privacy_guarantee": "K-anonymity (minimum 5 brands) + Differential privacy"
                    }
            
            return {
                "mode": "shared",
                "description": "Industry cohort (pending)",
                "details": "Waiting for sufficient brands to join cohort",
                "privacy_guarantee": "K-anonymity (minimum 5 brands) + Differential privacy"
            }
    
    async def _build_impact_metrics(
        self,
        brand: Any,
        patterns: List[BrandPattern]
    ) -> Dict[str, Any]:
        """Build impact metrics section."""
        # Calculate metrics
        total_samples = sum(p.sample_count for p in patterns)
        avg_confidence = sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0
        
        # Get before/after metrics (simplified - would need historical data)
        return {
            "patterns_extracted": len(patterns),
            "total_samples_analyzed": total_samples,
            "average_confidence": avg_confidence,
            "confidence_display": f"{avg_confidence * 100:.1f}%",
            "metrics": [
                {
                    "name": "Patterns Learned",
                    "value": len(patterns),
                    "description": "Number of patterns extracted from feedback"
                },
                {
                    "name": "Feedback Analyzed",
                    "value": total_samples,
                    "description": "Total feedback events used for learning"
                },
                {
                    "name": "Average Confidence",
                    "value": f"{avg_confidence * 100:.1f}%",
                    "description": "Confidence in learned patterns"
                }
            ]
        }
    
    async def _build_audit_log_section(
        self,
        audit_log: List[Any]
    ) -> List[Dict[str, Any]]:
        """Build audit log section."""
        return [
            {
                "action": log.action,
                "action_display": self._format_action_name(log.action),
                "details": log.details,
                "timestamp": log.timestamp.isoformat(),
                "timestamp_display": self._format_timestamp(log.timestamp)
            }
            for log in audit_log
        ]
    
    def _build_actions_section(self, settings: LearningSettings) -> Dict[str, Any]:
        """Build actions section with one-click options."""
        return {
            "available_actions": [
                {
                    "id": "change_privacy_tier",
                    "label": "Change Privacy Settings",
                    "description": "Update your privacy tier and consent",
                    "endpoint": "POST /v1/brands/{brand_id}/learning/settings",
                    "icon": "settings"
                },
                {
                    "id": "export_data",
                    "label": "Export Learning Data",
                    "description": "Download all your learning data (GDPR Article 20)",
                    "endpoint": "POST /v1/brands/{brand_id}/learning/export",
                    "icon": "download"
                },
                {
                    "id": "delete_data",
                    "label": "Delete Learning Data",
                    "description": "Permanently delete all learning data (GDPR Article 17)",
                    "endpoint": "DELETE /v1/brands/{brand_id}/learning/data",
                    "icon": "delete",
                    "warning": "This action cannot be undone",
                    "requires_confirmation": True
                }
            ],
            "quick_actions": {
                "disable_learning": {
                    "label": "Disable Learning",
                    "action": "Set privacy_tier to 'off'",
                    "enabled": settings.privacy_tier != PrivacyTier.OFF
                },
                "enable_private_learning": {
                    "label": "Enable Private Learning",
                    "action": "Set privacy_tier to 'private'",
                    "enabled": settings.privacy_tier != PrivacyTier.PRIVATE
                },
                "enable_shared_learning": {
                    "label": "Enable Shared Learning",
                    "action": "Set privacy_tier to 'shared'",
                    "enabled": settings.privacy_tier != PrivacyTier.SHARED,
                    "requires_consent": True
                }
            }
        }
    
    # Helper methods for formatting
    
    def _get_privacy_tier_description(self, tier: PrivacyTier) -> str:
        """Get human-readable description of privacy tier."""
        descriptions = {
            PrivacyTier.OFF: "Learning disabled - No data processing",
            PrivacyTier.PRIVATE: "Private learning - Your brand only",
            PrivacyTier.SHARED: "Shared learning - Anonymized industry patterns"
        }
        return descriptions.get(tier, "Unknown")
    
    def _format_pattern_type(self, pattern_type: str) -> str:
        """Format pattern type for display."""
        return pattern_type.replace("_", " ").title()
    
    def _generate_pattern_description(self, pattern: BrandPattern) -> str:
        """Generate human-readable pattern description."""
        if pattern.pattern_type == "color_preference":
            return f"Color preferences based on {pattern.sample_count} approved assets"
        elif pattern.pattern_type == "style_preference":
            return f"Style preferences based on {pattern.sample_count} approved assets"
        elif pattern.pattern_type == "prompt_optimization":
            return f"Prompt optimizations based on {pattern.sample_count} successful generations"
        else:
            return f"Pattern based on {pattern.sample_count} samples"
    
    def _format_pattern_details(self, pattern: BrandPattern) -> Dict[str, Any]:
        """Format pattern details for display."""
        return {
            "sample_count": pattern.sample_count,
            "confidence": f"{pattern.confidence_score * 100:.1f}%",
            "last_updated": pattern.updated_at.isoformat()
        }
    
    def _format_action_name(self, action: str) -> str:
        """Format action name for display."""
        return action.replace("_", " ").title()
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display."""
        # Calculate relative time
        now = datetime.now(timezone.utc)
        delta = now - timestamp
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
