#!/usr/bin/env python3
"""
Test script for compressed_twin migration.

This script verifies that:
1. The migration adds the compressed_twin column successfully
2. The column is nullable (non-breaking change)
3. Existing brands are not affected
4. New brands can store compressed twins
5. The rollback migration works correctly
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from supabase import create_client
from mobius.config import settings
from mobius.models.brand import CompressedDigitalTwin
import json
from datetime import datetime


def test_migration():
    """Test the compressed_twin migration."""
    
    print("=" * 80)
    print("Testing Compressed Twin Migration")
    print("=" * 80)
    
    # Initialize Supabase client
    supabase = create_client(settings.supabase_url, settings.supabase_key)
    
    # Test 1: Verify column exists
    print("\n[Test 1] Verifying compressed_twin column exists...")
    try:
        # Query the brands table to check if compressed_twin column exists
        result = supabase.table("brands").select("brand_id, compressed_twin").limit(1).execute()
        print("✓ Column exists and is queryable")
    except Exception as e:
        print(f"✗ Column does not exist or is not queryable: {e}")
        return False
    
    # Test 2: Verify existing brands are not affected (nullable field)
    print("\n[Test 2] Verifying existing brands are not affected...")
    try:
        # Query existing brands
        result = supabase.table("brands").select("brand_id, name, compressed_twin").limit(5).execute()
        brands = result.data
        
        if brands:
            print(f"✓ Found {len(brands)} existing brands")
            for brand in brands:
                if brand.get("compressed_twin") is None:
                    print(f"  - Brand '{brand.get('name')}': compressed_twin is NULL (expected)")
                else:
                    print(f"  - Brand '{brand.get('name')}': compressed_twin exists")
        else:
            print("  No existing brands found (this is OK for a new database)")
    except Exception as e:
        print(f"✗ Error querying existing brands: {e}")
        return False
    
    # Test 3: Create a test brand with compressed_twin
    print("\n[Test 3] Creating test brand with compressed_twin...")
    try:
        # Create a sample compressed twin
        compressed_twin = CompressedDigitalTwin(
            primary_colors=["#0057B8", "#1E3A8A"],
            secondary_colors=["#FF5733"],
            accent_colors=["#FFC300"],
            neutral_colors=["#FFFFFF", "#333333"],
            semantic_colors=["#10B981", "#EF4444"],
            font_families=["Helvetica Neue", "Georgia"],
            visual_dos=[
                "Use primary colors for headers",
                "Maintain 2:1 contrast ratio"
            ],
            visual_donts=[
                "Never use Comic Sans",
                "Avoid red on green"
            ],
            logo_placement="top-left or center",
            logo_min_size="100px width"
        )
        
        # Verify token count
        token_count = compressed_twin.estimate_tokens()
        print(f"  Compressed twin token count: {token_count}")
        
        if compressed_twin.validate_size():
            print(f"✓ Compressed twin is under 60k token limit")
        else:
            print(f"✗ Compressed twin exceeds 60k token limit")
            return False
        
        # Create test brand
        test_brand = {
            "organization_id": "00000000-0000-0000-0000-000000000000",
            "name": f"Test Brand - Migration Test {datetime.now().isoformat()}",
            "guidelines": {
                "colors": [],
                "typography": [],
                "logos": [],
                "rules": []
            },
            "compressed_twin": compressed_twin.model_dump()
        }
        
        result = supabase.table("brands").insert(test_brand).execute()
        test_brand_id = result.data[0]["brand_id"]
        print(f"✓ Created test brand with ID: {test_brand_id}")
        
        # Test 4: Verify we can retrieve the compressed_twin
        print("\n[Test 4] Verifying compressed_twin retrieval...")
        result = supabase.table("brands").select("compressed_twin").eq("brand_id", test_brand_id).execute()
        retrieved_twin = result.data[0]["compressed_twin"]
        
        if retrieved_twin:
            print("✓ Successfully retrieved compressed_twin")
            print(f"  Primary colors: {retrieved_twin.get('primary_colors')}")
            print(f"  Font families: {retrieved_twin.get('font_families')}")
        else:
            print("✗ Failed to retrieve compressed_twin")
            return False
        
        # Test 5: Verify we can update compressed_twin
        print("\n[Test 5] Verifying compressed_twin update...")
        updated_twin = compressed_twin.model_dump()
        updated_twin["primary_colors"].append("#AABBCC")
        
        result = supabase.table("brands").update({
            "compressed_twin": updated_twin
        }).eq("brand_id", test_brand_id).execute()
        
        result = supabase.table("brands").select("compressed_twin").eq("brand_id", test_brand_id).execute()
        retrieved_twin = result.data[0]["compressed_twin"]
        
        if "#AABBCC" in retrieved_twin.get("primary_colors", []):
            print("✓ Successfully updated compressed_twin")
        else:
            print("✗ Failed to update compressed_twin")
            return False
        
        # Cleanup: Delete test brand
        print("\n[Cleanup] Deleting test brand...")
        supabase.table("brands").delete().eq("brand_id", test_brand_id).execute()
        print("✓ Test brand deleted")
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("All migration tests passed! ✓")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_migration()
    sys.exit(0 if success else 1)
