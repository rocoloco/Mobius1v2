"""Inspect what's actually in the Neo4j graph."""

import asyncio
from mobius.storage.graph import graph_storage


async def inspect_graph():
    """Show all nodes and relationships in Neo4j."""
    
    print("Inspecting Neo4j Graph...")
    print("=" * 60)
    
    if not graph_storage._is_enabled():
        print("❌ Neo4j is not enabled")
        return
    
    async with graph_storage.driver.session() as session:
        # Count all nodes by label
        print("\n1. Node Counts by Label:")
        print("-" * 60)
        result = await session.run("""
            MATCH (n)
            RETURN labels(n)[0] as label, count(*) as count
            ORDER BY count DESC
        """)
        
        total_nodes = 0
        async for record in result:
            label = record['label']
            count = record['count']
            total_nodes += count
            print(f"   {label:20} {count:5} nodes")
        
        print(f"\n   {'TOTAL':20} {total_nodes:5} nodes")
        
        # Show all brands
        print("\n2. Brands in Graph:")
        print("-" * 60)
        result = await session.run("""
            MATCH (b:Brand)
            RETURN b.brand_id as brand_id, b.name as name
            ORDER BY b.created_at DESC
        """)
        
        brands = []
        async for record in result:
            brands.append(record)
            print(f"   • {record['name']}")
            print(f"     ID: {record['brand_id']}")
        
        if not brands:
            print("   (No brands found)")
        
        # For each brand, show what's connected
        for brand in brands:
            brand_id = brand['brand_id']
            brand_name = brand['name']
            
            print(f"\n3. Relationships for '{brand_name}':")
            print("-" * 60)
            
            # Count relationships by type
            result = await session.run("""
                MATCH (b:Brand {brand_id: $brand_id})-[r]->(n)
                RETURN type(r) as rel_type, labels(n)[0] as target_label, count(*) as count
                ORDER BY count DESC
            """, brand_id=brand_id)
            
            has_relationships = False
            async for record in result:
                has_relationships = True
                rel_type = record['rel_type']
                target = record['target_label']
                count = record['count']
                print(f"   {rel_type:30} → {target:20} ({count})")
            
            if not has_relationships:
                print("   (No relationships found)")
        
        # Show orphaned nodes (not connected to any brand)
        print("\n4. Orphaned Nodes (not connected to brands):")
        print("-" * 60)
        result = await session.run("""
            MATCH (n)
            WHERE NOT (n:Brand) AND NOT (:Brand)-[]->(n)
            RETURN labels(n)[0] as label, count(*) as count
            ORDER BY count DESC
        """)
        
        has_orphans = False
        async for record in result:
            has_orphans = True
            print(f"   {record['label']:20} {record['count']:5} nodes")
        
        if not has_orphans:
            print("   (No orphaned nodes)")
        
        # Show sample Rule nodes (since you see 5 of them)
        print("\n5. Sample Rule Nodes:")
        print("-" * 60)
        result = await session.run("""
            MATCH (r:Rule)
            RETURN r.rule_id as rule_id, r.category as category, r.instruction as instruction
            LIMIT 5
        """)
        
        async for record in result:
            print(f"   • {record['category']}: {record['instruction'][:60]}...")
            print(f"     ID: {record['rule_id']}")


if __name__ == "__main__":
    asyncio.run(inspect_graph())
