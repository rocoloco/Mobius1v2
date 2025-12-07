#!/usr/bin/env python3
"""
Fix logo URLs in existing brands.

This script updates brands where logo_thumbnail_url is set but guidelines.logos[].url is empty.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mobius.storage.brands import BrandStorage
from mobius.models.brand import LogoRule
import structlog

logger = structlog.get_logger()


async def fix_logo_urls(organization_id: str = None):
    """Fix logo URLs in all brands."""
    storage = BrandStorage()
    
    # Get all brands for the organization (or all if no org specified)
    if organization_id:
        brands = await storage.list_brands(organization_id=organization_id, limit=1000)
    else:
        # Get all brands across all organizations
        # We need to query the database directly
        from mobius.storage.database import get_supabase_client
        from mobius.models.brand import Brand
        supabase = get_supabase_client()
        result = supabase.table("brands").select("*").limit(1000).execute()
        brands = [Brand.model_validate(b) for b in result.data]
    
    fixed_count = 0
    skipped_count = 0
    
    for brand in brands:
        needs_fix = False
        
        # Check if brand has logo_thumbnail_url but empty logo URLs in guidelines
        if brand.logo_thumbnail_url:
            if brand.guidelines and brand.guidelines.logos:
                # Check if any logo has empty URL
                for logo in brand.guidelines.logos:
                    if not logo.url or logo.url == "":
                        logo.url = brand.logo_thumbnail_url
                        needs_fix = True
                        logger.info(
                            "logo_url_fixed",
                            brand_id=brand.brand_id,
                            brand_name=brand.name,
                            logo_variant=logo.variant_name,
                            logo_url=brand.logo_thumbnail_url
                        )
            elif brand.guidelines:
                # No logos in guidelines, create a default one
                default_logo = LogoRule(
                    variant_name="Primary Logo",
                    url=brand.logo_thumbnail_url,
                    min_width_px=150,
                    clear_space_ratio=0.1,
                    forbidden_backgrounds=["#FFFFFF", "#000000"]
                )
                brand.guidelines.logos.append(default_logo)
                needs_fix = True
                logger.info(
                    "default_logo_created",
                    brand_id=brand.brand_id,
                    brand_name=brand.name,
                    logo_url=brand.logo_thumbnail_url
                )
        
        if needs_fix:
            # Update the brand in database
            try:
                await storage.update_brand(
                    brand.brand_id,
                    {"guidelines": brand.guidelines.model_dump()}
                )
                fixed_count += 1
                logger.info(
                    "brand_updated",
                    brand_id=brand.brand_id,
                    brand_name=brand.name
                )
            except Exception as e:
                logger.error(
                    "brand_update_failed",
                    brand_id=brand.brand_id,
                    brand_name=brand.name,
                    error=str(e)
                )
        else:
            skipped_count += 1
    
    logger.info(
        "fix_complete",
        total_brands=len(brands),
        fixed_count=fixed_count,
        skipped_count=skipped_count
    )
    
    return fixed_count


if __name__ == "__main__":
    import sys
    
    org_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if org_id:
        print(f"🔧 Fixing logo URLs for organization {org_id}...")
    else:
        print("🔧 Fixing logo URLs in all brands...")
    
    fixed = asyncio.run(fix_logo_urls(org_id))
    print(f"✅ Fixed {fixed} brands")
