"""Verify if brands were synced to Neo4j."""

import asyncio
from mobius.storage.graph import graph_storage
from mobius.storage.brands import BrandStorage


async def check_neo4j_brands():
    """Check what brands exist in Neo4j."""
    
    print("Checking Neo4j for synced brands...")
    print("=" * 60)
    
    if not graph_storage._is_enabled():
        print("❌ Neo4j is not enabled or configured")
        return
    
    try:
        async with graph_storage.driver.session() as session:
            # Count brands
            result = await session.run("MATCH (b:Brand) RETURN count(b) as count")
            record = await result.single()
            brand_count = record["count"]
            
            print(f"\n✓ Neo4j connected")
            print(f"✓ Found {brand_count} brands in graph database\n")
            
            if brand_count > 0:
                # List all brands
                result = await session.run("""
                    MATCH (b:Brand)
                    OPTIONAL MATCH (b)-[r:OWNS_COLOR]->(c:Color)
                    RETURN b.brand_id as brand_id, 
                           b.name as name, 
                           b.created_at as created_at,
                           count(c) as color_count
                    ORDER BY b.created_at DESC
                """)
                
                print("Brands in Neo4j:")
                print("-" * 60)
                async for record in result:
                    print(f"  • {record['name']}")
                    print(f"    ID: {record['brand_id']}")
                    print(f"    Colors: {record['color_count']}")
                    print(f"    Created: {record['created_at']}")
                    print()
            
            # Now check Supabase
            print("\nChecking Supabase for comparison...")
            print("-" * 60)
            brand_storage = BrandStorage()
            brands = await brand_storage.list_brands(
                organization_id="00000000-0000-0000-0000-000000000000",
                limit=100
            )
            
            print(f"✓ Found {len(brands)} brands in Supabase\n")
            
            # Compare
            if len(brands) != brand_count:
                print(f"⚠️  MISMATCH: Supabase has {len(brands)} brands but Neo4j has {brand_count}")
                print("   Some brands may not have synced properly.\n")
                
                # Show which brands are missing
                async with graph_storage.driver.session() as session:
                    result = await session.run("MATCH (b:Brand) RETURN b.brand_id as brand_id")
                    neo4j_ids = {record["brand_id"] async for record in result}
                
                supabase_ids = {b.brand_id for b in brands}
                missing_in_neo4j = supabase_ids - neo4j_ids
                
                if missing_in_neo4j:
                    print("Brands in Supabase but NOT in Neo4j:")
                    for brand in brands:
                        if brand.brand_id in missing_in_neo4j:
                            print(f"  ❌ {brand.name} ({brand.brand_id})")
            else:
                print("✅ Supabase and Neo4j are in sync!")
                
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_neo4j_brands())
