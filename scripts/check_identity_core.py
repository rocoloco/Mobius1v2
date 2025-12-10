"""Check Identity Core data in Neo4j."""

import asyncio
from mobius.storage.graph import graph_storage


async def check_identity_core():
    """Show the complete Identity Core data for Stripe."""
    
    print("Checking Identity Core in Neo4j...")
    print("=" * 60)
    
    if not graph_storage._is_enabled():
        print("❌ Neo4j is not enabled")
        return
    
    async with graph_storage.driver.session() as session:
        # Get brand with archetype
        result = await session.run("""
            MATCH (b:Brand {name: "stripe.com"})
            OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
            RETURN b.name as brand, a.name as archetype
        """)
        
        record = await result.single()
        if record:
            print(f"\nBrand: {record['brand']}")
            print(f"Archetype: {record['archetype'] or 'None'}")
        
        # Get voice vectors
        print(f"\nVoice Vectors:")
        result = await session.run("""
            MATCH (b:Brand {name: "stripe.com"})-[v:HAS_VOICE_VECTOR]->(b)
            RETURN v.dimension as dimension, v.score as score
            ORDER BY v.score DESC
        """)
        
        voice_vectors = []
        async for record in result:
            dimension = record['dimension']
            score = record['score']
            voice_vectors.append((dimension, score))
            bar = "█" * int(score * 20)
            print(f"  {dimension:12} {bar:20} {score:.2f}")
        
        if not voice_vectors:
            print("  (No voice vectors found)")
        
        # Get negative constraints
        print(f"\nNegative Constraints:")
        result = await session.run("""
            MATCH (b:Brand {name: "stripe.com"})-[f:FORBIDS]->(b)
            RETURN f.constraint as constraint
        """)
        
        constraints = []
        async for record in result:
            constraints.append(record['constraint'])
            print(f"  • {record['constraint']}")
        
        if not constraints:
            print("  (No negative constraints found)")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"IDENTITY CORE STATUS:")
        print(f"  Archetype: {'✓' if record and record['archetype'] else '✗'}")
        print(f"  Voice Vectors: {len(voice_vectors)} {'✓' if voice_vectors else '✗'}")
        print(f"  Negative Constraints: {len(constraints)} {'✓' if constraints else '✗'}")
        
        if record and record['archetype'] and voice_vectors:
            print(f"\n✅ Identity Core is COMPLETE!")
        else:
            print(f"\n⚠️  Identity Core is INCOMPLETE")


if __name__ == "__main__":
    asyncio.run(check_identity_core())
