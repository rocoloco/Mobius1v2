#!/usr/bin/env python3
"""
Diagnostic script to analyze a real job and understand why logos are not being preserved.

This script will help identify the exact issue in your specific case.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mobius.storage.jobs import JobStorage
from mobius.storage.brands import BrandStorage


async def diagnose_job(job_id: str):
    """Diagnose a specific job to understand the logo preservation issue."""
    
    print(f"🔍 Diagnosing Job: {job_id}")
    print("=" * 60)
    
    try:
        # Load the job
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        
        if not job:
            print(f"❌ Job not found: {job_id}")
            return False
        
        print(f"✅ Job found:")
        print(f"   Status: {job.status}")
        print(f"   Brand ID: {job.brand_id}")
        print(f"   Created: {job.created_at}")
        print(f"   Progress: {job.progress}%")
        
        # Analyze job state
        state = job.state or {}
        print(f"\n📊 Job State Analysis:")
        print(f"   State keys: {list(state.keys())}")
        
        key_fields = [
            "attempt_count",
            "user_decision", 
            "user_tweak_instruction",
            "is_tweak",
            "original_had_logos",
            "current_image_url",
            "session_id"
        ]
        
        for field in key_fields:
            value = state.get(field)
            if field == "current_image_url" and value:
                display_value = value[:50] + "..." if len(str(value)) > 50 else value
            else:
                display_value = value
            print(f"   {field}: {display_value}")
        
        # Check the brand
        print(f"\n🏢 Brand Analysis:")
        brand_storage = BrandStorage()
        brand = await brand_storage.get_brand(job.brand_id)
        
        if not brand:
            print(f"❌ Brand not found: {job.brand_id}")
            return False
        
        print(f"✅ Brand found: {brand.name}")
        
        has_guidelines = bool(brand.guidelines)
        has_logos = bool(brand.guidelines and brand.guidelines.logos)
        logo_count = len(brand.guidelines.logos) if has_logos else 0
        
        print(f"   Has guidelines: {has_guidelines}")
        print(f"   Has logos: {has_logos}")
        print(f"   Logo count: {logo_count}")
        
        if has_logos:
            for i, logo in enumerate(brand.guidelines.logos):
                print(f"   Logo {i+1}: {logo.variant_name} - {logo.url}")
        
        # Simulate the logo detection logic
        print(f"\n🎯 Logo Detection Logic Simulation:")
        
        current_attempt = state.get("attempt_count", 0) + 1
        is_tweak_operation = state.get("is_tweak", False)
        previous_image_url = state.get("current_image_url")
        
        continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
        
        print(f"   current_attempt: {current_attempt}")
        print(f"   is_tweak_operation: {is_tweak_operation}")
        print(f"   has_previous_image: {bool(previous_image_url)}")
        print(f"   continue_conversation: {continue_conversation}")
        
        # Apply the fixed logic
        needs_logos = False
        if not continue_conversation:
            needs_logos = True
            reason = "First attempt - always fetch logos"
        else:
            original_had_logos = state.get("original_had_logos", False)
            user_instruction = state.get("user_tweak_instruction")
            logo_mentioned_in_tweak = False
            
            if user_instruction:
                instruction = user_instruction.lower()
                logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
                logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)
            
            needs_logos = original_had_logos or logo_mentioned_in_tweak
            reason = f"Tweak: original_had_logos={original_had_logos}, logo_mentioned={logo_mentioned_in_tweak}"
        
        print(f"   needs_logos: {needs_logos}")
        print(f"   reason: {reason}")
        
        # Final verdict
        print(f"\n🏁 DIAGNOSIS:")
        
        if not has_logos:
            print(f"❌ ROOT CAUSE: Brand has no logos!")
            print(f"   The brand '{brand.name}' doesn't have any logo assets.")
            print(f"   This would result in has_logo=False regardless of the fix.")
            return False
        
        if not continue_conversation and has_logos:
            print(f"✅ EXPECTED: First attempt should fetch logos")
            print(f"   This should result in has_logo=True")
            return True
        
        if continue_conversation and not state.get("original_had_logos"):
            if state.get("original_had_logos") is None:
                print(f"⚠️  ISSUE: original_had_logos flag is missing!")
                print(f"   This suggests the flag wasn't set during first generation.")
                print(f"   OR the job state wasn't properly updated.")
            else:
                print(f"⚠️  ISSUE: original_had_logos is False!")
                print(f"   This suggests the first generation didn't have logos.")
            
            if logo_mentioned_in_tweak:
                print(f"✅ RECOVERY: User mentioned logo in tweak, so logos will be fetched")
                return True
            else:
                print(f"❌ RESULT: No logos will be fetched for this tweak")
                return False
        
        if continue_conversation and state.get("original_had_logos"):
            print(f"✅ EXPECTED: Tweak should preserve logos")
            print(f"   This should result in has_logo=True")
            return True
        
        print(f"❓ UNCLEAR: Unexpected state combination")
        return False
        
    except Exception as e:
        print(f"❌ Error diagnosing job: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/diagnose_real_job.py <job_id>")
        print("")
        print("This script will analyze a specific job to understand")
        print("why the logo preservation might not be working.")
        sys.exit(1)
    
    job_id = sys.argv[1]
    result = asyncio.run(diagnose_job(job_id))
    
    if result:
        print(f"\n✅ Diagnosis complete - no issues found with the fix")
    else:
        print(f"\n❌ Diagnosis complete - issue identified")
    
    sys.exit(0 if result else 1)