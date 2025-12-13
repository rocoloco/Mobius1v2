#!/usr/bin/env python3
"""
Debug script to understand why original_had_logos isn't being set on first generation.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mobius.storage.jobs import JobStorage
from src.mobius.storage.brands import BrandStorage
import structlog

logger = structlog.get_logger()

async def debug_first_generation_issue(job_id: str):
    """Debug why original_had_logos isn't set on first generation."""
    
    print(f"🔍 Debugging First Generation Issue: {job_id}")
    print("=" * 60)
    
    # Get job details
    job_storage = JobStorage()
    job = await job_storage.get_job(job_id)
    
    if not job:
        print(f"❌ Job {job_id} not found")
        return
    
    print(f"✅ Job found:")
    print(f"   Status: {job.status}")
    print(f"   Brand ID: {job.brand_id}")
    print(f"   Created: {job.created_at}")
    print(f"   Progress: {job.progress}")
    
    # Get job state
    state = job.state
    print(f"\n📊 Job State Analysis:")
    print(f"   State keys: {list(state.keys())}")
    for key in ['attempt_count', 'original_had_logos', 'is_tweak', 'user_tweak_instruction']:
        value = state.get(key)
        print(f"   {key}: {value}")
    
    # Get brand details
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(job.brand_id)
    
    print(f"\n🏢 Brand Analysis:")
    if brand:
        print(f"✅ Brand found: {brand.name}")
        print(f"   Has guidelines: {bool(brand.guidelines)}")
        if brand.guidelines:
            print(f"   Has logos: {bool(brand.guidelines.logos)}")
            if brand.guidelines.logos:
                print(f"   Logo count: {len(brand.guidelines.logos)}")
                for i, logo in enumerate(brand.guidelines.logos, 1):
                    print(f"   Logo {i}: {logo.variant_name} - {logo.url}")
    else:
        print(f"❌ Brand not found")
        return
    
    # Simulate the logic from generate_node
    print(f"\n🎯 First Generation Logic Simulation:")
    
    current_attempt = state.get("attempt_count", 0) + 1
    is_tweak_operation = state.get("is_tweak", False)
    previous_image_url = state.get("current_image_url")
    
    continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
    
    print(f"   current_attempt: {current_attempt}")
    print(f"   is_tweak_operation: {is_tweak_operation}")
    print(f"   has_previous_image: {bool(previous_image_url)}")
    print(f"   continue_conversation: {continue_conversation}")
    
    # Determine if we need logos
    if not continue_conversation:
        needs_logos = True
        reason = "First attempt: always fetch logos"
    else:
        original_had_logos = state.get("original_had_logos", False)
        user_instruction = state.get("user_tweak_instruction")
        logo_mentioned_in_tweak = False
        if user_instruction:
            instruction = user_instruction.lower()
            logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
            logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)
        
        needs_logos = original_had_logos or logo_mentioned_in_tweak
        reason = f"Continuation: original_had_logos={original_had_logos}, logo_mentioned={logo_mentioned_in_tweak}"
    
    print(f"   needs_logos: {needs_logos}")
    print(f"   reason: {reason}")
    
    # Check if logos would actually be fetched
    would_fetch_logos = needs_logos and brand.guidelines and brand.guidelines.logos
    print(f"   would_fetch_logos: {would_fetch_logos}")
    
    if needs_logos and not would_fetch_logos:
        if not brand.guidelines:
            print(f"   ⚠️  ISSUE: Brand has no guidelines!")
        elif not brand.guidelines.logos:
            print(f"   ⚠️  ISSUE: Brand guidelines have no logos!")
    
    # What would original_had_logos be set to?
    logo_bytes_list = []  # Simulate empty list if logos not fetched
    if would_fetch_logos:
        logo_bytes_list = [b"fake_logo_bytes"]  # Simulate successful logo fetch
    
    original_had_logos_result = bool(logo_bytes_list)
    print(f"   original_had_logos would be set to: {original_had_logos_result}")
    
    print(f"\n🏁 DIAGNOSIS:")
    if current_attempt == 1 and not original_had_logos_result and would_fetch_logos:
        print(f"⚠️  ISSUE: First generation should set original_had_logos=True but won't!")
        print(f"   This suggests logo fetching is failing silently.")
    elif current_attempt == 1 and not would_fetch_logos:
        print(f"⚠️  ISSUE: First generation won't fetch logos!")
        print(f"   Brand has logos but logic prevents fetching.")
    elif current_attempt > 1 and state.get("original_had_logos") is None:
        print(f"⚠️  ISSUE: original_had_logos was never set in first generation!")
        print(f"   This is the root cause - first generation failed to set the flag.")
    else:
        print(f"✅ Logic appears correct for this attempt.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/debug_first_generation.py <job_id>")
        print("\nThis script will analyze why original_had_logos isn't being set properly.")
        sys.exit(1)
    
    job_id = sys.argv[1]
    asyncio.run(debug_first_generation_issue(job_id))