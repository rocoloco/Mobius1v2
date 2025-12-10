"""Test Neo4j sync with full MOAT structure."""

import asyncio
from mobius.storage.brands import BrandStorage
from mobius.storage.graph import graph_storage
from mobius.models.brand import (
    Brand, BrandGuidelines, Color, Typography, 
    IdentityCore, ContextualRule, AssetGraph, BrandRule
)
from datetime import datetime, timezone
import uuid


async def test_moat_sync():
    """Create a brand with full MOAT structure and verify Neo4j sync."""
    
    print("Testing Neo4j sync with full MOAT structure...")
    print("=" * 60)
    
    # Create a brand with complete MOAT structure
    brand_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    brand = Brand(
        brand_id=brand_id,
        organization_id="00000000-0000-0000-0000-000000000000",
        name="MOAT Test Brand",
        guidelines=BrandGuidelines(
            # Identity Core (THE MOAT)
            identity_core=IdentityCore(
                archetype="The Sage",
                voice_vectors={
                    "formal": 0.8,
                    "witty": 0.2,
                    "technical": 0.7,
                    "urgent": 0.1
                },
                negative_constraints=[
                    "No drop shadows",
                    "No neon colors",
                    "Never use gradients on text"
                ]
            ),
            
            # Visual DNA
            colors=[
                Color(
                    hex="#0057B8",
                    name="Midnight Blue",
                    usage="primary",
                    usage_weight=0.6,
                    context="Headers and CTAs"
                ),
                Color(
                    hex="#FFFFFF",
                    name="White",
                    usage="neutral",
                    usage_weight=0.3,
                    context="Backgrounds"
                ),
            ],
            
            typography=[
                Typography(
                    family="Inter",
                    weights=["400", "600", "700"],
                    usage="Primary font for all text"
                ),
                Typography(
                    family="Georgia",
                    weights=["400", "700"],
                    usage="Serif for quotes and emphasis"
                ),
            ],
            
            # Governance Rules
            rules=[
                BrandRule(
                    category="visual",
                    instruction="Logo must have 20px minimum clear space",
                    severity="critical",
                    negative_constraint=False
                ),
                BrandRule(
                    category="visual",
                    instruction="Do not use drop shadows on any elements",
                    severity="warning",
                    negative_constraint=True
                ),
            ],
            
            # Contextual Rules (MOAT - Channel-specific)
            contextual_rules=[
                ContextualRule(
                    context="social_media_linkedin",
                    rule="Images must contain human subjects; 20% overlay opacity maximum",
                    priority=10,
                    applies_to=["image"]
                ),
                ContextualRule(
                    context="print_packaging",
                    rule="CMYK only; minimal whitespace 15mm",
                    priority=8,
                    applies_to=["image", "document"]
                ),
            ],
            
            # Asset Graph (MOAT - Asset inventory)
            asset_graph=AssetGraph(
                logos={
                    "primary": "s3://bucket/logo_main.svg",
                    "reversed": "s3://bucket/logo_white.svg",
                    "icon": "s3://bucket/logo_icon.png"
                },
                templates={
                    "social_post": "s3://bucket/template_social.psd",
                    "email_header": "s3://bucket/template_email.psd"
                },
                patterns={
                    "background_texture": "s3://bucket/pattern_bg.png"
                }
            )
        ),
        created_at=now,
        updated_at=now
    )
    
    print(f"\n1. Creating brand with MOAT structure...")
    print(f"   Name: {brand.name}")
    print(f"   Archetype: {brand.guidelines.identity_core.archetype}")
    print(f"   Voice Vectors: {len(brand.guidelines.identity_core.voice_vectors)}")
    print(f"   Colors: {len(brand.guidelines.colors)}")
    print(f"   Typography: {len(brand.guidelines.typography)}")
    print(f"   Rules: {len(brand.guidelines.rules)}")
    print(f"   Contextual Rules: {len(brand.guidelines.contextual_rules)}")
    print(f"   Logo Variants: {len(brand.guidelines.asset_graph.logos)}")
    
    # Create brand (this should sync everything to Neo4j)
    storage = BrandStorage()
    created_brand = await storage.create_brand(brand)
    
    print(f"\n   ✓ Brand created in Supabase")
    
    # Wait for sync
    await asyncio.sleep(1)
    
    # Verify in Neo4j
    print(f"\n2. Verifying Neo4j sync...")
    
    if not graph_storage._is_enabled():
        print("   ❌ Neo4j is not enabled")
        return
    
    async with graph_storage.driver.session() as session:
        # Check brand node
        result = await session.run(
            "MATCH (b:Brand {brand_id: $brand_id}) RETURN b",
            brand_id=brand_id
        )
        brand_record = await result.single()
        
        if not brand_record:
            print(f"   ❌ Brand NOT found in Neo4j")
            return
        
        print(f"   ✓ Brand node found")
        
        # Check archetype
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[:HAS_ARCHETYPE]->(a:Archetype)
            RETURN a.name as archetype
            """,
            brand_id=brand_id
        )
        archetype_record = await result.single()
        if archetype_record:
            print(f"   ✓ Archetype: {archetype_record['archetype']}")
        
        # Check voice vectors
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[v:HAS_VOICE_VECTOR]->(b)
            RETURN v.dimension as dimension, v.score as score
            """,
            brand_id=brand_id
        )
        voice_vectors = [dict(record) async for record in result]
        print(f"   ✓ Voice Vectors: {len(voice_vectors)}")
        for vv in voice_vectors:
            print(f"      - {vv['dimension']}: {vv['score']}")
        
        # Check negative constraints
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[f:FORBIDS]->(b)
            RETURN f.constraint as constraint
            """,
            brand_id=brand_id
        )
        constraints = [record['constraint'] async for record in result]
        print(f"   ✓ Negative Constraints: {len(constraints)}")
        for c in constraints:
            print(f"      - {c}")
        
        # Check colors
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[r:OWNS_COLOR]->(c:Color)
            RETURN c.name as name, c.hex as hex, r.usage as usage
            """,
            brand_id=brand_id
        )
        colors = [dict(record) async for record in result]
        print(f"   ✓ Colors: {len(colors)}")
        for color in colors:
            print(f"      - {color['name']}: {color['hex']} ({color['usage']})")
        
        # Check typography
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[:USES_TYPOGRAPHY]->(t:Typography)
            RETURN t.family as family
            """,
            brand_id=brand_id
        )
        fonts = [record['family'] async for record in result]
        print(f"   ✓ Typography: {len(fonts)}")
        for font in fonts:
            print(f"      - {font}")
        
        # Check rules
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[:HAS_RULE]->(r:Rule)
            RETURN r.category as category, r.severity as severity
            """,
            brand_id=brand_id
        )
        rules = [dict(record) async for record in result]
        print(f"   ✓ Rules: {len(rules)}")
        
        # Check contextual rules
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
            RETURN cr.context as context, cr.priority as priority
            """,
            brand_id=brand_id
        )
        ctx_rules = [dict(record) async for record in result]
        print(f"   ✓ Contextual Rules: {len(ctx_rules)}")
        for cr in ctx_rules:
            print(f"      - {cr['context']} (priority: {cr['priority']})")
        
        # Check logo variants
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[l:HAS_LOGO]->(b)
            RETURN l.variant as variant
            """,
            brand_id=brand_id
        )
        logos = [record['variant'] async for record in result]
        print(f"   ✓ Logo Variants: {len(logos)}")
        for logo in logos:
            print(f"      - {logo}")
        
        # Check templates
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[t:HAS_TEMPLATE]->(b)
            RETURN t.name as name
            """,
            brand_id=brand_id
        )
        templates = [record['name'] async for record in result]
        print(f"   ✓ Templates: {len(templates)}")
        
        # Check patterns
        result = await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})-[p:HAS_PATTERN]->(b)
            RETURN p.name as name
            """,
            brand_id=brand_id
        )
        patterns = [record['name'] async for record in result]
        print(f"   ✓ Patterns: {len(patterns)}")
    
    print(f"\n✅ SUCCESS! Full MOAT structure synced to Neo4j")
    
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
    asyncio.run(test_moat_sync())
