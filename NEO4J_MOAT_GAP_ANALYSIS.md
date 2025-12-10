# Neo4j Graph MOAT Structure - Gap Analysis

## Current State (What's Being Synced)

### Nodes
- **Brand**: `brand_id`, `name`, `organization_id`, `learning_active`, `feedback_count`, `created_at`, `updated_at`
- **Color**: `hex`, `name`
- **Asset**: `asset_id`, `prompt`, `image_url`, `compliance_score`, `status`, `created_at`
- **Template**: `template_id`, `name`, `description`, `created_at`

### Relationships
- `(Brand)-[:OWNS_COLOR {usage, usage_weight, context}]->(Color)`
- `(Brand)-[:GENERATED_ASSET]->(Asset)`
- `(Brand)-[:HAS_TEMPLATE]->(Template)`
- `(Template)-[:BASED_ON_ASSET]->(Asset)`
- `(Asset)-[:RECEIVED_FEEDBACK {action, reason, timestamp}]->(Asset)` (self-loop)

## MOAT Structure (What Should Be Synced)

### Missing Critical Data

#### 1. Identity Core (The Strategic Moat)
**Not currently synced:**
- `archetype` - Brand archetype (e.g., "The Sage", "The Hero")
- `voice_vectors` - Voice dimensions (formal, witty, technical, urgent)
- `negative_constraints` - High-level "never do this" rules

**Why it matters:** This is the strategic positioning that creates lock-in. Without this in the graph, we can't query "Find brands with similar archetypes" or "Show me all brands that are formal but witty."

#### 2. Typography (Visual DNA)
**Not currently synced:**
- Font families
- Font weights
- Usage guidelines

**Why it matters:** Typography is a key brand differentiator. We should be able to query "Find brands using Inter" or "Show me brands with similar typography."

#### 3. Contextual Rules (Channel-Specific Governance)
**Not currently synced:**
- Context-specific rules (LinkedIn vs. Instagram, print vs. digital)
- Rule priorities
- Asset type applicability

**Why it matters:** This enables queries like "What are the LinkedIn-specific rules for this brand?" or "Find brands with print packaging rules."

#### 4. Asset Graph (Asset Inventory)
**Not currently synced:**
- Logo variants (primary, reversed, icon, wordmark)
- Templates
- Patterns
- Photography style

**Why it matters:** This creates the single source of truth for assets. We should be able to query "Get all logo variants for this brand" or "Find brands with similar asset structures."

#### 5. Brand Rules (Governance)
**Not currently synced:**
- Rule categories (visual, verbal, legal)
- Rule severity (warning, critical)
- Negative constraints flag

**Why it matters:** Enables queries like "Show me all critical visual rules" or "Find brands with similar governance structures."

## Recommended Neo4j Schema Updates

### New Nodes

```cypher
// Typography node
(:Typography {
  family: string,
  weights: [string],
  usage: string
})

// Rule node
(:Rule {
  rule_id: string,
  category: string,  // visual, verbal, legal
  instruction: string,
  severity: string,  // warning, critical
  negative_constraint: boolean
})

// ContextualRule node
(:ContextualRule {
  rule_id: string,
  context: string,  // social_media_linkedin, print_packaging, etc.
  rule: string,
  priority: int,
  applies_to: [string]
})

// Archetype node (shared across brands)
(:Archetype {
  name: string  // "The Sage", "The Hero", etc.
})
```

### New Relationships

```cypher
// Identity Core
(Brand)-[:HAS_ARCHETYPE]->(Archetype)
(Brand)-[:HAS_VOICE_VECTOR {dimension: string, score: float}]->(Brand)  // self-loop for each vector
(Brand)-[:FORBIDS {constraint: string}]->(Brand)  // self-loop for negative constraints

// Typography
(Brand)-[:USES_TYPOGRAPHY {usage: string}]->(Typography)

// Rules
(Brand)-[:HAS_RULE]->(Rule)
(Brand)-[:HAS_CONTEXTUAL_RULE]->(ContextualRule)

// Asset Graph
(Brand)-[:HAS_LOGO {variant: string, url: string}]->(Brand)  // self-loop for each logo variant
```

