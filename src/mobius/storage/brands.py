"""
Brand storage operations.

Provides CRUD operations for brand entities in Supabase.
"""

from mobius.models.brand import Brand
from mobius.storage.database import get_supabase_client
from mobius.storage.graph import graph_storage
from typing import List, Optional
from datetime import datetime, timezone
import asyncio
import structlog

logger = structlog.get_logger()


class BrandStorage:
    """Storage operations for brand entities."""

    def __init__(self):
        self.client = get_supabase_client()

    async def create_brand(self, brand: Brand) -> Brand:
        """
        Create a new brand in the database.

        Args:
            brand: Brand entity to create

        Returns:
            Brand: Created brand with database-generated fields

        Raises:
            Exception: If database operation fails
        """
        logger.info("creating_brand", brand_id=brand.brand_id, name=brand.name)

        # Exclude None values and fields not in database schema
        data = brand.model_dump(exclude_none=True, exclude={'website'})
        result = self.client.table("brands").insert(data).execute()

        logger.info("brand_created", brand_id=brand.brand_id)
        created_brand = Brand.model_validate(result.data[0])

        # Sync to Neo4j graph database (fully async, non-blocking)
        asyncio.create_task(graph_storage.sync_brand(created_brand))

        return created_brand

    async def get_brand(self, brand_id: str) -> Optional[Brand]:
        """
        Retrieve a brand by ID.

        Args:
            brand_id: UUID of the brand

        Returns:
            Brand if found, None otherwise
        """
        logger.debug("fetching_brand", brand_id=brand_id)

        result = (
            self.client.table("brands")
            .select("*")
            .eq("brand_id", brand_id)
            .is_("deleted_at", "null")
            .execute()
        )

        if result.data:
            return Brand.model_validate(result.data[0])
        return None

    async def list_brands(
        self, organization_id: str, search: Optional[str] = None, limit: int = 100
    ) -> List[Brand]:
        """
        List all brands for an organization.

        Args:
            organization_id: UUID of the organization
            search: Optional search term for brand name
            limit: Maximum number of brands to return

        Returns:
            List of Brand entities
        """
        logger.debug(
            "listing_brands", organization_id=organization_id, search=search, limit=limit
        )

        query = (
            self.client.table("brands")
            .select("*")
            .eq("organization_id", organization_id)
            .is_("deleted_at", "null")
        )

        if search:
            query = query.ilike("name", f"%{search}%")

        result = query.limit(limit).execute()

        return [Brand.model_validate(b) for b in result.data]

    async def update_brand(self, brand_id: str, updates: dict) -> Brand:
        """
        Update brand fields.

        Args:
            brand_id: UUID of the brand
            updates: Dictionary of fields to update

        Returns:
            Updated Brand entity

        Raises:
            Exception: If brand not found or update fails
        """
        logger.info("updating_brand", brand_id=brand_id, fields=list(updates.keys()))

        # Add updated_at timestamp
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("brands")
            .update(updates)
            .eq("brand_id", brand_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Brand {brand_id} not found")

        logger.info("brand_updated", brand_id=brand_id)
        updated_brand = Brand.model_validate(result.data[0])

        # Sync to Neo4j graph database (fully async, non-blocking)
        asyncio.create_task(graph_storage.sync_brand(updated_brand))

        return updated_brand

    async def delete_brand(self, brand_id: str) -> bool:
        """
        Soft delete a brand.

        Sets deleted_at timestamp instead of removing the record.
        Associated assets remain accessible for audit purposes.

        Args:
            brand_id: UUID of the brand

        Returns:
            True if successful

        Raises:
            Exception: If brand not found or delete fails
        """
        logger.info("soft_deleting_brand", brand_id=brand_id)

        result = (
            self.client.table("brands")
            .update({"deleted_at": datetime.now(timezone.utc).isoformat()})
            .eq("brand_id", brand_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Brand {brand_id} not found")

        logger.info("brand_soft_deleted", brand_id=brand_id)
        return True

    async def get_brand_with_stats(self, brand_id: str) -> Optional[dict]:
        """
        Get brand with computed statistics.

        Returns brand data with asset_count and avg_compliance_score.

        Args:
            brand_id: UUID of the brand

        Returns:
            Dictionary with brand data and statistics, or None if not found
        """
        logger.debug("fetching_brand_with_stats", brand_id=brand_id)

        # Get brand
        brand = await self.get_brand(brand_id)
        if not brand:
            return None

        # Get asset count and average compliance score
        assets_result = (
            self.client.table("assets")
            .select("compliance_score")
            .eq("brand_id", brand_id)
            .execute()
        )

        asset_count = len(assets_result.data)
        avg_score = 0.0
        if asset_count > 0:
            scores = [
                a["compliance_score"]
                for a in assets_result.data
                if a.get("compliance_score") is not None
            ]
            avg_score = sum(scores) / len(scores) if scores else 0.0

        return {
            **brand.model_dump(),
            "asset_count": asset_count,
            "avg_compliance_score": avg_score,
        }
