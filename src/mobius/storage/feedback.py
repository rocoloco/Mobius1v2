"""
Feedback storage operations.

Provides CRUD operations for feedback entities in Supabase.
"""

from pydantic import BaseModel
from mobius.storage.database import get_supabase_client
from mobius.storage.graph import graph_storage
from typing import List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class Feedback(BaseModel):
    """Feedback entity model."""

    feedback_id: str
    asset_id: str
    brand_id: str
    action: str  # 'approve' or 'reject'
    reason: Optional[str] = None
    created_at: datetime


class FeedbackStorage:
    """Storage operations for feedback entities."""

    def __init__(self):
        self.client = get_supabase_client()

    async def create_feedback(
        self, asset_id: str, brand_id: str, action: str, reason: Optional[str] = None
    ) -> Feedback:
        """
        Create a new feedback entry.

        The database trigger will automatically update the brand's
        feedback_count and learning_active flag.

        Args:
            asset_id: UUID of the asset
            brand_id: UUID of the brand
            action: 'approve' or 'reject'
            reason: Optional reason for rejection

        Returns:
            Feedback: Created feedback entity

        Raises:
            Exception: If database operation fails
        """
        logger.info(
            "creating_feedback",
            asset_id=asset_id,
            brand_id=brand_id,
            action=action,
        )

        data = {
            "asset_id": asset_id,
            "brand_id": brand_id,
            "action": action,
            "reason": reason,
        }

        result = self.client.table("feedback").insert(data).execute()

        logger.info("feedback_created", feedback_id=result.data[0]["feedback_id"])
        created_feedback = Feedback.model_validate(result.data[0])

        # Sync to Neo4j graph database (awaited to prevent connection cleanup race conditions)
        # Graph sync is designed to fail gracefully and won't raise exceptions
        await graph_storage.sync_feedback(
            feedback_id=created_feedback.feedback_id,
            asset_id=asset_id,
            brand_id=brand_id,
            action=action,
            reason=reason,
            timestamp=created_feedback.created_at.isoformat()
        )

        return created_feedback

    async def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """
        Retrieve a feedback entry by ID.

        Args:
            feedback_id: UUID of the feedback

        Returns:
            Feedback if found, None otherwise
        """
        logger.debug("fetching_feedback", feedback_id=feedback_id)

        result = (
            self.client.table("feedback")
            .select("*")
            .eq("feedback_id", feedback_id)
            .execute()
        )

        if result.data:
            return Feedback.model_validate(result.data[0])
        return None

    async def list_feedback_by_brand(
        self, brand_id: str, limit: int = 100, offset: int = 0
    ) -> List[Feedback]:
        """
        List all feedback for a brand.

        Args:
            brand_id: UUID of the brand
            limit: Maximum number of feedback entries to return
            offset: Number of entries to skip

        Returns:
            List of Feedback entities
        """
        logger.debug("listing_feedback_by_brand", brand_id=brand_id, limit=limit)

        result = (
            self.client.table("feedback")
            .select("*")
            .eq("brand_id", brand_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return [Feedback.model_validate(f) for f in result.data]

    async def list_feedback_by_asset(self, asset_id: str) -> List[Feedback]:
        """
        List all feedback for an asset.

        Args:
            asset_id: UUID of the asset

        Returns:
            List of Feedback entities
        """
        logger.debug("listing_feedback_by_asset", asset_id=asset_id)

        result = (
            self.client.table("feedback")
            .select("*")
            .eq("asset_id", asset_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [Feedback.model_validate(f) for f in result.data]

    async def get_feedback_stats(self, brand_id: str) -> dict:
        """
        Get feedback statistics for a brand.

        Returns total approvals, rejections, and learning_active status.

        Args:
            brand_id: UUID of the brand

        Returns:
            Dictionary with feedback statistics
        """
        logger.debug("fetching_feedback_stats", brand_id=brand_id)

        # Get all feedback for the brand
        result = (
            self.client.table("feedback")
            .select("action")
            .eq("brand_id", brand_id)
            .execute()
        )

        approvals = sum(1 for f in result.data if f["action"] == "approve")
        rejections = sum(1 for f in result.data if f["action"] == "reject")
        total = len(result.data)

        # Get learning_active status from brand
        brand_result = (
            self.client.table("brands")
            .select("learning_active")
            .eq("brand_id", brand_id)
            .execute()
        )

        learning_active = (
            brand_result.data[0]["learning_active"] if brand_result.data else False
        )

        return {
            "total_feedback": total,
            "approvals": approvals,
            "rejections": rejections,
            "learning_active": learning_active,
        }
