"""Run Neo4j MOAT verification queries."""

import asyncio
from mobius.storage.graph import graph_storage
import json


async def run_query(session, name: str, query: str, params: dict = None):
    """Run a query and display results."""
    print(f"\n{'='*60}")
    print(f"QUERY: {name}")
    print(f"{'='*60}")
    
    try:
        result = await session.run(query, params or {})
        records = [dict(record) async for record in result]
        
        if not records:
            print("(No results)")
            return
        
        # Pretty print results
        for i, record in enumerate(records, 1):
            if i <= 10:  # Limit to first 10 results
                print(f"\n{i}. {json.dumps(record, indent=2, default=str)}")
        
        if len(records) > 10:
            print(f"\n... and {len(records) - 10} more results")
        
        print(f"\nTotal: {len(records)} results")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def run_moat_verification():
    """Run key MOAT verification queries."""
    
    print("="*60)
    print("NEO4J MOAT VERIFICATION")
    print("="*60)
    
    if not graph_storage._is_enabled():
        print("❌ Neo4j is not enabled")
        return
    
    async with graph_storage.driver.session() as session:
        
        # 1. Basic Overview
        await run_query(
            session,
            "1. Node Type Distribution",
            """
            MATCH (n)
            RETURN DISTINCT labels(n) as NodeType, count(*) as Count
            ORDER BY Count DESC
            """
        )
        
        # 2. Brand Overview
        await run_query(
            session,
            "2. Brand Data Richness",
            """
            MATCH (b:Brand)
            OPTIONAL MATCH (b)-[:OWNS_COLOR]->(c:Color)
            OPTIONAL MATCH (b)-[:USES_TYPOGRAPHY]->(t:Typography)
            OPTIONAL MATCH (b)-[:HAS_RULE]->(r:Rule)
            OPTIONAL MATCH (b)-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
            OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
            RETURN 
              b.name as Brand,
              a.name as Archetype,
              count(DISTINCT c) as Colors,
              count(DISTINCT t) as Fonts,
              count(DISTINCT r) as Rules,
              count(DISTINCT cr) as ContextualRules
            ORDER BY b.created_at DESC
            """
        )
        
        # 3. MOAT Completeness Check
        await run_query(
            session,
            "3. MOAT Structure Completeness",
            """
            MATCH (b:Brand)
            OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
            OPTIONAL MATCH (b)-[v:HAS_VOICE_VECTOR]->(b)
            OPTIONAL MATCH (b)-[f:FORBIDS]->(b)
            OPTIONAL MATCH (b)-[:HAS_CONTEXTUAL_RULE]->(cr)
            OPTIONAL MATCH (b)-[l:HAS_LOGO]->(b)
            RETURN 
              b.name as Brand,
              CASE WHEN a IS NOT NULL THEN 'YES' ELSE 'NO' END as HasArchetype,
              count(DISTINCT v) as VoiceVectors,
              count(DISTINCT f) as NegativeConstraints,
              count(DISTINCT cr) as ContextualRules,
              count(DISTINCT l) as LogoVariants,
              CASE 
                WHEN a IS NOT NULL AND count(DISTINCT v) > 0 THEN 'COMPLETE'
                ELSE 'INCOMPLETE'
              END as MOATStatus
            ORDER BY b.created_at DESC
            """
        )
        
        # 4. Color Intelligence
        await run_query(
            session,
            "4. Color Usage by Semantic Role",
            """
            MATCH (b:Brand)-[r:OWNS_COLOR]->(c:Color)
            RETURN 
              r.usage as ColorRole,
              count(DISTINCT c) as UniqueColors,
              count(DISTINCT b) as BrandsUsingRole,
              collect(DISTINCT c.hex)[0..5] as SampleHexCodes
            ORDER BY BrandsUsingRole DESC
            """
        )
        
        # 5. Typography Intelligence
        await run_query(
            session,
            "5. Most Popular Fonts",
            """
            MATCH (b:Brand)-[:USES_TYPOGRAPHY]->(t:Typography)
            RETURN t.family as Font, count(b) as BrandCount, collect(b.name)[0..5] as SampleBrands
            ORDER BY BrandCount DESC
            """
        )
        
        # 6. Governance Rules
        await run_query(
            session,
            "6. Rule Categories Distribution",
            """
            MATCH (b:Brand)-[:HAS_RULE]->(r:Rule)
            RETURN r.category as RuleCategory, r.severity as Severity, count(*) as RuleCount
            ORDER BY RuleCount DESC
            """
        )
        
        # 7. Contextual Rules
        await run_query(
            session,
            "7. Rules by Channel/Context",
            """
            MATCH (b:Brand)-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
            RETURN 
              cr.context as Channel,
              count(DISTINCT b) as BrandsWithRules,
              collect(DISTINCT b.name)[0..3] as SampleBrands
            ORDER BY BrandsWithRules DESC
            """
        )
        
        # 8. Asset Graph
        await run_query(
            session,
            "8. Logo Variants by Brand",
            """
            MATCH (b:Brand)-[l:HAS_LOGO]->(b)
            RETURN b.name as Brand, collect(l.variant) as LogoVariants, count(l) as VariantCount
            ORDER BY VariantCount DESC
            """
        )
        
        # 9. Brand Complexity Score
        await run_query(
            session,
            "9. Brand Complexity Score (Lock-In Strength)",
            """
            MATCH (b:Brand)
            OPTIONAL MATCH (b)-[:OWNS_COLOR]->(c)
            OPTIONAL MATCH (b)-[:USES_TYPOGRAPHY]->(t)
            OPTIONAL MATCH (b)-[:HAS_RULE]->(r)
            OPTIONAL MATCH (b)-[:HAS_CONTEXTUAL_RULE]->(cr)
            WITH b, 
                 count(DISTINCT c) as ColorCount,
                 count(DISTINCT t) as FontCount,
                 count(DISTINCT r) as RuleCount,
                 count(DISTINCT cr) as ContextualRuleCount
            RETURN 
              b.name as Brand,
              ColorCount,
              FontCount,
              RuleCount,
              ContextualRuleCount,
              (ColorCount + FontCount + RuleCount * 2 + ContextualRuleCount * 3) as ComplexityScore
            ORDER BY ComplexityScore DESC
            """
        )
        
        # 10. Migration Difficulty (MOAT Strength)
        await run_query(
            session,
            "10. Migration Difficulty Score (MOAT Strength)",
            """
            MATCH (b:Brand)
            OPTIONAL MATCH (b)-[r]->(n)
            WITH b, count(DISTINCT r) as RelationshipCount, count(DISTINCT n) as NodeCount
            RETURN 
              b.name as Brand,
              RelationshipCount,
              NodeCount,
              (RelationshipCount * NodeCount) as MigrationDifficulty,
              CASE 
                WHEN (RelationshipCount * NodeCount) > 50 THEN 'HIGH (Strong Lock-In)'
                WHEN (RelationshipCount * NodeCount) > 20 THEN 'MEDIUM'
                ELSE 'LOW (Weak Lock-In)'
              END as LockInStrength
            ORDER BY MigrationDifficulty DESC
            """
        )
        
        print("\n" + "="*60)
        print("VERIFICATION COMPLETE")
        print("="*60)
        print("\nFor more queries, see: NEO4J_MOAT_QUERIES.md")
        print("To run in Neo4j Browser: https://console.neo4j.io/")


if __name__ == "__main__":
    asyncio.run(run_moat_verification())
