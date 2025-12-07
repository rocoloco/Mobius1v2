#!/usr/bin/env python3
"""
Verify logo URLs for a specific brand.

Usage:
    python scripts/verify_logo_urls.py <brand_id>
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mobius.storage.brands import BrandStorage
import structlog

logger = structlog.get_logger()


async def verify_brand_logos(brand_id: str):
    """Verify logo URLs for a specific brand."""
    storage = BrandStorage()
    
    # Get the brand
    brand = await storage.get_brand(brand_id)
    
    if not brand:
        print(f"❌ Brand {brand_id} not found")
        return False
    
    print(f"\n📋 Brand: {brand.name}")
    print(f"   ID: {brand.brand_id}")
    print(f"   Organization: {brand.organization_id}")
    print()
    
    # Check logo_thumbnail_url
    print(f"🖼️  Logo Thumbnail URL: {brand.logo_thumbnail_url or '(not set)'}")
    print()
    
    # Check guidelines.logos
    if brand.guidelines and brand.guidelines.logos:
        print(f"📝 Guidelines Logos ({len(brand.guidelines.logos)}):")
        for i, logo in enumerate(brand.guidelines.logos, 1):
            print(f"   {i}. {logo.variant_name}")
            print(f"      URL: {logo.url or '(empty)'}")
            print(f"      Min Width: {logo.min_width_px}px")
            print(f"      Clear Space Ratio: {logo.clear_space_ratio}")
            
            # Check if URL is valid
            if not logo.url or logo.url == "":
                print(f"      ⚠️  WARNING: Logo URL is empty!")
            elif not logo.url.startswith(("http://", "https://")):
                print(f"      ⚠️  WARNING: Logo URL is invalid (missing protocol)!")
            else:
                print(f"      ✅ Logo URL looks valid")
            print()
    else:
        print("📝 Guidelines Logos: (none)")
        if brand.logo_thumbnail_url:
            print("   ⚠️  WARNING: Brand has logo_thumbnail_url but no logos in guidelines!")
        print()
    
    # Summary
    has_issue = False
    if brand.logo_thumbnail_url:
        if not brand.guidelines or not brand.guidelines.logos:
            print("❌ ISSUE: Brand has logo_thumbnail_url but no logos in guidelines")
            has_issue = True
        else:
            for logo in brand.guidelines.logos:
                if not logo.url or logo.url == "":
                    print(f"❌ ISSUE: Logo '{logo.variant_name}' has empty URL")
                    has_issue = True
    
    if not has_issue:
        print("✅ No logo URL issues detected")
    else:
        print()
        print("💡 Run 'python scripts/fix_logo_urls.py' to fix this issue")
    
    return not has_issue


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_logo_urls.py <brand_id>")
        sys.exit(1)
    
    brand_id = sys.argv[1]
    is_valid = asyncio.run(verify_brand_logos(brand_id))
    sys.exit(0 if is_valid else 1)
