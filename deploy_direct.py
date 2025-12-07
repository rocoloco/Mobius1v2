#!/usr/bin/env python3
"""Deploy directly using Modal Python SDK."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and deploy the app
from mobius.api.app_consolidated import app

if __name__ == "__main__":
    print("Deploying Mobius to Modal...")
    print("App name:", app.name)
    print("\nNote: Run 'modal deploy src/mobius/api/app_consolidated.py' manually")
    print("Or use the Modal web dashboard to redeploy")
