"""Re-sync existing brands to Neo4j with full MOAT structure."""

import asyncio
from mobius.storage.brands import BrandStorage
from mobius.storage.graph import graph_storage


async def resync_all_brands():
    """Re-sync all brands from Supabase to Neo4j with new MOAT structure."""
    
    print("Re-syncing brands to Neo4j with MOAT structure...")
    print("=" * 60)
    
    # Get all brands from Supabase
    storage = BrandStorage()
    brands = await storage.list_brands(
        organization_id="00000000-0000-0000-0000-000000000000",
        limit=100
    )
    
    if not brands:
        print("No brands found in Supabase")
        return
    
    print(f"\nFound {len(brands)} brands in Supabase:")
    for brand in brands:
        print(f"  • {brand.name} ({brand.brand_id})")
    
    print(f"\nRe-syncing to Neo4j...")
    
    for i, brand in enumerate(brands, 1):
        print(f"\n{i}. Syncing: {brand.name}")
        
        try:
            # Sync to Neo4j (this will use the new MOAT sync logic)
            await graph_storage.sync_brand(brand)
            
            # Verify what was synced
            if brand.guidelines:
                print(f"   ✓ Colors: {len(brand.guidelines.colors) if brand.guidelines.colors else 0}")
                print(f"   ✓ Typography: {len(brand.guidelines.typography) if brand.guidelines.typography else 0}")
                print(f"   ✓ Rules: {len(brand.guidelines.rules) if brand.guidelines.rules else 0}")
                print(f"   ✓ Contextual Rules: {len(brand.guidelines.contextual_rules) if brand.guidelines.contextual_rules else 0}")
                
                if brand.guidelines.identity_core:
                    print(f"   ✓ Identity Core:")
                    print(f"      - Archetype: {brand.guidelines.identity_core.archetype or 'None'}")
                    print(f"      - Voice Vectors: {len(brand.guidelines.identity_core.voice_vectors)}")
                    print(f"      - Negative Constraints: {len(brand.guidelines.identity_core.negative_constraints)}")
                else:
                    print(f"   ⚠️  No Identity Core")
                
                if brand.guidelines.asset_graph:
                    print(f"   ✓ Asset Graph:")
                    print(f"      - Logos: {len(brand.guidelines.asset_graph.logos)}")
                    print(f"      - Templates: {len(brand.guidelines.asset_graph.templates)}")
                    print(f"      - Patterns: {len(brand.guidelines.asset_graph.patterns)}")
                else:
                    print(f"   ⚠️  No Asset Graph")
            else:
                print(f"   ⚠️  No guidelines")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n✅ Re-sync complete!")
    print(f"\nRun 'python scripts/inspect_neo4j_graph.py' to verify.")


if __name__ == "__main__":
    asyncio.run(resync_all_brands())
