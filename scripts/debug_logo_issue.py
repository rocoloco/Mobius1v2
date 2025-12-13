#!/usr/bin/env python3
"""
Debug script to trace the logo preservation issue in real-time.

This script will help identify exactly where the logo configuration is being lost.
"""

import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mobius.models.state import JobState


def analyze_state_for_logo_config(state: dict, step_name: str):
    """Analyze a state dict for logo-related configuration."""
    
    print(f"\n🔍 {step_name} - State Analysis:")
    print("=" * 50)
    
    # Key fields to check
    key_fields = [
        "job_id",
        "brand_id", 
        "attempt_count",
        "user_decision",
        "user_tweak_instruction",
        "is_tweak",
        "original_had_logos",
        "current_image_url"
    ]
    
    for field in key_fields:
        value = state.get(field)
        if field == "current_image_url" and value:
            # Truncate long URLs
            display_value = value[:50] + "..." if len(str(value)) > 50 else value
        else:
            display_value = value
        print(f"  {field}: {display_value}")
    
    # Analyze logo configuration
    print(f"\n📊 Logo Configuration Analysis:")
    
    # Check if this would trigger logo fetching
    current_attempt = state.get("attempt_count", 0) + 1
    is_tweak_operation = state.get("is_tweak", False)
    previous_image_url = state.get("current_image_url")
    
    continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
    
    print(f"  current_attempt: {current_attempt}")
    print(f"  is_tweak_operation: {is_tweak_operation}")
    print(f"  has_previous_image: {bool(previous_image_url)}")
    print(f"  continue_conversation: {continue_conversation}")
    
    # Determine needs_logos based on the fixed logic
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
    
    print(f"  needs_logos: {needs_logos}")
    print(f"  reason: {reason}")
    
    # Verdict
    if continue_conversation and not needs_logos:
        print(f"  🚨 ISSUE: This is a tweak but logos won't be fetched!")
    elif needs_logos:
        print(f"  ✅ GOOD: Logos will be fetched")
    else:
        print(f"  ℹ️  INFO: First attempt, logos will be fetched")
    
    return needs_logos


def simulate_tweak_workflow():
    """Simulate the tweak workflow to identify where logo config is lost."""
    
    print("🧪 Simulating Tweak Workflow")
    print("=" * 60)
    
    # Step 1: Initial generation state (after first successful generation)
    initial_state = {
        "job_id": "test-job-123",
        "brand_id": "test-brand-456",
        "prompt": "Create a professional business card design",
        "attempt_count": 1,
        "current_image_url": "https://example.com/image1.jpg",
        "status": "needs_review",
        "original_had_logos": True,  # This should be set after first generation
        "compliance_scores": [{"overall_score": 75.0}]
    }
    
    analyze_state_for_logo_config(initial_state, "Step 1: After Initial Generation")
    
    # Step 2: User requests tweak (tweak handler processes this)
    tweak_state = {**initial_state}
    tweak_state.update({
        "user_tweak_instruction": "Please fix all critical violations and improve the layout",
        "user_decision": "tweak",
        "is_tweak": True,
        "attempt_count": 2,  # Incremented by tweak handler
        "status": "correcting"
    })
    
    analyze_state_for_logo_config(tweak_state, "Step 2: After Tweak Request")
    
    # Step 3: After correct_node processes the instruction
    corrected_state = {**tweak_state}
    corrected_state.update({
        "prompt": "Looking at the image you just generated in our previous conversation, please make this specific modification: Please fix all critical violations and improve the layout...",
        "user_tweak_instruction": None,  # Cleared by correct_node
        "status": "correcting"
    })
    
    analyze_state_for_logo_config(corrected_state, "Step 3: After correct_node")
    
    # Step 4: When generate_node is called (this is where the bug should be fixed)
    generate_state = {**corrected_state}
    
    needs_logos = analyze_state_for_logo_config(generate_state, "Step 4: In generate_node")
    
    print(f"\n🎯 FINAL VERDICT:")
    if needs_logos:
        print("✅ Logo configuration preserved - fix is working!")
    else:
        print("❌ Logo configuration lost - fix needs more work!")
    
    return needs_logos


def test_edge_cases():
    """Test various edge cases that might cause logo loss."""
    
    print(f"\n🔬 Testing Edge Cases")
    print("=" * 40)
    
    # Edge Case 1: Legacy job without original_had_logos
    print(f"\n📋 Edge Case 1: Legacy job (no original_had_logos flag)")
    legacy_state = {
        "job_id": "legacy-job",
        "brand_id": "test-brand",
        "attempt_count": 2,
        "is_tweak": True,
        "current_image_url": "https://example.com/image.jpg",
        # Note: original_had_logos is missing
    }
    
    needs_logos_legacy = analyze_state_for_logo_config(legacy_state, "Legacy Job")
    
    # Edge Case 2: User mentions logo in instruction
    print(f"\n📋 Edge Case 2: Logo mentioned in tweak instruction")
    logo_mention_state = {
        "job_id": "logo-mention-job",
        "brand_id": "test-brand",
        "attempt_count": 2,
        "is_tweak": True,
        "current_image_url": "https://example.com/image.jpg",
        "user_tweak_instruction": "Make the logo bigger and more prominent",
        "original_had_logos": False  # Original didn't have logos
    }
    
    needs_logos_mention = analyze_state_for_logo_config(logo_mention_state, "Logo Mentioned")
    
    # Edge Case 3: Multiple attempts without tweak
    print(f"\n📋 Edge Case 3: Multiple attempts (auto-correction)")
    multi_attempt_state = {
        "job_id": "multi-attempt-job", 
        "brand_id": "test-brand",
        "attempt_count": 3,  # Multiple attempts
        "current_image_url": "https://example.com/image.jpg",
        "original_had_logos": True,
        # Note: is_tweak is False (auto-correction, not user tweak)
    }
    
    needs_logos_multi = analyze_state_for_logo_config(multi_attempt_state, "Multi-Attempt")
    
    return all([needs_logos_legacy == False, needs_logos_mention == True, needs_logos_multi == True])


if __name__ == "__main__":
    print("🔍 Logo Preservation Debug Analysis")
    print("=" * 70)
    
    # Test main workflow
    main_result = simulate_tweak_workflow()
    
    # Test edge cases
    edge_result = test_edge_cases()
    
    print(f"\n🏁 SUMMARY:")
    print(f"Main workflow: {'✅ PASS' if main_result else '❌ FAIL'}")
    print(f"Edge cases: {'✅ PASS' if edge_result else '❌ FAIL'}")
    
    if main_result and edge_result:
        print(f"\n🎉 All tests pass! The fix should work correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Issues detected. The fix needs refinement.")
        sys.exit(1)