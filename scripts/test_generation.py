#!/usr/bin/env python3
"""
Test image generation after deployment.

Usage:
    python scripts/test_generation.py <brand_id> <prompt>
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mobius.api.routes import generate_handler
from mobius.models.generation import GenerateRequest
import structlog

logger = structlog.get_logger()


async def test_generation(brand_id: str, prompt: str):
    """Test image generation for a brand."""
    
    print(f"\n🎨 Testing Image Generation")
    print(f"   Brand ID: {brand_id}")
    print(f"   Prompt: {prompt}")
    print()
    
    # Create generation request
    request = GenerateRequest(
        brand_id=brand_id,
        prompt=prompt,
        async_mode=False  # Synchronous for testing
    )
    
    try:
        # Call generation handler
        print("⏳ Generating image...")
        response = await generate_handler(request)
        
        print(f"\n✅ Generation Complete!")
        print(f"   Job ID: {response.job_id}")
        print(f"   Status: {response.status}")
        
        if response.result:
            print(f"\n📊 Results:")
            print(f"   Image URI: {response.result.image_uri[:100]}...")
            print(f"   Approved: {response.result.approved}")
            print(f"   Score: {response.result.score}")
            print(f"   Attempts: {response.result.attempt_count}")
            
            if response.result.audit_result:
                print(f"\n🔍 Audit Details:")
                audit = response.result.audit_result
                print(f"   Overall Score: {audit.overall_score}")
                print(f"   Approved: {audit.approved}")
                
                print(f"\n   Category Scores:")
                for category in audit.category_details:
                    status = "✅" if category.passed else "❌"
                    print(f"   {status} {category.category}: {category.score}")
                    
                    if category.violations:
                        print(f"      Violations:")
                        for violation in category.violations:
                            print(f"      - [{violation.severity}] {violation.description}")
                
                print(f"\n   Summary: {audit.summary}")
            
            # Check for specific issues
            print(f"\n🔎 Issue Checks:")
            
            # We can't check the actual image content here, but we can check audit results
            logo_usage_passed = False
            has_text_violations = False
            has_distortion_violations = False
            
            if response.result.audit_result:
                for category in response.result.audit_result.category_details:
                    if category.category == "logo_usage":
                        logo_usage_passed = category.passed
                        for violation in category.violations:
                            if "distort" in violation.description.lower():
                                has_distortion_violations = True
                    
                    if category.category == "typography":
                        for violation in category.violations:
                            if "text" in violation.description.lower():
                                has_text_violations = True
            
            print(f"   Logo Usage Passed: {'✅' if logo_usage_passed else '❌'}")
            print(f"   No Distortion Issues: {'✅' if not has_distortion_violations else '❌'}")
            print(f"   No Text Issues: {'✅' if not has_text_violations else '❌'}")
            
            if not logo_usage_passed:
                print(f"\n   ⚠️  Logo usage did not pass - check violations above")
            if has_distortion_violations:
                print(f"   ⚠️  Logo distortion detected - check violations above")
            if has_text_violations:
                print(f"   ⚠️  Text issues detected - check violations above")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Generation Failed!")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_generation.py <brand_id> <prompt>")
        print()
        print("Example:")
        print('  python scripts/test_generation.py 9f5e7f7b-3d8f-4423-b3c1-698b718e37ab "a professional photo of a woman drinking from a water bottle"')
        sys.exit(1)
    
    brand_id = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    success = asyncio.run(test_generation(brand_id, prompt))
    sys.exit(0 if success else 1)
