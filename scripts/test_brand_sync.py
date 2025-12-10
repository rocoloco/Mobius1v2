"""Test brand sync to Neo4j to reproduce the routing error."""

import asyncio
from mobius.storage.brands import BrandStorage
from mobius.storage.graph import graph_storage
import structlog

logger = structlog.get_logger()


async def test_sync():
    """Test syncing the Stripe brand to Neo4j."""
    
    # Get the Stripe brand that was just created
    brand_id = "d111ddff-ba45-4236-a999-0b4a1d5eaee5"
    
    print(f"Fetching brand {brand_id}...")
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    
    if not brand:
        print(f"✗ Brand not found: {brand_id}")
        return
    
    print(f"✓ Brand found: {brand.name}")
    print(f"  Colors: {len(brand.guidelines.colors) if brand.guidelines else 0}")
    
    print("\nAttempting to sync to Neo4j...")
    try:
        await graph_storage.sync_brand(brand)
        print("✓ Sync completed successfully!")
        
        # Verify the sync by querying
        print("\nVerifying sync...")
        colors = await graph_storage.get_brand_colors(brand_id)
        print(f"✓ Found {len(colors)} colors in graph database")
        for color in colors:
            print(f"  - {color['name']}: {color['hex']} ({color['usage']})")
            
    except Exception as e:
        print(f"✗ Sync failed: {type(e).__name__}")
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sync())
