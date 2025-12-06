"""
Asset storage operations.

Provides CRUD operations for asset entities in Supabase.
"""

from mobius.models.asset import Asset
from mobius.storage.database import get_supabase_client
from typing import List, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


class AssetStorage:
    """Storage operations for asset entities."""

    def __init__(self):
        self.client = get_supabase_client()

    async def create_asset(self, asset: Asset) -> Asset:
        """
        Create a new asset in the database.

        Args:
            asset: Asset entity to create

        Returns:
            Asset: Created asset with database-generated fields

        Raises:
            Exception: If database operation fails
        """
        logger.info("creating_asset", asset_id=asset.asset_id, brand_id=asset.brand_id)

        data = asset.model_dump()
        result = self.client.table("assets").insert(data).execute()

        logger.info("asset_created", asset_id=asset.asset_id)
        return Asset.model_validate(result.data[0])

    async def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        Retrieve an asset by ID.

        Args:
            asset_id: UUID of the asset

        Returns:
            Asset if found, None otherwise
        """
        logger.debug("fetching_asset", asset_id=asset_id)

        result = (
            self.client.table("assets")
            .select("*")
            .eq("asset_id", asset_id)
            .execute()
        )

        if result.data:
            return Asset.model_validate(result.data[0])
        return None

    async def list_assets(
        self, brand_id: str, limit: int = 100, offset: int = 0
    ) -> List[Asset]:
        """
        List all assets for a brand.

        Args:
            brand_id: UUID of the brand
            limit: Maximum number of assets to return
            offset: Number of assets to skip

        Returns:
            List of Asset entities
        """
        logger.debug("listing_assets", brand_id=brand_id, limit=limit, offset=offset)

        result = (
            self.client.table("assets")
            .select("*")
            .eq("brand_id", brand_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return [Asset.model_validate(a) for a in result.data]

    async def list_assets_by_job(self, job_id: str) -> List[Asset]:
        """
        List all assets for a job.

        Args:
            job_id: UUID of the job

        Returns:
            List of Asset entities
        """
        logger.debug("listing_assets_by_job", job_id=job_id)

        result = (
            self.client.table("assets")
            .select("*")
            .eq("job_id", job_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [Asset.model_validate(a) for a in result.data]

    async def update_asset(self, asset_id: str, updates: dict) -> Asset:
        """
        Update asset fields.

        Args:
            asset_id: UUID of the asset
            updates: Dictionary of fields to update

        Returns:
            Updated Asset entity

        Raises:
            Exception: If asset not found or update fails
        """
        logger.info("updating_asset", asset_id=asset_id, fields=list(updates.keys()))

        # Add updated_at timestamp
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("assets")
            .update(updates)
            .eq("asset_id", asset_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Asset {asset_id} not found")

        logger.info("asset_updated", asset_id=asset_id)
        return Asset.model_validate(result.data[0])

    async def delete_asset(self, asset_id: str) -> bool:
        """
        Delete an asset.

        Hard delete - removes the record from the database.

        Args:
            asset_id: UUID of the asset

        Returns:
            True if successful

        Raises:
            Exception: If asset not found or delete fails
        """
        logger.info("deleting_asset", asset_id=asset_id)

        result = (
            self.client.table("assets")
            .delete()
            .eq("asset_id", asset_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Asset {asset_id} not found")

        logger.info("asset_deleted", asset_id=asset_id)
        return True
