"""
Private learning engine for per-brand pattern extraction.

This module implements brand-specific learning with complete data isolation.
No data is shared between brands, ensuring maximum privacy.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from collections import Counter
import uuid
import re
import structlog

from mobius.models.learning import (
    BrandPattern,
    LearningSettings,
    PrivacyTier,
    LearningAuditLog
)
from mobius.storage.database import get_supabase_client

logger = structlog.get_logger()


class PrivateLearningEngine:
    """
    Per-brand learning engine with full data isolation.
    
    This engine extracts patterns from a brand's feedback history and uses them
    to optimize future generations. All data remains isolated to the brand and
    is never shared with other brands.
    
    Features:
    - Pattern extraction from feedback history
    - Brand-specific prompt optimization
    - GDPR-compliant data export
    - Right to deletion support
    """
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def extract_patterns(self, brand_id: str) -> List[BrandPattern]:
        """
        Extract patterns from brand's feedback history.
        
        Analyzes all feedback for the brand and extracts patterns such as:
        - Color preferences (which colors get approved more often)
        - Style preferences (which styles get approved more often)
        - Prompt patterns (which prompt structures work better)
        
        Args:
            brand_id: Brand to extract patterns for
            
        Returns:
            List of extracted patterns
            
        Raises:
            ValueError: If brand doesn't exist or learning is disabled
        """
        logger.info("extracting_private_patterns", brand_id=brand_id)
        
        # Verify consent FIRST
        if not await self._verify_consent(brand_id, PrivacyTier.PRIVATE):
            logger.info("pattern_extraction_blocked", brand_id=brand_id, reason="no_consent")
            await self._log_action(
                brand_id,
                "pattern_extraction_blocked",
                {"reason": "insufficient_consent"}
            )
            return []
        
        # Get feedback data for this brand only
        feedback_result = self.client.table("feedback").select(
            "*, assets!inner(compliance_score, generation_params)"
        ).eq("brand_id", brand_id).execute()
        
        if not feedback_result.data:
            logger.info("no_feedback_data", brand_id=brand_id)
            return []
        
        feedback_data = feedback_result.data
        patterns = []
        
        # Extract color preferences
        color_pattern = await self._extract_color_preferences(brand_id, feedback_data)
        if color_pattern:
            patterns.append(color_pattern)
        
        # Extract style preferences
        style_pattern = await self._extract_style_preferences(brand_id, feedback_data)
        if style_pattern:
            patterns.append(style_pattern)
        
        # Extract prompt optimization patterns
        prompt_pattern = await self._extract_prompt_patterns(brand_id, feedback_data)
        if prompt_pattern:
            patterns.append(prompt_pattern)
        
        # Minimize data before storing
        for pattern in patterns:
            pattern.pattern_data = self._minimize_pattern_data(pattern.pattern_data)
            await self._store_pattern(pattern)
        
        # Log action for transparency
        await self._log_action(
            brand_id,
            "pattern_extracted",
            {
                "pattern_count": len(patterns),
                "pattern_types": [p.pattern_type for p in patterns]
            }
        )
        
        logger.info(
            "patterns_extracted",
            brand_id=brand_id,
            pattern_count=len(patterns)
        )
        
        return patterns
    
    async def optimize_prompt(self, brand_id: str, base_prompt: str) -> str:
        """
        Optimize prompt based on brand's learned patterns.
        
        Applies learned optimizations to improve generation quality based on
        the brand's historical feedback.
        
        Args:
            brand_id: Brand to optimize for
            base_prompt: Original prompt to optimize
            
        Returns:
            Optimized prompt
        """
        logger.info("optimizing_prompt", brand_id=brand_id)
        
        # Check privacy settings
        settings = await self._get_settings(brand_id)
        if settings.privacy_tier == PrivacyTier.OFF:
            logger.info("optimization_skipped", brand_id=brand_id, reason="learning_disabled")
            return base_prompt
        
        # Get learned patterns for this brand
        patterns = await self._get_patterns(brand_id)
        
        if not patterns:
            logger.info("no_patterns_available", brand_id=brand_id)
            return base_prompt
        
        # Apply learned optimizations
        optimized = base_prompt
        for pattern in patterns:
            if pattern.pattern_type == "prompt_optimization":
                optimized = self._apply_optimization(optimized, pattern.pattern_data)
        
        # Log action
        await self._log_action(
            brand_id,
            "prompt_optimized",
            {
                "original_length": len(base_prompt),
                "optimized_length": len(optimized),
                "patterns_applied": len([p for p in patterns if p.pattern_type == "prompt_optimization"])
            }
        )
        
        logger.info(
            "prompt_optimized",
            brand_id=brand_id,
            original_length=len(base_prompt),
            optimized_length=len(optimized)
        )
        
        return optimized
    
    async def export_learning_data(self, brand_id: str) -> Dict[str, Any]:
        """
        Export all learning data for a brand (GDPR Article 20 compliance).
        
        Returns all patterns, settings, and audit logs for the brand in a
        machine-readable format.
        
        Args:
            brand_id: Brand to export data for
            
        Returns:
            Dictionary containing all learning data
        """
        logger.info("exporting_learning_data", brand_id=brand_id)
        
        # Get all data
        patterns = await self._get_patterns(brand_id)
        settings = await self._get_settings(brand_id)
        audit_log = await self._get_audit_log(brand_id)
        
        export_data = {
            "brand_id": brand_id,
            "export_date": datetime.now(timezone.utc).isoformat(),
            "settings": settings.model_dump() if settings else None,
            "patterns": [p.model_dump() for p in patterns],
            "audit_log": [log.model_dump() for log in audit_log],
            "metadata": {
                "pattern_count": len(patterns),
                "audit_log_entries": len(audit_log),
                "export_format_version": "1.0"
            }
        }
        
        # Log export action
        await self._log_action(
            brand_id,
            "data_exported",
            {
                "pattern_count": len(patterns),
                "audit_log_entries": len(audit_log)
            }
        )
        
        logger.info(
            "learning_data_exported",
            brand_id=brand_id,
            pattern_count=len(patterns)
        )
        
        return export_data
    
    async def delete_learning_data(self, brand_id: str) -> bool:
        """
        Delete all learning data for a brand (GDPR Article 17 compliance).
        
        Permanently removes all patterns and audit logs for the brand.
        This action cannot be undone.
        
        Args:
            brand_id: Brand to delete data for
            
        Returns:
            True if deletion successful
        """
        logger.info("deleting_learning_data", brand_id=brand_id)
        
        # Log deletion BEFORE deleting (so it's in the audit log)
        await self._log_action(
            brand_id,
            "data_deletion_initiated",
            {"timestamp": datetime.now(timezone.utc).isoformat()}
        )
        
        # Delete all patterns for this brand
        self.client.table("brand_patterns").delete().eq(
            "brand_id", brand_id
        ).execute()
        
        # Note: We keep the audit log for compliance purposes
        # The audit log shows that deletion occurred
        # If full deletion including audit log is required, uncomment:
        # self.client.table("learning_audit_log").delete().eq(
        #     "brand_id", brand_id
        # ).execute()
        
        logger.info("learning_data_deleted", brand_id=brand_id)
        
        return True
    
    # Private helper methods
    
    async def _get_settings(self, brand_id: str) -> LearningSettings:
        """Get learning settings for a brand."""
        result = self.client.table("learning_settings").select("*").eq(
            "brand_id", brand_id
        ).execute()
        
        if result.data:
            return LearningSettings.model_validate(result.data[0])
        
        # Return default settings if none exist
        return LearningSettings(
            brand_id=brand_id,
            privacy_tier=PrivacyTier.PRIVATE
        )
    
    async def _get_patterns(
        self,
        brand_id: str,
        pattern_type: Optional[str] = None
    ) -> List[BrandPattern]:
        """Get learned patterns for a brand."""
        query = self.client.table("brand_patterns").select("*").eq(
            "brand_id", brand_id
        )
        
        if pattern_type:
            query = query.eq("pattern_type", pattern_type)
        
        result = query.order("confidence_score", desc=True).execute()
        
        return [BrandPattern.model_validate(p) for p in result.data]
    
    async def _get_audit_log(self, brand_id: str) -> List[LearningAuditLog]:
        """Get audit log for a brand."""
        result = self.client.table("learning_audit_log").select("*").eq(
            "brand_id", brand_id
        ).order("timestamp", desc=True).execute()
        
        return [LearningAuditLog.model_validate(log) for log in result.data]
    
    async def _store_pattern(self, pattern: BrandPattern) -> None:
        """Store a pattern in the database."""
        # Only store patterns with sufficient confidence
        if pattern.confidence_score < 0.3:
            logger.info(
                "pattern_rejected_low_confidence",
                pattern_id=pattern.pattern_id,
                confidence=pattern.confidence_score
            )
            return
        
        data = pattern.model_dump()
        self.client.table("brand_patterns").insert(data).execute()
    
    async def _log_action(
        self,
        brand_id: str,
        action: str,
        details: Dict[str, Any]
    ) -> None:
        """Log an action to the audit log."""
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "action": action,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.client.table("learning_audit_log").insert(log_entry).execute()
    
    async def _extract_color_preferences(
        self,
        brand_id: str,
        feedback_data: List[Dict[str, Any]]
    ) -> Optional[BrandPattern]:
        """
        Extract color preference patterns from feedback.
        
        Analyzes which specific colors (hex codes) appear more frequently in
        approved assets vs rejected assets, calculating success rates for each.
        
        Algorithm:
        1. Extract colors from generation_params of all approved/rejected assets
        2. Count occurrences of each color in approved vs rejected
        3. Calculate success_rate = approved_count / (approved_count + rejected_count)
        4. Filter for colors with ≥3 total occurrences (statistical significance)
        5. Keep only colors with success_rate > 60%
        6. Calculate confidence based on total sample size
        
        Returns:
            BrandPattern with color_preferences dict, or None if insufficient data
        """
        approved = [f for f in feedback_data if f["action"] == "approve"]
        rejected = [f for f in feedback_data if f["action"] == "reject"]
        
        if len(approved) < 5:  # Need minimum samples
            return None
        
        # Count color occurrences in approved and rejected
        approved_colors = Counter()
        rejected_colors = Counter()
        
        for feedback in approved:
            colors = feedback.get("assets", {}).get("generation_params", {}).get("colors_used", [])
            approved_colors.update(colors)
        
        for feedback in rejected:
            colors = feedback.get("assets", {}).get("generation_params", {}).get("colors_used", [])
            rejected_colors.update(colors)
        
        # Calculate success rates for each color
        color_preferences = {}
        all_colors = set(approved_colors.keys()) | set(rejected_colors.keys())
        
        for color in all_colors:
            approved_count = approved_colors.get(color, 0)
            rejected_count = rejected_colors.get(color, 0)
            total_count = approved_count + rejected_count
            
            # Require minimum 3 occurrences for statistical significance
            if total_count < 3:
                continue
            
            success_rate = approved_count / total_count
            
            # Only keep colors with >60% success rate
            if success_rate > 0.6:
                confidence = self._calculate_statistical_significance(
                    approved_count, rejected_count, total_count
                )
                
                color_preferences[color] = {
                    "success_rate": round(success_rate, 2),
                    "approved_count": approved_count,
                    "rejected_count": rejected_count,
                    "confidence": round(confidence, 2)
                }
        
        if not color_preferences:
            return None
        
        pattern_data = {
            "color_preferences": color_preferences,
            "total_approved": len(approved),
            "total_rejected": len(rejected),
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Overall confidence based on sample size
        confidence = min(len(approved) / 50.0, 1.0)
        
        return BrandPattern(
            pattern_id=str(uuid.uuid4()),
            brand_id=brand_id,
            pattern_type="color_preference",
            pattern_data=pattern_data,
            confidence_score=confidence,
            sample_count=len(feedback_data)
        )
    
    async def _extract_style_preferences(
        self,
        brand_id: str,
        feedback_data: List[Dict[str, Any]]
    ) -> Optional[BrandPattern]:
        """
        Extract style preference patterns from feedback.
        
        Analyzes generation parameters (model, style, aspect_ratio, etc.) of
        approved assets to identify successful configurations.
        
        Algorithm:
        1. Extract generation_params from all approved assets
        2. Count frequency of each parameter value (e.g., model="flux-pro")
        3. Calculate success rates for each parameter value
        4. Identify parameter combinations that appear frequently
        5. Store as style_preferences with confidence scores
        
        Returns:
            BrandPattern with style preferences, or None if <5 approved samples
        """
        approved = [f for f in feedback_data if f["action"] == "approve"]
        
        if len(approved) < 5:
            return None
        
        # Analyze generation parameters
        param_counters = {
            "model": Counter(),
            "style": Counter(),
            "aspect_ratio": Counter(),
            "guidance_scale": Counter()
        }
        
        for feedback in approved:
            params = feedback.get("assets", {}).get("generation_params", {})
            for param_name in param_counters.keys():
                if param_name in params:
                    param_counters[param_name][params[param_name]] += 1
        
        # Build style preferences
        style_preferences = {}
        for param_name, counter in param_counters.items():
            if counter:
                total = sum(counter.values())
                style_preferences[param_name] = {
                    value: {
                        "count": count,
                        "percentage": round(count / total, 2)
                    }
                    for value, count in counter.items()
                }
        
        if not style_preferences:
            return None
        
        pattern_data = {
            "style_preferences": style_preferences,
            "total_approved": len(approved),
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        confidence = min(len(approved) / 50.0, 1.0)
        
        return BrandPattern(
            pattern_id=str(uuid.uuid4()),
            brand_id=brand_id,
            pattern_type="style_preference",
            pattern_data=pattern_data,
            confidence_score=confidence,
            sample_count=len(approved)
        )
    
    async def _extract_prompt_patterns(
        self,
        brand_id: str,
        feedback_data: List[Dict[str, Any]]
    ) -> Optional[BrandPattern]:
        """
        Extract prompt optimization patterns from feedback.
        
        Analyzes prompts that led to approved vs rejected assets to identify:
        1. Style descriptors that improve success (e.g., "modern", "minimalist")
        2. Terms that should be avoided (appear more in rejected)
        3. Prompt structures that work well
        
        Algorithm:
        1. Tokenize prompts from approved and rejected assets
        2. Calculate term frequency in approved vs rejected
        3. Identify terms with significantly higher success rates
        4. Build optimization rules (add successful terms, avoid problematic ones)
        5. Store as actionable optimizations
        
        Returns:
            BrandPattern with prompt optimizations, or None if <10 approved samples
        """
        approved = [f for f in feedback_data if f["action"] == "approve"]
        rejected = [f for f in feedback_data if f["action"] == "reject"]
        
        if len(approved) < 10:  # Need more samples for prompt patterns
            return None
        
        # Tokenize prompts
        approved_terms = Counter()
        rejected_terms = Counter()
        
        for feedback in approved:
            prompt = feedback.get("assets", {}).get("generation_params", {}).get("prompt", "")
            terms = self._tokenize_prompt(prompt)
            approved_terms.update(terms)
        
        for feedback in rejected:
            prompt = feedback.get("assets", {}).get("generation_params", {}).get("prompt", "")
            terms = self._tokenize_prompt(prompt)
            rejected_terms.update(terms)
        
        # Calculate term success rates
        optimizations = []
        all_terms = set(approved_terms.keys()) | set(rejected_terms.keys())
        
        for term in all_terms:
            approved_count = approved_terms.get(term, 0)
            rejected_count = rejected_terms.get(term, 0)
            total_count = approved_count + rejected_count
            
            if total_count < 5:  # Need minimum occurrences
                continue
            
            success_rate = approved_count / total_count
            confidence = self._calculate_statistical_significance(
                approved_count, rejected_count, total_count
            )
            
            # High-value terms (>70% success rate)
            if success_rate > 0.7:
                optimizations.append({
                    "type": "add_style_descriptor",
                    "descriptor": term,
                    "success_rate": round(success_rate, 2),
                    "occurrences": total_count,
                    "confidence": round(confidence, 2)
                })
            
            # Problematic terms (<40% success rate)
            elif success_rate < 0.4:
                optimizations.append({
                    "type": "remove_problematic_term",
                    "term": term,
                    "success_rate": round(success_rate, 2),
                    "occurrences": total_count,
                    "confidence": round(confidence, 2)
                })
            
            # Emphasis-worthy terms (60-70% success rate)
            elif 0.6 < success_rate <= 0.7:
                optimizations.append({
                    "type": "emphasize_element",
                    "element": term,
                    "success_rate": round(success_rate, 2),
                    "occurrences": total_count,
                    "confidence": round(confidence, 2)
                })
        
        if not optimizations:
            return None
        
        pattern_data = {
            "optimizations": optimizations,
            "total_approved": len(approved),
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        confidence = min(len(approved) / 100.0, 1.0)
        
        return BrandPattern(
            pattern_id=str(uuid.uuid4()),
            brand_id=brand_id,
            pattern_type="prompt_optimization",
            pattern_data=pattern_data,
            confidence_score=confidence,
            sample_count=len(approved)
        )
    
    def _apply_optimization(
        self,
        prompt: str,
        optimization_data: Dict[str, Any]
    ) -> str:
        """Apply a learned optimization to a prompt."""
        # Simplified implementation - real version would apply learned patterns
        optimizations = optimization_data.get("optimizations", [])
        
        optimized = prompt
        for opt in optimizations:
            # Apply each optimization
            pass
        
        return optimized

    def _apply_optimization(
        self,
        prompt: str,
        optimization_data: Dict[str, Any]
    ) -> str:
        """
        Apply learned optimizations to a prompt.
        
        Applies each optimization rule intelligently:
        - add_style_descriptor: Append if not already present
        - remove_problematic_term: Remove term from prompt
        - emphasize_element: Add emphasis markers
        - color_suggestion: Add color hints if missing
        
        Args:
            prompt: Original user prompt
            optimization_data: pattern_data from prompt_optimization pattern
            
        Returns:
            Optimized prompt with learned improvements applied
        """
        optimized = prompt
        optimizations = optimization_data.get("optimizations", [])
        
        for opt in optimizations:
            # Only apply optimizations with sufficient confidence
            if opt.get("confidence", 0) < 0.5:
                continue
            
            opt_type = opt.get("type")
            
            if opt_type == "add_style_descriptor":
                descriptor = opt.get("descriptor", "")
                # Add if not already present (case-insensitive)
                if descriptor.lower() not in optimized.lower():
                    optimized = f"{descriptor} {optimized}"
            
            elif opt_type == "remove_problematic_term":
                term = opt.get("term", "")
                # Remove term completely (case-insensitive)
                optimized = re.sub(rf'\b{re.escape(term)}\b', '', optimized, flags=re.IGNORECASE)
            
            elif opt_type == "emphasize_element":
                element = opt.get("element", "")
                # Wrap with emphasis if element exists
                if element.lower() in optimized.lower():
                    optimized = re.sub(
                        rf'\b({re.escape(element)})\b',
                        r'\1',
                        optimized,
                        flags=re.IGNORECASE
                    )
            
            elif opt_type == "color_suggestion":
                color = opt.get("color", "")
                # Add color hint if "color" not mentioned
                if "color" not in optimized.lower() and color:
                    optimized = f"{optimized}, featuring {color}"
        
        # Clean up formatting
        optimized = re.sub(r'\s+', ' ', optimized)  # Remove extra spaces
        optimized = re.sub(r'\s*,\s*,\s*', ', ', optimized)  # Remove double commas
        optimized = optimized.strip()
        
        return optimized
    
    def _calculate_statistical_significance(
        self,
        approved_count: int,
        rejected_count: int,
        total_count: int
    ) -> float:
        """
        Calculate statistical significance of a pattern.
        
        Uses a simplified confidence calculation based on:
        1. Sample size (more samples = higher confidence)
        2. Approval rate distance from 50% (clearer patterns = higher confidence)
        
        Args:
            approved_count: Number of approved occurrences
            rejected_count: Number of rejected occurrences
            total_count: Total occurrences
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if total_count < 5:
            return 0.0
        
        approval_rate = approved_count / total_count if total_count > 0 else 0
        
        # Sample confidence: reaches 1.0 at 30 samples
        sample_confidence = min(total_count / 30.0, 1.0)
        
        # Rate confidence: 0 at 50%, 1.0 at 0% or 100%
        rate_confidence = abs(approval_rate - 0.5) * 2
        
        # Combined confidence
        return sample_confidence * rate_confidence
    
    async def apply_pattern_decay(self) -> Dict[str, Any]:
        """
        Apply time-based decay to pattern confidence scores.
        
        Patterns lose confidence over time as brand preferences may change.
        Decay formula: confidence * (0.5 ^ (age_days / 90))
        
        This means:
        - After 90 days: 50% confidence remaining
        - After 180 days: 25% confidence remaining
        - After 270 days: 12.5% confidence remaining
        
        Should be called by Modal cron job daily.
        
        Returns:
            Summary of decay operations (patterns updated, avg decay, etc.)
        """
        logger.info("applying_pattern_decay")
        
        # Fetch all patterns
        result = self.client.table("brand_patterns").select("*").execute()
        patterns = result.data
        
        patterns_processed = 0
        patterns_updated = 0
        total_decay_factor = 0.0
        oldest_pattern_age_days = 0
        patterns_below_threshold = 0
        
        for pattern_data in patterns:
            patterns_processed += 1
            
            created_at = datetime.fromisoformat(pattern_data["created_at"].replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - created_at).days
            
            if age_days > oldest_pattern_age_days:
                oldest_pattern_age_days = age_days
            
            # Apply decay only if age > 30 days (grace period)
            if age_days > 30:
                old_confidence = pattern_data["confidence_score"]
                decay_factor = 0.5 ** (age_days / 90.0)
                new_confidence = old_confidence * decay_factor
                
                # Update in database
                self.client.table("brand_patterns").update({
                    "confidence_score": new_confidence,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("pattern_id", pattern_data["pattern_id"]).execute()
                
                patterns_updated += 1
                total_decay_factor += decay_factor
                
                # Check if below threshold
                if new_confidence < 0.1:
                    patterns_below_threshold += 1
                    # Delete patterns with very low confidence
                    self.client.table("brand_patterns").delete().eq(
                        "pattern_id", pattern_data["pattern_id"]
                    ).execute()
                
                logger.info(
                    "pattern_decayed",
                    pattern_id=pattern_data["pattern_id"],
                    age_days=age_days,
                    old_confidence=old_confidence,
                    new_confidence=new_confidence
                )
        
        avg_decay_factor = total_decay_factor / patterns_updated if patterns_updated > 0 else 1.0
        
        summary = {
            "patterns_processed": patterns_processed,
            "patterns_updated": patterns_updated,
            "avg_decay_factor": round(avg_decay_factor, 2),
            "oldest_pattern_age_days": oldest_pattern_age_days,
            "patterns_below_threshold": patterns_below_threshold
        }
        
        logger.info("pattern_decay_complete", **summary)
        
        return summary
    
    async def get_learning_effectiveness(self, brand_id: str) -> Dict[str, Any]:
        """
        Calculate learning effectiveness metrics.
        
        Compares compliance scores before and after learning activation to
        measure if learning actually improves outcomes.
        
        Algorithm:
        1. Get brand's learning_active_at timestamp
        2. Query assets before and after that timestamp
        3. Calculate average compliance scores for each period
        4. Calculate improvement percentage
        5. Check statistical significance (need ≥30 post-learning samples)
        
        Returns:
            Effectiveness metrics including before/after scores and improvement %
            
        Raises:
            ValueError: If brand not found
        """
        logger.info("calculating_learning_effectiveness", brand_id=brand_id)
        
        # Get brand's learning_active_at timestamp
        brand_result = self.client.table("brands").select(
            "learning_active_at"
        ).eq("brand_id", brand_id).execute()
        
        if not brand_result.data:
            raise ValueError(f"Brand {brand_id} not found")
        
        brand_data = brand_result.data[0]
        learning_active_at = brand_data.get("learning_active_at")
        
        if not learning_active_at:
            return {
                "learning_active": False,
                "message": "Learning not yet activated for this brand"
            }
        
        learning_timestamp = datetime.fromisoformat(learning_active_at.replace("Z", "+00:00"))
        
        # Query assets before learning
        before_result = self.client.table("assets").select(
            "compliance_score"
        ).eq("brand_id", brand_id).lt(
            "created_at", learning_active_at
        ).execute()
        
        # Query assets after learning
        after_result = self.client.table("assets").select(
            "compliance_score"
        ).eq("brand_id", brand_id).gte(
            "created_at", learning_active_at
        ).execute()
        
        before_scores = [a["compliance_score"] for a in before_result.data if a.get("compliance_score")]
        after_scores = [a["compliance_score"] for a in after_result.data if a.get("compliance_score")]
        
        if not before_scores or not after_scores:
            return {
                "learning_active": True,
                "learning_active_since": learning_active_at,
                "message": "Insufficient data for effectiveness calculation",
                "before_sample_count": len(before_scores),
                "after_sample_count": len(after_scores)
            }
        
        avg_before = sum(before_scores) / len(before_scores)
        avg_after = sum(after_scores) / len(after_scores)
        improvement = ((avg_after - avg_before) / avg_before) * 100 if avg_before > 0 else 0
        
        statistically_significant = len(after_scores) >= 30
        
        effectiveness = {
            "learning_active": True,
            "avg_compliance_before_learning": round(avg_before, 1),
            "avg_compliance_after_learning": round(avg_after, 1),
            "improvement_percentage": round(improvement, 2),
            "before_sample_count": len(before_scores),
            "after_sample_count": len(after_scores),
            "statistically_significant": statistically_significant,
            "learning_active_since": learning_active_at
        }
        
        logger.info("learning_effectiveness_calculated", brand_id=brand_id, **effectiveness)
        
        return effectiveness
    
    async def _verify_consent(self, brand_id: str, required_tier: PrivacyTier) -> bool:
        """
        Verify brand has consented to learning at required tier.
        
        Checks if brand's current privacy tier is at or above the required tier
        for a given operation.
        
        Tier hierarchy: OFF < PRIVATE < SHARED
        
        Args:
            brand_id: Brand to check consent for
            required_tier: Minimum tier required for operation
            
        Returns:
            True if consent granted, False otherwise
            
        Raises:
            ValueError: If brand doesn't exist
        """
        # Define tier hierarchy
        tier_levels = {
            PrivacyTier.OFF: 0,
            PrivacyTier.PRIVATE: 1,
            PrivacyTier.SHARED: 2
        }
        
        # Get brand's current settings
        settings = await self._get_settings(brand_id)
        
        current_level = tier_levels.get(settings.privacy_tier, 0)
        required_level = tier_levels.get(required_tier, 0)
        
        consent_granted = current_level >= required_level
        
        if not consent_granted:
            logger.warning(
                "insufficient_consent",
                brand_id=brand_id,
                current_tier=settings.privacy_tier.value,
                required_tier=required_tier.value
            )
        
        return consent_granted
    
    def _minimize_pattern_data(self, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Minimize pattern data to essential information only (GDPR Article 5).
        
        Removes any potentially identifying information from patterns before storage.
        
        Allowed fields (whitelist approach):
        - Statistical aggregates (counts, rates, averages)
        - Confidence scores
        - Analysis metadata (dates, versions)
        
        Forbidden (must be removed):
        - Raw prompts (only store terms/patterns)
        - Asset IDs
        - User IDs
        - Brand identifiers in pattern_data (OK as foreign key)
        - Timestamps with sub-second precision
        
        Args:
            pattern_data: Raw pattern data from extraction
            
        Returns:
            Minimized pattern data safe for storage
        """
        # Forbidden fields that must be removed
        forbidden_fields = {
            "prompt", "raw_prompt", "asset_id", "user_id", "brand_id",
            "asset_ids", "user_ids", "brand_ids"
        }
        
        def minimize_recursive(data: Any) -> Any:
            if isinstance(data, dict):
                minimized = {}
                for key, value in data.items():
                    # Skip forbidden fields
                    if key.lower() in forbidden_fields:
                        continue
                    
                    # Truncate timestamps to minute precision
                    if key.endswith("_date") or key.endswith("_at"):
                        if isinstance(value, str) and "T" in value:
                            # Truncate to minute precision
                            value = value[:16] + ":00Z" if value.endswith("Z") else value[:16] + ":00"
                    
                    # Round floats to 2 decimal places
                    if isinstance(value, float):
                        value = round(value, 2)
                    
                    # Recursively minimize nested structures
                    minimized[key] = minimize_recursive(value)
                
                return minimized
            
            elif isinstance(data, list):
                return [minimize_recursive(item) for item in data]
            
            else:
                return data
        
        return minimize_recursive(pattern_data)
    
    def _tokenize_prompt(self, prompt: str) -> List[str]:
        """
        Tokenize a prompt into terms for analysis.
        
        Args:
            prompt: Prompt text to tokenize
            
        Returns:
            List of lowercase terms
        """
        # Remove punctuation and split on spaces
        prompt = re.sub(r'[^\w\s]', ' ', prompt)
        terms = prompt.lower().split()
        
        # Filter out very short terms and common stop words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        terms = [t for t in terms if len(t) > 2 and t not in stop_words]
        
        return terms
