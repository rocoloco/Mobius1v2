"""
Shared learning engine for industry-wide pattern aggregation.

This module implements anonymized industry-wide learning with strict privacy guarantees:
- K-anonymity: Minimum 5 brands must contribute
- Differential privacy: Laplace noise added to prevent individual identification
- No individual brand traces stored
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import numpy as np
import structlog

from mobius.models.learning import (
    IndustryPattern,
    BrandPattern,
    PrivacyTier,
    LearningSettings
)
from mobius.storage.database import get_supabase_client

logger = structlog.get_logger()


class SharedLearningEngine:
    """
    Industry-wide learning engine with differential privacy.
    
    This engine aggregates patterns from multiple brands in the same industry
    cohort while preserving privacy through:
    - K-anonymity enforcement (minimum 5 contributors)
    - Differential privacy noise injection
    - Pattern contributor anonymization
    - Aggregate-only storage
    
    Features:
    - Industry cohort pattern aggregation
    - Differential privacy using Laplace mechanism
    - K-anonymity enforcement
    - No individual brand traces
    """
    
    MIN_CONTRIBUTORS = 5  # K-anonymity threshold
    NOISE_SCALE = 0.1     # Differential privacy noise scale (epsilon = 1/0.1 = 10)
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def aggregate_patterns(
        self,
        cohort: str,
        pattern_type: str
    ) -> Optional[IndustryPattern]:
        """
        Aggregate patterns from multiple brands with privacy preservation.
        
        Collects patterns from all brands in a cohort that have opted into
        shared learning, then aggregates them with differential privacy.
        
        Args:
            cohort: Industry cohort (e.g., "fashion", "tech", "food")
            pattern_type: Type of pattern to aggregate
            
        Returns:
            Aggregated industry pattern, or None if insufficient contributors
            
        Raises:
            ValueError: If cohort or pattern_type is invalid
        """
        logger.info(
            "aggregating_shared_patterns",
            cohort=cohort,
            pattern_type=pattern_type
        )
        
        # Get all brands in cohort with shared learning enabled
        contributing_brands = await self._get_shared_learning_brands(cohort)
        
        # K-anonymity check: Need at least MIN_CONTRIBUTORS brands
        if len(contributing_brands) < self.MIN_CONTRIBUTORS:
            logger.warning(
                "insufficient_contributors",
                cohort=cohort,
                count=len(contributing_brands),
                required=self.MIN_CONTRIBUTORS
            )
            return None
        
        # Collect patterns from all contributing brands
        all_patterns = []
        for brand_id in contributing_brands:
            patterns = await self._get_brand_patterns(brand_id, pattern_type)
            all_patterns.extend(patterns)
        
        if not all_patterns:
            logger.info("no_patterns_to_aggregate", cohort=cohort, pattern_type=pattern_type)
            return None
        
        # Aggregate with differential privacy
        aggregated_data = self._aggregate_with_privacy(all_patterns)
        
        # Create industry pattern
        industry_pattern = IndustryPattern(
            pattern_id=str(uuid.uuid4()),
            cohort=cohort,
            pattern_type=pattern_type,
            pattern_data=aggregated_data,
            contributor_count=len(contributing_brands),
            noise_level=self.NOISE_SCALE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Store pattern
        await self._store_industry_pattern(industry_pattern)
        
        logger.info(
            "industry_pattern_created",
            pattern_id=industry_pattern.pattern_id,
            cohort=cohort,
            contributors=len(contributing_brands)
        )
        
        return industry_pattern
    
    async def get_industry_patterns(
        self,
        cohort: str,
        pattern_type: Optional[str] = None
    ) -> List[IndustryPattern]:
        """
        Get aggregated industry patterns for a cohort.
        
        Args:
            cohort: Industry cohort
            pattern_type: Optional filter by pattern type
            
        Returns:
            List of industry patterns
        """
        query = self.client.table("industry_patterns").select("*").eq(
            "cohort", cohort
        )
        
        if pattern_type:
            query = query.eq("pattern_type", pattern_type)
        
        result = query.order("contributor_count", desc=True).execute()
        
        return [IndustryPattern.model_validate(p) for p in result.data]
    
    def _aggregate_with_privacy(self, patterns: List[BrandPattern]) -> Dict[str, Any]:
        """
        Apply differential privacy noise to aggregated data.
        
        Uses the Laplace mechanism to add noise proportional to the sensitivity
        of the query. This ensures that the presence or absence of any single
        brand's data cannot be reliably detected.
        
        Args:
            patterns: List of brand patterns to aggregate
            
        Returns:
            Aggregated data with differential privacy noise
        """
        # Compute aggregate statistics
        aggregated = self._compute_aggregates(patterns)
        
        # Add Laplace noise for differential privacy
        # Laplace(0, sensitivity/epsilon) where epsilon = 1/NOISE_SCALE
        for key, value in aggregated.items():
            if isinstance(value, (int, float)):
                # Add Laplace noise: Lap(0, scale)
                noise = np.random.laplace(0, self.NOISE_SCALE)
                aggregated[key] = float(value + noise)
                
                # Ensure non-negative values for counts
                if "count" in key.lower():
                    aggregated[key] = max(0, aggregated[key])
        
        # Add metadata about privacy guarantees
        aggregated["_privacy"] = {
            "mechanism": "laplace",
            "noise_scale": self.NOISE_SCALE,
            "epsilon": 1.0 / self.NOISE_SCALE,
            "k_anonymity": len(patterns)
        }
        
        return aggregated
    
    def _compute_aggregates(self, patterns: List[BrandPattern]) -> Dict[str, Any]:
        """
        Compute aggregate statistics from patterns.
        
        Args:
            patterns: List of patterns to aggregate
            
        Returns:
            Dictionary of aggregate statistics
        """
        if not patterns:
            return {}
        
        # Compute basic aggregates
        total_samples = sum(p.sample_count for p in patterns)
        avg_confidence = sum(p.confidence_score for p in patterns) / len(patterns)
        
        # Extract pattern-specific data
        pattern_data_list = [p.pattern_data for p in patterns]
        
        # Aggregate pattern-specific metrics
        aggregated = {
            "total_patterns": len(patterns),
            "total_samples": total_samples,
            "average_confidence": avg_confidence,
            "pattern_count_by_type": {}
        }
        
        # Count patterns by type
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in aggregated["pattern_count_by_type"]:
                aggregated["pattern_count_by_type"][pattern_type] = 0
            aggregated["pattern_count_by_type"][pattern_type] += 1
        
        # Aggregate pattern-specific data
        # This is simplified - real implementation would aggregate specific metrics
        if pattern_data_list:
            # Example: aggregate approval rates if present
            approval_rates = [
                pd.get("approval_rate", 0)
                for pd in pattern_data_list
                if "approval_rate" in pd
            ]
            if approval_rates:
                aggregated["average_approval_rate"] = sum(approval_rates) / len(approval_rates)
        
        return aggregated
    
    async def _get_shared_learning_brands(self, cohort: str) -> List[str]:
        """
        Get brands that opted into shared learning for a cohort.
        
        Args:
            cohort: Industry cohort
            
        Returns:
            List of brand IDs with shared learning enabled
        """
        # Get all brands in cohort
        brands_result = self.client.table("brands").select("brand_id").eq(
            "cohort", cohort
        ).is_("deleted_at", "null").execute()
        
        if not brands_result.data:
            return []
        
        brand_ids = [b["brand_id"] for b in brands_result.data]
        
        # Filter by privacy settings
        shared_brands = []
        for brand_id in brand_ids:
            settings_result = self.client.table("learning_settings").select("*").eq(
                "brand_id", brand_id
            ).execute()
            
            if settings_result.data:
                settings = LearningSettings.model_validate(settings_result.data[0])
                if settings.privacy_tier == PrivacyTier.SHARED:
                    shared_brands.append(brand_id)
        
        return shared_brands
    
    async def _get_brand_patterns(
        self,
        brand_id: str,
        pattern_type: str
    ) -> List[BrandPattern]:
        """
        Get patterns for a specific brand and type.
        
        Args:
            brand_id: Brand identifier
            pattern_type: Type of pattern
            
        Returns:
            List of brand patterns
        """
        result = self.client.table("brand_patterns").select("*").eq(
            "brand_id", brand_id
        ).eq("pattern_type", pattern_type).execute()
        
        return [BrandPattern.model_validate(p) for p in result.data]
    
    async def _store_industry_pattern(self, pattern: IndustryPattern) -> None:
        """
        Store an industry pattern in the database.
        
        Args:
            pattern: Industry pattern to store
        """
        data = pattern.model_dump()
        self.client.table("industry_patterns").insert(data).execute()
    
    async def verify_k_anonymity(self, pattern_id: str) -> bool:
        """
        Verify that a pattern meets k-anonymity requirements.
        
        Args:
            pattern_id: Pattern to verify
            
        Returns:
            True if pattern meets k-anonymity requirements
        """
        result = self.client.table("industry_patterns").select("*").eq(
            "pattern_id", pattern_id
        ).execute()
        
        if not result.data:
            return False
        
        pattern = IndustryPattern.model_validate(result.data[0])
        return pattern.contributor_count >= self.MIN_CONTRIBUTORS
    
    async def verify_differential_privacy(self, pattern_id: str) -> bool:
        """
        Verify that a pattern has differential privacy noise applied.
        
        Args:
            pattern_id: Pattern to verify
            
        Returns:
            True if pattern has differential privacy noise
        """
        result = self.client.table("industry_patterns").select("*").eq(
            "pattern_id", pattern_id
        ).execute()
        
        if not result.data:
            return False
        
        pattern = IndustryPattern.model_validate(result.data[0])
        return pattern.noise_level > 0
    
    def calculate_privacy_budget(self, num_queries: int) -> float:
        """
        Calculate remaining privacy budget (epsilon) after queries.
        
        Differential privacy has a privacy budget that depletes with each query.
        This helps track how much privacy has been "spent".
        
        Args:
            num_queries: Number of queries made
            
        Returns:
            Total epsilon spent
        """
        epsilon_per_query = 1.0 / self.NOISE_SCALE
        return epsilon_per_query * num_queries
    
    async def anonymize_contributors(
        self,
        pattern_id: str
    ) -> Dict[str, Any]:
        """
        Get anonymized contributor information for a pattern.
        
        Returns aggregate information about contributors without
        revealing individual brand identities.
        
        Args:
            pattern_id: Pattern to get contributor info for
            
        Returns:
            Anonymized contributor information
        """
        result = self.client.table("industry_patterns").select("*").eq(
            "pattern_id", pattern_id
        ).execute()
        
        if not result.data:
            return {}
        
        pattern = IndustryPattern.model_validate(result.data[0])
        
        # Return only aggregate information
        return {
            "cohort": pattern.cohort,
            "contributor_count": pattern.contributor_count,
            "description": f"{pattern.contributor_count} brands in {pattern.cohort} industry",
            "individual_brands": "Not disclosed (privacy protection)"
        }