### Enhanced Queries Enabled

With the full MOAT structure in Neo4j, we can run powerful queries:

```cypher
// Find brands with similar identity
MATCH (b1:Brand)-[:HAS_ARCHETYPE]->(a:Archetype)<-[:HAS_ARCHETYPE]-(b2:Brand)
WHERE b1.brand_id = $brand_id AND b1 <> b2
RETURN b2.name, a.name as shared_archetype

// Find brands with similar voice profiles
MATCH (b1:Brand)-[v1:HAS_VOICE_VECTOR]->(b1)
MATCH (b2:Brand)-[v2:HAS_VOICE_VECTOR]->(b2)
WHERE b1.brand_id = $brand_id 
  AND v1.dimension = v2.dimension
  AND abs(v1.score - v2.score) < 0.2
WITH b2, count(*) as matching_vectors
WHERE matching_vectors >= 3
RETURN b2.name, matching_vectors

// Find brands using the same typography
MATCH (b1:Brand)-[:USES_TYPOGRAPHY]->(t:Typography)<-[:USES_TYPOGRAPHY]-(b2:Brand)
WHERE b1.brand_id = $brand_id AND b1 <> b2
RETURN b2.name, collect(t.family) as shared_fonts

// Get all contextual rules for a specific context
MATCH (b:Brand {brand_id: $brand_id})-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
WHERE cr.context = 'social_media_linkedin'
RETURN cr.rule, cr.priority
ORDER BY cr.priority DESC

// Find brands with similar governance complexity
MATCH (b1:Brand {brand_id: $brand_id})-[:HAS_RULE]->(r1:Rule)
MATCH (b2:Brand)-[:HAS_RULE]->(r2:Rule)
WHERE b1 <> b2
WITH b2, 
     count(r2) as rule_count,
     sum(CASE WHEN r2.severity = 'critical' THEN 1 ELSE 0 END) as critical_count
ORDER BY abs(rule_count - $target_rule_count)
RETURN b2.name, rule_count, critical_count
LIMIT 5
```

## Implementation Priority

### Phase 1: Core Identity (Highest MOAT Value)
1. Sync `identity_core.archetype` → Create Archetype nodes
2. Sync `identity_core.voice_vectors` → Create voice vector relationships
3. Sync `identity_core.negative_constraints` → Create constraint relationships

### Phase 2: Visual DNA
4. Sync `typography` → Create Typography nodes and relationships
5. Enhance color sync to include semantic grouping (primary, secondary, accent, neutral, semantic)

### Phase 3: Governance
6. Sync `rules` → Create Rule nodes
7. Sync `contextual_rules` → Create ContextualRule nodes

### Phase 4: Asset Graph
8. Sync `asset_graph.logos` → Create logo variant relationships
9. Sync `asset_graph.templates` → Link to Template nodes
10. Sync `asset_graph.patterns` → Create pattern relationships

## Benefits of Full MOAT Sync

1. **Strategic Insights**: Query brands by archetype, voice profile, governance complexity
2. **Competitive Analysis**: Find brands with similar positioning or visual DNA
3. **Recommendation Engine**: "Brands like yours use these rules..."
4. **Compliance Tracking**: Track which brands have specific governance rules
5. **Asset Discovery**: Find all variants of logos, templates, patterns across brands
6. **Learning Patterns**: Identify common rule patterns across successful brands
7. **Migration Difficulty**: The more structured data in the graph, the harder it is for clients to leave

## Next Steps

1. Update `graph.py` to sync identity_core, typography, rules, and contextual_rules
2. Create migration script to backfill existing brands with new graph structure
3. Add graph queries to API endpoints for brand insights and recommendations
4. Build dashboard visualizations powered by graph queries
