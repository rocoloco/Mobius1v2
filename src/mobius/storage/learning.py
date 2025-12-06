"""
Storage layer for learning system data.

This module provides database operations for learning settings,
patterns, and audit logs.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import structlog

from mobius.models.learning import (
    LearningSettings,
    BrandPattern,
    IndustryPattern,
    LearningAuditLog,
    PrivacyTier
)
from mobius.storage.database import get_supabase_client

logger = structlog.get_logger()


class LearningStorage:
    """Storage operations for learning system."""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    # Learning Settings Operations
    
    async def get_settings(self, brand_id: str) -> Optional[LearningSettings]:
        """Get learning settings for a brand."""
        result = self.client.table("learning_settings").select("*").eq(
            "brand_id", brand_id
        ).execute()
        
        if result.data:
            return LearningSettings.model_validate(result.data[0])
        return None
    
    async def create_settings(self, settings: LearningSettings) -> LearningSettings:
        """Create learning settings for a brand."""
        data = settings.model_dump()
        result = self.client.table("learning_settings").insert(data).execute()
        return LearningSettings.model_validate(result.data[0])
    
    async def update_settings(
        self,
        brand_id: str,
        updates: Dict[str, Any]
    ) -> LearningSettings:
        """Update learning settings for a brand."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = self.client.table("learning_settings").update(updates).eq(
            "brand_id", brand_id
        ).execute()
        return LearningSettings.model_validate(result.data[0])
    
    # Brand Pattern Operations
    
    async def get_brand_patterns(
        self,
        brand_id: str,
        pattern_type: Optional[str] = None
    ) -> List[BrandPattern]:
        """Get patterns for a brand."""
        query = self.client.table("brand_patterns").select("*").eq(
            "brand_id", brand_id
        )
        
        if pattern_type:
            query = query.eq("pattern_type", pattern_type)
        
        result = query.order("confidence_score", desc=True).execute()
        return [BrandPattern.model_validate(p) for p in result.data]
    
    async def create_brand_pattern(self, pattern: BrandPattern) -> BrandPattern:
        """Create a brand pattern."""
        data = pattern.model_dump()
        result = self.client.table("brand_patterns").insert(data).execute()
        return BrandPattern.model_validate(result.data[0])
    
    async def delete_brand_patterns(self, brand_id: str) -> int:
        """Delete all patterns for a brand."""
        result = self.client.table("brand_patterns").delete().eq(
            "brand_id", brand_id
        ).execute()
        return len(result.data) if result.data else 0
    
    # Industry Pattern Operations
    
    async def get_industry_patterns(
        self,
        cohort: str,
        pattern_type: Optional[str] = None
    ) -> List[IndustryPattern]:
        """Get industry patterns for a cohort."""
        query = self.client.table("industry_patterns").select("*").eq(
            "cohort", cohort
        )
        
        if pattern_type:
            query = query.eq("pattern_type", pattern_type)
        
        result = query.order("contributor_count", desc=True).execute()
        return [IndustryPattern.model_validate(p) for p in result.data]
    
    async def create_industry_pattern(
        self,
        pattern: IndustryPattern
    ) -> IndustryPattern:
        """Create an industry pattern."""
        data = pattern.model_dump()
        result = self.client.table("industry_patterns").insert(data).execute()
        return IndustryPattern.model_validate(result.data[0])
    
    # Audit Log Operations
    
    async def get_audit_log(
        self,
        brand_id: str,
        limit: int = 100
    ) -> List[LearningAuditLog]:
        """Get audit log for a brand."""
        result = self.client.table("learning_audit_log").select("*").eq(
            "brand_id", brand_id
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return [LearningAuditLog.model_validate(log) for log in result.data]
    
    async def create_audit_log(self, log: LearningAuditLog) -> LearningAuditLog:
        """Create an audit log entry."""
        data = log.model_dump()
        result = self.client.table("learning_audit_log").insert(data).execute()
        return LearningAuditLog.model_validate(result.data[0])
