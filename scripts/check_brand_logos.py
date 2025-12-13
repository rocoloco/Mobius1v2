#!/usr/bin/env python3
"""
Quick script to check if a specific brand has logos in the database.
This will help verify if the issue is with logo availability or the fix logic.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mobius.storage.brands import BrandStorage


async def check_brand_logos(brand_id: str):
    """Check if a brand has logos available."""
    
    print(f"🔍 Checking brand logos for: {brand_id}")
    print("=" * 50)
    
    try:
        brand_storage = BrandStorage()
        brand = await brand_storage.get_brand(brand_id)
        
        if not brand:
            print(f"❌ Brand not found: {brand_id}")
            return False
        
        print(f"✅ Brand found: {brand.name}")
        print(f"   Brand ID: {brand.brand_id}")
        print(f"   Organization: {brand.organization_id}")
        
        if not brand.guidelines:
            print(f"❌ No guidelines found for brand")
            return False
        
        print(f"✅ Guidelines found")
        
        if not brand.guidelines.logos:
            print(f"❌ No logos found in guidelines")
            return False
        
        print(f"✅ Logos found: {len(brand.guidelines.logos)}")
        
        for i, logo in enumerate(brand.guidelines.logos):
            print(f"   Logo {i+1}:")
            print(f"     Variant: {logo.variant_name}")
            print(f"     URL: {logo.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking brand: {e}")
        return False


async def list_all_brands():
    """List all brands to help identify which one to test."""
    
    print(f"📋 Listing all brands...")
    print("=" * 30)
    
    try:
        brand_storage = BrandStorage()
        # Use default organization ID
        organization_id = "00000000-0000-0000-0000-000000000000"
        brands = await brand_storage.list_brands(organization_id=organization_id)
        
        if not brands:
            print("❌ No brands found")
            return
        
        print(f"Found {len(brands)} brands:")
        for brand in brands:
            has_logos = bool(brand.guidelines and brand.guidelines.logos)
            logo_count = len(brand.guidelines.logos) if has_logos else 0
            
            print(f"  • {brand.name} ({brand.brand_id})")
            print(f"    Logos: {logo_count} {'✅' if has_logos else '❌'}")
        
    except Exception as e:
        print(f"❌ Error listing brands: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        brand_id = sys.argv[1]
        result = asyncio.run(check_brand_logos(brand_id))
        sys.exit(0 if result else 1)
    else:
        print("Usage: python scripts/check_brand_logos.py <brand_id>")
        print("Or run without arguments to list all brands:")
        print("")
        asyncio.run(list_all_brands())