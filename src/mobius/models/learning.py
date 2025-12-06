"""
Learning system data models with privacy controls.

This module defines the data models for Mobius's meta-learning system,
which enables the platform to improve generation quality over time while
maintaining strict privacy controls.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class PrivacyTier(str, Enum):
    """
    Privacy tiers for learning system.
    
    OFF: No automated learning, manual review only
    PRIVATE: Learn from own brand's feedback only (default)
    SHARED: Contribute to anonymized industry patterns (opt-in)
    """
    OFF = "off"
    PRIVATE = "private"
    SHARED = "shared"


class LearningSettings(BaseModel):
    """
    Privacy settings and consent tracking for brand learning.
    
    Controls how a brand's feedback data is used for learning and
    tracks consent for data processing.
    """
    brand_id: str = Field(description="Brand identifier")
    privacy_tier: PrivacyTier = Field(
        default=PrivacyTier.PRIVATE,
        description="Privacy tier controlling learning behavior"
    )
    consent_date: Optional[datetime] = Field(
        default=None,
        description="When user consented to current privacy tier"
    )
    consent_version: str = Field(
        default="1.0",
        description="Version of consent agreement"
    )
    data_retention_days: int = Field(
        default=365,
        description="How long to retain learning data"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BrandPattern(BaseModel):
    """
    Learned pattern from a single brand's feedback (private learning).
    
    Stores brand-specific patterns extracted from feedback history.
    Data is isolated per brand and never shared.
    """
    pattern_id: str = Field(description="Unique pattern identifier")
    brand_id: str = Field(description="Brand this pattern belongs to")
    pattern_type: str = Field(
        description="Type of pattern: color_preference, style_preference, prompt_optimization"
    )
    pattern_data: Dict[str, Any] = Field(
        description="Pattern-specific data structure"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in this pattern (0-1)"
    )
    sample_count: int = Field(
        ge=0,
        description="Number of feedback samples used to extract this pattern"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IndustryPattern(BaseModel):
    """
    Aggregated pattern from multiple brands (shared learning).
    
    Stores anonymized industry-wide patterns with privacy guarantees:
    - K-anonymity: Minimum 5 brands contribute
    - Differential privacy: Noise added to prevent individual identification
    - No individual brand traces stored
    """
    pattern_id: str = Field(description="Unique pattern identifier")
    cohort: str = Field(
        description="Industry cohort: fashion, tech, food, etc."
    )
    pattern_type: str = Field(
        description="Type of pattern: color_preference, style_preference, etc."
    )
    pattern_data: Dict[str, Any] = Field(
        description="Aggregated pattern data with differential privacy noise"
    )
    contributor_count: int = Field(
        ge=5,
        description="Number of brands contributing (minimum 5 for k-anonymity)"
    )
    noise_level: float = Field(
        gt=0.0,
        description="Differential privacy noise scale applied"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningAuditLog(BaseModel):
    """
    Audit log entry for learning system actions.
    
    Provides transparency by logging all learning-related actions
    for compliance and user trust.
    """
    log_id: str = Field(description="Unique log entry identifier")
    brand_id: str = Field(description="Brand this action relates to")
    action: str = Field(
        description="Action performed: pattern_extracted, prompt_optimized, "
                    "data_exported, data_deleted, privacy_tier_changed"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific details"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Privacy Tier Behavior Documentation
PRIVACY_TIER_BEHAVIORS = {
    "off": {
        "name": "Off (Manual Only)",
        "description": "No automated learning. All feedback stored but not used for training.",
        "data_usage": "Feedback collected but not processed",
        "data_sharing": "No data sharing",
        "suitable_for": "Highly regulated industries (healthcare, finance)",
        "guarantees": [
            "No automated pattern extraction",
            "Manual review and adjustment only",
            "Full data retention for audit purposes"
        ]
    },
    "private": {
        "name": "Private (Default)",
        "description": "Learn from own brand's feedback only with complete data isolation.",
        "data_usage": "Brand-specific pattern extraction and prompt optimization",
        "data_sharing": "No data sharing with other brands",
        "suitable_for": "Most organizations, default for all new brands",
        "guarantees": [
            "Complete data isolation between brands",
            "Brand-specific prompt optimization",
            "Full data ownership and control",
            "Can export or delete data at any time"
        ]
    },
    "shared": {
        "name": "Shared (Opt-in)",
        "description": "Contribute to anonymized industry patterns with privacy preservation.",
        "data_usage": "Aggregated with other brands in same industry cohort",
        "data_sharing": "Anonymized patterns shared across cohort",
        "suitable_for": "Organizations wanting network effects",
        "guarantees": [
            "Differential privacy noise injection",
            "K-anonymity enforcement (minimum 5 brands)",
            "Pattern contributor anonymization",
            "Aggregate-only storage (no individual traces)",
            "Can opt-out at any time"
        ]
    }
}


# Legal Review Checklist for Shared Mode
SHARED_MODE_LEGAL_CHECKLIST = {
    "title": "Legal Review Checklist for Shared Learning Mode",
    "version": "1.0",
    "last_updated": "2025-12-05",
    "checklist": [
        {
            "category": "Data Protection",
            "items": [
                "Verify differential privacy implementation meets industry standards",
                "Confirm k-anonymity threshold (minimum 5 brands) is enforced",
                "Validate that no individual brand data can be reverse-engineered",
                "Ensure aggregate-only storage with no individual traces",
                "Verify data retention policies comply with local regulations"
            ]
        },
        {
            "category": "Consent Management",
            "items": [
                "Obtain explicit opt-in consent before enabling shared mode",
                "Provide clear explanation of data usage in plain language",
                "Document consent version and timestamp",
                "Enable easy opt-out mechanism",
                "Notify users of any changes to privacy practices"
            ]
        },
        {
            "category": "Transparency",
            "items": [
                "Provide dashboard showing what patterns were learned",
                "Display data sources (e.g., '5 fashion brands')",
                "Show impact metrics (compliance score improvements)",
                "Maintain audit log of all learning actions",
                "Enable data export functionality"
            ]
        },
        {
            "category": "User Rights",
            "items": [
                "Implement right to access learning data",
                "Implement right to export learning data (GDPR Article 20)",
                "Implement right to delete learning data (GDPR Article 17)",
                "Implement right to opt-out of shared learning",
                "Provide mechanism to update privacy preferences"
            ]
        },
        {
            "category": "Security",
            "items": [
                "Encrypt learning data at rest",
                "Encrypt learning data in transit",
                "Implement access controls for learning data",
                "Log all access to learning data",
                "Regular security audits of learning system"
            ]
        }
    ]
}


# Consent UI Flow Documentation
CONSENT_UI_FLOW = {
    "title": "Learning Privacy Consent Flow",
    "version": "1.0",
    "steps": [
        {
            "step": 1,
            "screen": "Privacy Tier Selection",
            "description": "Present three privacy tiers with clear explanations",
            "elements": [
                "Radio buttons for Off, Private (default), Shared",
                "Visual comparison chart showing differences",
                "Examples of what each tier means in practice",
                "Recommendation badge on 'Private' option"
            ],
            "example_text": {
                "off": "Manual only - No automated learning. Best for highly regulated industries.",
                "private": "Private learning - Learn from your brand only. Recommended for most users.",
                "shared": "Shared learning - Contribute to industry improvements with privacy protection."
            }
        },
        {
            "step": 2,
            "screen": "Shared Mode Details (if selected)",
            "description": "Explain shared mode privacy guarantees",
            "elements": [
                "Explanation of differential privacy",
                "Explanation of k-anonymity (minimum 5 brands)",
                "Visual showing 'Your data' → 'Noise added' → 'Aggregated pattern'",
                "List of what IS and IS NOT shared",
                "Example: 'Fashion brands prefer warm colors' (aggregate) vs 'Brand X uses #FF0000' (never shared)"
            ]
        },
        {
            "step": 3,
            "screen": "Consent Confirmation",
            "description": "Obtain explicit consent",
            "elements": [
                "Checkbox: 'I understand how my data will be used'",
                "Checkbox: 'I consent to [selected tier] learning mode'",
                "Link to full privacy policy",
                "Link to data processing addendum",
                "Prominent 'Confirm' button (disabled until checkboxes checked)"
            ]
        },
        {
            "step": 4,
            "screen": "Confirmation & Next Steps",
            "description": "Confirm settings and show transparency options",
            "elements": [
                "Success message with selected tier",
                "Link to learning dashboard",
                "Reminder that settings can be changed anytime",
                "Link to data export functionality",
                "Link to data deletion functionality"
            ]
        }
    ],
    "change_flow": {
        "description": "Changing privacy tier after initial setup",
        "steps": [
            "Navigate to Settings > Learning Privacy",
            "View current tier and consent date",
            "Click 'Change Privacy Tier'",
            "Follow steps 1-4 above",
            "If downgrading from Shared to Private: Confirm that shared contributions will remain but no new data will be shared",
            "If upgrading to Shared: Full consent flow required"
        ]
    }
}
