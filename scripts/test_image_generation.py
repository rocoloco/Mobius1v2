#!/usr/bin/env python3
"""
Quick test script to verify image generation is working and images reach the frontend.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import httpx
import json
import time

async def test_image_generation():
    """Test the image generation API endpoint."""
    
    # Test brand ID (replace with your actual brand ID)
    brand_id = "7d7811bb-733a-485b-baa5-73efed715d07"
    
    # API base URL (adjust if needed)
    base_url = "http://localhost:8000"  # Adjust if your API runs on different port
    
    print("🧪 Testing Image Generation API...")
    print(f"   Brand ID: {brand_id}")
    print(f"   API URL: {base_url}")
    print()
    
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
        try:
            # Step 1: Submit generation request
            print("📤 Submitting generation request...")
            
            generation_payload = {
                "prompt": "Create a simple professional logo design with our brand colors",
                "async": True  # Use async mode
            }
            
            response = await client.post(
                f"{base_url}/v1/generate",
                json=generation_payload,
                params={"brand_id": brand_id}
            )
            
            if response.status_code != 200:
                print(f"❌ Generation request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
            
            result = response.json()
            job_id = result.get("job_id")
            
            if not job_id:
                print(f"❌ No job_id in response: {result}")
                return
            
            print(f"✅ Generation request submitted successfully")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {result.get('status')}")
            print()
            
            # Step 2: Poll for completion
            print("🔄 Polling for completion...")
            
            max_polls = 60  # 5 minutes with 5-second intervals
            poll_interval = 5
            
            for attempt in range(max_polls):
                print(f"   Poll {attempt + 1}/{max_polls}...")
                
                status_response = await client.get(f"{base_url}/v1/jobs/{job_id}")
                
                if status_response.status_code != 200:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                current_status = status_data.get("status")
                progress = status_data.get("progress", 0)
                image_url = status_data.get("current_image_url")
                
                print(f"   Status: {current_status}, Progress: {progress}%")
                
                if image_url:
                    print(f"   🖼️  Image URL: {image_url[:100]}...")
                
                # Check for completion
                if current_status in ["completed", "failed", "needs_review"]:
                    print()
                    if current_status == "completed":
                        print("🎉 Generation completed successfully!")
                        if image_url:
                            print(f"   ✅ Image available at: {image_url}")
                            
                            # Test image accessibility
                            try:
                                img_response = await client.head(image_url)
                                if img_response.status_code == 200:
                                    print(f"   ✅ Image is accessible (HTTP {img_response.status_code})")
                                else:
                                    print(f"   ⚠️  Image may not be accessible (HTTP {img_response.status_code})")
                            except Exception as e:
                                print(f"   ⚠️  Could not verify image accessibility: {e}")
                        else:
                            print("   ⚠️  No image URL in completed job")
                            
                    elif current_status == "failed":
                        print("❌ Generation failed")
                        error = status_data.get("error")
                        if error:
                            print(f"   Error: {error}")
                            
                    elif current_status == "needs_review":
                        print("⏸️  Generation needs review")
                        compliance_score = status_data.get("compliance_score")
                        if compliance_score:
                            print(f"   Compliance Score: {compliance_score}%")
                    
                    return
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
            
            print("⏰ Polling timed out - generation may still be in progress")
            print(f"   Final status: {current_status}")
            
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    print("🚀 Image Generation Test")
    print("=" * 50)
    
    try:
        asyncio.run(test_image_generation())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()