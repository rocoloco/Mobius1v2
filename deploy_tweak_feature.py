#!/usr/bin/env python3
"""
Deploy the multi-turn tweak feature to Modal.

This script deploys the updated Mobius API with the new tweak endpoint.
"""

import subprocess
import sys

def main():
    print("🚀 Deploying Mobius with Multi-Turn Tweak Feature...")
    print()
    
    try:
        # Deploy to Modal
        print("📦 Deploying to Modal...")
        result = subprocess.run(
            ["modal", "deploy", "src/mobius/api/app.py"],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print()
            print("✅ Deployment successful!")
            print()
            print("New endpoint available:")
            print("  POST /v1/jobs/{job_id}/tweak")
            print()
            print("Test the tweak feature:")
            print("  1. Generate an image")
            print("  2. Click 'Tweak' button in dashboard")
            print("  3. Enter refinement instruction")
            print("  4. Watch multi-turn magic happen! ✨")
            return 0
        else:
            print("❌ Deployment failed")
            print(result.stderr)
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print("❌ Modal CLI not found. Install with: pip install modal")
        return 1

if __name__ == "__main__":
    sys.exit(main())
