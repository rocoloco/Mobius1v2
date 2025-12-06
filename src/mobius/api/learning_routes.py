"""
API route handlers for learning management endpoints.

These endpoints provide transparency and control over the learning system,
allowing users to manage privacy settings, view learned patterns, export data,
and delete learning data.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import uuid
import structlog

from mobius.api.schemas import (
    UpdateLearningSettingsRequest,
    LearningSettingsResponse,
    LearningPatternsResponse,
    BrandPatternResponse,
    LearningDashboardResponse,
    LearningAuditLogResponse,
    LearningAuditLogEntry,
    ExportLearningDataResponse,
    DeleteLearningDataResponse
)
from mobius.api.utils import generate_request_id, set_request_id, get_request_id
from mobius.api.errors import NotFoundError, ValidationError
from mobius.learning.private import PrivateLearningEngine
from mobius.learning.shared import SharedLearningEngine
from mobius.storage.learning import LearningStorage
from mobius.storage.brands import BrandStorage
from mobius.models.learning import LearningSettings, PrivacyTier

logger = structlog.get_logger()


async def update_learning_settings_handler(
    brand_id: str,
    request: UpdateLearningSettingsRequest
) -> LearningSettingsResponse:
    """
    Update learning privacy settings for a brand.
    
    POST /v1/brands/{brand_id}/learning/settings
    
    Allows users to change their privacy tier and consent settings.
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info(
        "update_learning_settings_request",
        request_id=request_id,
        brand_id=brand_id,
        privacy_tier=request.privacy_tier
    )
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Get or create settings
    learning_storage = LearningStorage()
    existing_settings = await learning_storage.get_settings(brand_id)
    
    # Prepare updates
    updates = {
        "privacy_tier": request.privacy_tier,
        "consent_date": request.consent_date or datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if request.data_retention_days is not None:
        updates["data_retention_days"] = request.data_retention_days
    
    # Update or create settings
    if existing_settings:
        settings = await learning_storage.update_settings(brand_id, updates)
    else:
        settings = LearningSettings(
            brand_id=brand_id,
            privacy_tier=PrivacyTier(request.privacy_tier),
            consent_date=datetime.now(timezone.utc),
            data_retention_days=request.data_retention_days or 365
        )
        settings = await learning_storage.create_settings(settings)
    
    logger.info(
        "learning_settings_updated",
        request_id=request_id,
        brand_id=brand_id,
        privacy_tier=settings.privacy_tier
    )
    
    return LearningSettingsResponse(
        brand_id=settings.brand_id,
        privacy_tier=settings.privacy_tier.value,
        consent_date=settings.consent_date,
        consent_version=settings.consent_version,
        data_retention_days=settings.data_retention_days,
        created_at=settings.created_at,
        updated_at=settings.updated_at,
        request_id=request_id
    )


async def get_learning_settings_handler(brand_id: str) -> LearningSettingsResponse:
    """
    Get current learning settings for a brand.
    
    GET /v1/brands/{brand_id}/learning/settings
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("get_learning_settings_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Get settings
    learning_storage = LearningStorage()
    settings = await learning_storage.get_settings(brand_id)
    
    if not settings:
        # Return default settings
        settings = LearningSettings(
            brand_id=brand_id,
            privacy_tier=PrivacyTier.PRIVATE
        )
    
    return LearningSettingsResponse(
        brand_id=settings.brand_id,
        privacy_tier=settings.privacy_tier.value,
        consent_date=settings.consent_date,
        consent_version=settings.consent_version,
        data_retention_days=settings.data_retention_days,
        created_at=settings.created_at,
        updated_at=settings.updated_at,
        request_id=request_id
    )


async def get_learning_dashboard_handler(brand_id: str) -> LearningDashboardResponse:
    """
    Get learning transparency dashboard for a brand.
    
    GET /v1/brands/{brand_id}/learning/dashboard
    
    Shows what patterns were learned, data sources, and impact metrics.
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("get_learning_dashboard_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Get settings
    learning_storage = LearningStorage()
    settings = await learning_storage.get_settings(brand_id)
    
    if not settings:
        settings = LearningSettings(brand_id=brand_id, privacy_tier=PrivacyTier.PRIVATE)
    
    # Get patterns
    patterns = await learning_storage.get_brand_patterns(brand_id)
    
    # Format patterns for dashboard
    patterns_learned = [
        {
            "type": p.pattern_type,
            "description": f"Pattern based on {p.sample_count} samples",
            "confidence": p.confidence_score
        }
        for p in patterns
    ]
    
    # Determine data sources based on privacy tier
    if settings.privacy_tier == PrivacyTier.OFF:
        data_sources = "Learning disabled"
    elif settings.privacy_tier == PrivacyTier.PRIVATE:
        data_sources = "Your brand only"
    else:  # SHARED
        # Get industry patterns to count contributors
        if brand.cohort:
            shared_engine = SharedLearningEngine()
            industry_patterns = await shared_engine.get_industry_patterns(brand.cohort)
            if industry_patterns:
                avg_contributors = sum(p.contributor_count for p in industry_patterns) / len(industry_patterns)
                data_sources = f"~{int(avg_contributors)} brands in {brand.cohort} industry"
            else:
                data_sources = f"{brand.cohort} industry (aggregating)"
        else:
            data_sources = "Industry cohort (pending)"
    
    # Calculate impact metrics (simplified)
    impact_metrics = {
        "patterns_extracted": len(patterns),
        "total_samples": sum(p.sample_count for p in patterns),
        "average_confidence": sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0
    }
    
    return LearningDashboardResponse(
        brand_id=brand_id,
        privacy_tier=settings.privacy_tier.value,
        patterns_learned=patterns_learned,
        data_sources=data_sources,
        impact_metrics=impact_metrics,
        last_updated=datetime.now(timezone.utc),
        request_id=request_id
    )


async def get_learning_patterns_handler(brand_id: str) -> LearningPatternsResponse:
    """
    Get learned patterns for a brand.
    
    GET /v1/brands/{brand_id}/learning/patterns
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("get_learning_patterns_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Get patterns
    learning_storage = LearningStorage()
    patterns = await learning_storage.get_brand_patterns(brand_id)
    
    # Format patterns
    pattern_responses = [
        BrandPatternResponse(
            pattern_id=p.pattern_id,
            brand_id=p.brand_id,
            pattern_type=p.pattern_type,
            pattern_data=p.pattern_data,
            confidence_score=p.confidence_score,
            sample_count=p.sample_count,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in patterns
    ]
    
    return LearningPatternsResponse(
        brand_id=brand_id,
        patterns=pattern_responses,
        total=len(pattern_responses),
        request_id=request_id
    )


async def export_learning_data_handler(brand_id: str) -> ExportLearningDataResponse:
    """
    Export all learning data for a brand (GDPR Article 20 compliance).
    
    POST /v1/brands/{brand_id}/learning/export
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("export_learning_data_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Export data using private learning engine
    private_engine = PrivateLearningEngine()
    export_data = await private_engine.export_learning_data(brand_id)
    
    logger.info(
        "learning_data_exported",
        request_id=request_id,
        brand_id=brand_id,
        pattern_count=len(export_data["patterns"])
    )
    
    return ExportLearningDataResponse(
        brand_id=export_data["brand_id"],
        export_date=datetime.fromisoformat(export_data["export_date"]),
        settings=export_data["settings"],
        patterns=export_data["patterns"],
        audit_log=export_data["audit_log"],
        metadata=export_data["metadata"],
        request_id=request_id
    )


async def delete_learning_data_handler(brand_id: str) -> DeleteLearningDataResponse:
    """
    Delete all learning data for a brand (GDPR Article 17 compliance).
    
    DELETE /v1/brands/{brand_id}/learning/data
    
    This permanently removes all patterns. This action cannot be undone.
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("delete_learning_data_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Delete data using private learning engine
    private_engine = PrivateLearningEngine()
    success = await private_engine.delete_learning_data(brand_id)
    
    logger.info(
        "learning_data_deleted",
        request_id=request_id,
        brand_id=brand_id,
        success=success
    )
    
    return DeleteLearningDataResponse(
        brand_id=brand_id,
        deleted=success,
        message="All learning data has been permanently deleted" if success else "Deletion failed",
        request_id=request_id
    )


async def get_learning_audit_log_handler(brand_id: str) -> LearningAuditLogResponse:
    """
    Get audit log for learning system actions.
    
    GET /v1/brands/{brand_id}/learning/audit
    
    Provides transparency by showing all learning-related actions.
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("get_learning_audit_log_request", request_id=request_id, brand_id=brand_id)
    
    # Verify brand exists
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    if not brand:
        raise NotFoundError("brand", brand_id, request_id)
    
    # Get audit log
    learning_storage = LearningStorage()
    audit_log = await learning_storage.get_audit_log(brand_id, limit=100)
    
    # Format entries
    entries = [
        LearningAuditLogEntry(
            log_id=log.log_id,
            action=log.action,
            details=log.details,
            timestamp=log.timestamp
        )
        for log in audit_log
    ]
    
    return LearningAuditLogResponse(
        brand_id=brand_id,
        entries=entries,
        total=len(entries),
        request_id=request_id
    )
