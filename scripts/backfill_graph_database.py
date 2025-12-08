"""
Backfill existing PostgreSQL data into Neo4j graph database.

Usage:
    python scripts/backfill_graph_database.py --dry-run
    python scripts/backfill_graph_database.py --execute
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mobius.storage.brands import BrandStorage
from mobius.storage.graph import graph_storage
import structlog

logger = structlog.get_logger()


async def backfill_brands(dry_run: bool = True):
    """Backfill all brands and their colors."""
    brand_storage = BrandStorage()

    # Get all brands (no organization filter for backfill)
    # We'll need to query Supabase directly for all brands
    from mobius.storage.database import get_supabase_client

    client = get_supabase_client()
    result = client.table("brands").select("*").is_("deleted_at", "null").execute()

    brands_data = result.data
    logger.info("backfill_brands_start", count=len(brands_data))

    from mobius.models.brand import Brand

    for brand_data in brands_data:
        brand = Brand.model_validate(brand_data)

        if dry_run:
            logger.info(
                "dry_run_would_sync_brand",
                brand_id=brand.brand_id,
                brand_name=brand.name,
                color_count=len(brand.guidelines.colors) if brand.guidelines else 0,
            )
        else:
            await graph_storage.sync_brand(brand)
            logger.info(
                "brand_synced",
                brand_id=brand.brand_id,
                brand_name=brand.name,
                color_count=len(brand.guidelines.colors) if brand.guidelines else 0,
            )

    logger.info("backfill_brands_complete", count=len(brands_data))


async def backfill_assets(dry_run: bool = True):
    """Backfill all assets."""
    from mobius.storage.database import get_supabase_client
    from mobius.models.asset import Asset

    client = get_supabase_client()
    result = client.table("assets").select("*").execute()

    assets_data = result.data
    logger.info("backfill_assets_start", count=len(assets_data))

    for asset_data in assets_data:
        asset = Asset.model_validate(asset_data)

        if dry_run:
            logger.info(
                "dry_run_would_sync_asset",
                asset_id=asset.asset_id,
                brand_id=asset.brand_id,
            )
        else:
            await graph_storage.sync_asset(asset)
            logger.info("asset_synced", asset_id=asset.asset_id, brand_id=asset.brand_id)

    logger.info("backfill_assets_complete", count=len(assets_data))


async def backfill_feedback(dry_run: bool = True):
    """Backfill all feedback."""
    from mobius.storage.database import get_supabase_client
    from mobius.storage.feedback import Feedback

    client = get_supabase_client()
    result = client.table("feedback").select("*").execute()

    feedback_data = result.data
    logger.info("backfill_feedback_start", count=len(feedback_data))

    for fb_data in feedback_data:
        feedback = Feedback.model_validate(fb_data)

        if dry_run:
            logger.info(
                "dry_run_would_sync_feedback",
                feedback_id=feedback.feedback_id,
                asset_id=feedback.asset_id,
                action=feedback.action,
            )
        else:
            await graph_storage.sync_feedback(
                feedback_id=feedback.feedback_id,
                asset_id=feedback.asset_id,
                brand_id=feedback.brand_id,
                action=feedback.action,
                reason=feedback.reason,
                timestamp=feedback.created_at.isoformat(),
            )
            logger.info(
                "feedback_synced",
                feedback_id=feedback.feedback_id,
                asset_id=feedback.asset_id,
            )

    logger.info("backfill_feedback_complete", count=len(feedback_data))


async def backfill_templates(dry_run: bool = True):
    """Backfill all templates."""
    from mobius.storage.database import get_supabase_client
    from mobius.models.template import Template

    client = get_supabase_client()
    result = client.table("templates").select("*").is_("deleted_at", "null").execute()

    templates_data = result.data
    logger.info("backfill_templates_start", count=len(templates_data))

    for template_data in templates_data:
        template = Template.model_validate(template_data)

        if dry_run:
            logger.info(
                "dry_run_would_sync_template",
                template_id=template.template_id,
                brand_id=template.brand_id,
                name=template.name,
            )
        else:
            await graph_storage.sync_template(template)
            logger.info(
                "template_synced",
                template_id=template.template_id,
                brand_id=template.brand_id,
            )

    logger.info("backfill_templates_complete", count=len(templates_data))


async def main():
    parser = argparse.ArgumentParser(description="Backfill graph database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")
    parser.add_argument("--execute", action="store_true", help="Actually sync data")
    parser.add_argument(
        "--only",
        choices=["brands", "assets", "feedback", "templates"],
        help="Only backfill specific entity type",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Must specify --dry-run or --execute")
        return

    dry_run = args.dry_run

    logger.info("backfill_start", dry_run=dry_run, only=args.only)

    try:
        if args.only == "brands" or not args.only:
            await backfill_brands(dry_run)

        if args.only == "assets" or not args.only:
            await backfill_assets(dry_run)

        if args.only == "feedback" or not args.only:
            await backfill_feedback(dry_run)

        if args.only == "templates" or not args.only:
            await backfill_templates(dry_run)

        await graph_storage.close()

        logger.info("backfill_complete")

    except Exception as e:
        logger.error("backfill_failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
