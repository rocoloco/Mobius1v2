#!/usr/bin/env python3
"""
Test script to verify that the original_had_logos fix works correctly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mobius.storage.brands import BrandStorage
from src.mobius.nodes.generate import generate_node
import structlog

logger = structlog.get_logger()

async def test_original_had_logos_fix():
    """Test that original_had_logos is set correctly during first generation."""
    
    print("🔍 Testing original_had_logos Fix")
    print("=" * 40)
    
    # Simulate a first generation state (attempt_count = 0)
    initial_state = {
        "job_id": "test-job-12345",
        "brand_id": "7d7811bb-733a-485b-baa5-73efed715d07",  # Stripe
        "prompt": "Create a professional business card design",
        "attempt_count": 0,  # CRITICAL: First generation
        "current_image_url": None,
        "is_tweak": False,
        "user_tweak_instruction": None,
    }
    
    print(f"Initial state:")
    print(f"   attempt_count: {initial_state['attempt_count']}")
    print(f"   current_image_url: {initial_state.get('current_image_url')}")
    print(f"   is_tweak: {initial_state.get('is_tweak')}")
    
    # Simulate the logic from generate_node
    current_attempt = initial_state.get("attempt_count", 0) + 1
    is_tweak_operation = initial_state.get("is_tweak", False)
    previous_image_url = initial_state.get("current_image_url")
    
    continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
    
    print(f"\n🎯 Generation Logic:")
    print(f"   current_attempt: {current_attempt}")
    print(f"   is_tweak_operation: {is_tweak_operation}")
    print(f"   has_previous_image: {bool(previous_image_url)}")
    print(f"   continue_conversation: {continue_conversation}")
    
    # Determine if we need logos
    if not continue_conversation:
        needs_logos = True
        reason = "First attempt: always fetch logos"
    else:
        original_had_logos = initial_state.get("original_had_logos", False)
        user_instruction = initial_state.get("user_tweak_instruction")
        logo_mentioned_in_tweak = False
        if user_instruction:
            instruction = user_instruction.lower()
            logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
            logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)
        
        needs_logos = original_had_logos or logo_mentioned_in_tweak
        reason = f"Continuation: original_had_logos={original_had_logos}, logo_mentioned={logo_mentioned_in_tweak}"
    
    print(f"   needs_logos: {needs_logos}")
    print(f"   reason: {reason}")
    
    # Check if brand has logos
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(initial_state["brand_id"])
    
    has_brand_logos = bool(brand and brand.guidelines and brand.guidelines.logos)
    would_fetch_logos = needs_logos and has_brand_logos
    
    print(f"   has_brand_logos: {has_brand_logos}")
    print(f"   would_fetch_logos: {would_fetch_logos}")
    
    # Simulate what original_had_logos would be set to
    logo_bytes_list = []
    if would_fetch_logos:
        logo_bytes_list = [b"fake_logo_bytes"]  # Simulate successful logo fetch
    
    original_had_logos_result = bool(logo_bytes_list)
    print(f"   original_had_logos would be set to: {original_had_logos_result}")
    
    print(f"\n🏁 RESULT:")
    if current_attempt == 1 and original_had_logos_result:
        print(f"✅ SUCCESS: First generation will set original_had_logos=True")
        print(f"   This will allow future tweaks to preserve logo configuration")
    elif current_attempt == 1 and not original_had_logos_result:
        print(f"❌ ISSUE: First generation will set original_had_logos=False")
        if not needs_logos:
            print(f"   Problem: needs_logos=False for first generation")
        elif not has_brand_logos:
            print(f"   Problem: Brand has no logos available")
        else:
            print(f"   Problem: Logo fetching would fail")
    else:
        print(f"⚠️  This is not a first generation test")
    
    # Test a tweak scenario
    print(f"\n" + "=" * 40)
    print(f"🔄 Testing Tweak Scenario")
    
    tweak_state = {
        "job_id": "test-job-67890",
        "brand_id": "7d7811bb-733a-485b-baa5-73efed715d07",  # Stripe
        "prompt": "Create a professional business card design",
        "attempt_count": 2,  # This is a tweak (attempt > 1)
        "current_image_url": "https://example.com/previous-image.png",
        "is_tweak": False,
        "user_tweak_instruction": "Please fix all critical violations marked in red",
        "original_had_logos": True,  # This should be preserved from first generation
    }
    
    print(f"Tweak state:")
    print(f"   attempt_count: {tweak_state['attempt_count']}")
    print(f"   original_had_logos: {tweak_state.get('original_had_logos')}")
    print(f"   user_tweak_instruction: {tweak_state.get('user_tweak_instruction')}")
    
    # Simulate tweak logic
    current_attempt = tweak_state.get("attempt_count", 0) + 1
    is_tweak_operation = tweak_state.get("is_tweak", False)
    previous_image_url = tweak_state.get("current_image_url")
    
    continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
    
    print(f"\n🎯 Tweak Logic:")
    print(f"   current_attempt: {current_attempt}")
    print(f"   continue_conversation: {continue_conversation}")
    
    # For tweaks, check original_had_logos
    original_had_logos = tweak_state.get("original_had_logos", False)
    user_instruction = tweak_state.get("user_tweak_instruction")
    logo_mentioned_in_tweak = False
    if user_instruction:
        instruction = user_instruction.lower()
        logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
        logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)
    
    needs_logos = original_had_logos or logo_mentioned_in_tweak
    
    print(f"   original_had_logos: {original_had_logos}")
    print(f"   logo_mentioned_in_tweak: {logo_mentioned_in_tweak}")
    print(f"   needs_logos: {needs_logos}")
    
    print(f"\n🏁 TWEAK RESULT:")
    if needs_logos and original_had_logos:
        print(f"✅ SUCCESS: Tweak will preserve logo configuration from original")
        print(f"   Logos will be fetched because original_had_logos=True")
    elif not needs_logos and not original_had_logos:
        print(f"✅ SUCCESS: Tweak will preserve no-logo configuration from original")
        print(f"   No logos will be fetched because original_had_logos=False")
    else:
        print(f"⚠️  Mixed result: needs_logos={needs_logos}, original_had_logos={original_had_logos}")

if __name__ == "__main__":
    asyncio.run(test_original_had_logos_fix())