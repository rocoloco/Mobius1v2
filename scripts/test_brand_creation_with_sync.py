"""Test brand creation with Neo4j sync to verify the await fix works."""

import asyncio
from mobius.storage.brands import BrandStorage
from mobius.storage.graph import graph_storage
from mobius.models.brand import Brand, BrandGuidelines, Color
from datetime import datetime, timezone
import uuid


async def test_brand_sync():
    """Create a test brand and verify it syncs to Neo4j."""
    
    print("Testing brand creation with Neo4j sync...")
    print("=" * 60)
    
    # Create a test brand
    brand_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    brand = Brand(
        brand_id=brand_id,
        organization_id="00000000-0000-0000-0000-000000000000",
        name="Test Sync Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(
                    hex="#FF0000",
                    name="Red",
                    usage="primary",
                    usage_weight=0.5,
                    context="Main brand color"
                ),
                Color(
                    hex="#0000FF",
                    name="Blue",
                    usage="secondary",
                    usage_weight=0.3,
                    context="Accent color"
                ),
            ]
        ),
        created_at=now,
        updated_at=now
    )
    
    print(f"\n1. Creating brand: {brand.name}")
    print(f"   ID: {brand_id}")
    print(f"   Colors: {len(brand.guidelines.colors)}")
    
    # Create brand (this should sync to Neo4j with await)
    storage = BrandStorage()
    created_brand = await storage.create_brand(brand)
    
    print(f"   ✓ Brand created in Supabase")
    
    # Wait a moment for any async operations
    await asyncio.sleep(1)
    
    # Verify in Neo4j
    print(f"\n2. Verifying Neo4j sync...")
    
    if not graph_storage._is_enabled():
        print("   ❌ Neo4j is not enabled")
        return
    
    async with graph_storage.driver.session() as session:
        # Check if brand exists
        result = await session.run(
            "MATCH (b:Brand {brand_id: $brand_id}) RETURN b",
            brand_id=brand_id
        )
        brand_record = await result.single()
        
        if brand_record:
            print(f"   ✓ Brand found in Neo4j")
            
            # Check colors
            result = await session.run(
                """
                MATCH (b:Brand {brand_id: $brand_id})-[r:OWNS_COLOR]->(c:Color)
                RETURN c.hex as hex, c.name as name, r.usage as usage
                """,
                brand_id=brand_id
            )
            
            colors = [dict(record) async for record in result]
            print(f"   ✓ Found {len(colors)} colors in Neo4j:")
            for color in colors:
                print(f"      - {color['name']}: {color['hex']} ({color['usage']})")
            
            if len(colors) == len(brand.guidelines.colors):
                print(f"\n✅ SUCCESS! Brand and colors synced correctly to Neo4j")
            else:
                print(f"\n⚠️  Color count mismatch: Expected {len(brand.guidelines.colors)}, got {len(colors)}")
        else:
            print(f"   ❌ Brand NOT found in Neo4j")
            print(f"   This means the sync failed or didn't complete")
    
    # Cleanup
    print(f"\n3. Cleaning up test brand...")
    await storage.delete_brand(brand_id)
    
    async with graph_storage.driver.session() as session:
        await session.run(
            "MATCH (b:Brand {brand_id: $brand_id}) DETACH DELETE b",
            brand_id=brand_id
        )
    
    print(f"   ✓ Test brand deleted")


if __name__ == "__main__":
    asyncio.run(test_brand_sync())
