#!/usr/bin/env python3
"""
Test script for visual brand scraper.

This script tests the visual scraper against a list of known brands
to validate extraction quality.

Usage:
    python scripts/test_visual_scraper.py
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import modal
except ImportError:
    print("❌ Modal not installed. Run: pip install modal")
    sys.exit(1)


# Test URLs with expected characteristics
TEST_CASES = [
    {
        "url": "https://stripe.com",
        "expected_archetype": "The Sage",  # Technical expertise, developer-focused
        "expected_primary_color": "purple/blue",
    },
    {
        "url": "https://nike.com",
        "expected_archetype": "The Hero",  # Achievement, performance
        "expected_primary_color": "black/white",
    },
    {
        "url": "https://apple.com",
        "expected_archetype": "The Magician",  # Innovation, transformation
        "expected_primary_color": "black/white/gray",
    },
    {
        "url": "https://patagonia.com",
        "expected_archetype": "The Explorer",  # Adventure, outdoors
        "expected_primary_color": "earth tones",
    },
]


def test_visual_scraper():
    """Run visual scraper tests."""
    print("\n" + "="*60)
    print("VISUAL BRAND SCRAPER - TEST SUITE")
    print("="*60 + "\n")
    
    # Import the Modal function
    try:
        from mobius.ingestion.visual_scraper import analyze_brand_visuals
    except ImportError:
        print("❌ Could not import visual_scraper module")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        url = test_case["url"]
        print(f"\n[{i}/{len(TEST_CASES)}] Testing: {url}")
        print("-" * 60)
        
        try:
            # Run the scraper
            result = analyze_brand_visuals.remote(url)
            
            # Check for errors
            if "error" in result:
                print(f"❌ FAILED: {result['error']}")
                results.append({
                    "url": url,
                    "status": "error",
                    "error": result["error"],
                })
                continue
            
            # Extract key metrics
            archetype = result.get("identity_core", {}).get("archetype", "Unknown")
            confidence = result.get("confidence", 0.0)
            color_count = len(result.get("colors", []))
            
            # Display results
            print(f"✅ SUCCESS")
            print(f"   Archetype: {archetype}")
            print(f"   Expected:  {test_case['expected_archetype']}")
            print(f"   Confidence: {confidence:.1%}")
            print(f"   Colors extracted: {color_count}")
            
            # Show color palette
            if result.get("colors"):
                print(f"   Color palette:")
                for color in result["colors"][:5]:  # Show first 5
                    print(f"     • {color['name']} ({color['hex']}) - {color['usage']}")
            
            # Show voice vectors
            voice = result.get("identity_core", {}).get("voice_vectors", {})
            if voice:
                print(f"   Voice profile:")
                for dimension, score in voice.items():
                    print(f"     • {dimension}: {score:.2f}")
            
            results.append({
                "url": url,
                "status": "success",
                "archetype": archetype,
                "confidence": confidence,
                "color_count": color_count,
            })
            
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                "url": url,
                "status": "exception",
                "error": str(e),
            })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    total_count = len(results)
    
    print(f"Passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_count - success_count} test(s) failed")
    
    # Save results
    output_file = Path(__file__).parent.parent / "visual_scraper_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    try:
        test_visual_scraper()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
