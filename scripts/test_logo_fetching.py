#!/usr/bin/env python3
"""
Test script to verify logo fetching works correctly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mobius.storage.brands import BrandStorage
from src.mobius.nodes.generate import fetch_and_process_logos_parallel
import structlog

logger = structlog.get_logger()

async def test_logo_fetching():
    """Test if logo fetching works for Stripe brand."""
    
    print("🔍 Testing Logo Fetching for Stripe Brand")
    print("=" * 50)
    
    # Get Stripe brand
    brand_storage = BrandStorage()
    brand_id = "7d7811bb-733a-485b-baa5-73efed715d07"
    brand = await brand_storage.get_brand(brand_id)
    
    if not brand:
        print(f"❌ Brand {brand_id} not found")
        return
    
    print(f"✅ Brand found: {brand.name}")
    print(f"   Has guidelines: {bool(brand.guidelines)}")
    
    if not brand.guidelines:
        print("❌ No guidelines found")
        return
    
    print(f"   Has logos: {bool(brand.guidelines.logos)}")
    
    if not brand.guidelines.logos:
        print("❌ No logos found in guidelines")
        return
    
    print(f"   Logo count: {len(brand.guidelines.logos)}")
    
    for i, logo in enumerate(brand.guidelines.logos, 1):
        print(f"   Logo {i}: {logo.variant_name} - {logo.url}")
    
    # Test logo fetching
    print(f"\n🔄 Testing Logo Fetching...")
    
    try:
        logo_bytes_list = await fetch_and_process_logos_parallel(
            brand.guidelines.logos,
            job_id="test-job",
            operation_type="test_logo_fetching"
        )
        
        print(f"✅ Logo fetching completed")
        print(f"   Logos fetched: {len(logo_bytes_list)}")
        print(f"   Success rate: {len(logo_bytes_list)}/{len(brand.guidelines.logos)}")
        
        for i, logo_bytes in enumerate(logo_bytes_list, 1):
            print(f"   Logo {i}: {len(logo_bytes)} bytes")
        
        # Test the boolean conversion
        original_had_logos = bool(logo_bytes_list)
        print(f"   original_had_logos would be: {original_had_logos}")
        
        if not logo_bytes_list:
            print("❌ ISSUE: No logos were successfully fetched!")
            print("   This explains why original_had_logos is False")
        else:
            print("✅ Logo fetching works correctly")
            
    except Exception as e:
        print(f"❌ Logo fetching failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_logo_fetching())