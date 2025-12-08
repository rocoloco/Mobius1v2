# Mobius Graph Schema Design

## Overview
Transform Mobius from list-based storage to a graph model that enables relationship intelligence, advanced queries, and network effects for competitive moat.

---

## Node Types

### 1. Brand Node
**Properties:**
- `brand_id` (string, primary key)
- `organization_id` (string, indexed)
- `name` (string)
- `website` (string, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `learning_active` (boolean)
- `privacy_tier` (enum: off, private, shared)

**Purpose:** Root node for all brand-related entities

---

### 2. Color Node
**Properties:**
- `color_id` (string, primary key)
- `name` (string) - e.g., "Midnight Blue"
- `hex` (string) - e.g., "#0057B8"
- `usage` (enum: primary, secondary, accent, neutral, semantic)
- `usage_weight` (float, 0.0-1.0)
- `context` (string, optional)

**Purpose:** Individual color specifications with semantic roles

---

### 3. Typography Node
**Properties:**
- `typography_id` (string, primary key)
- `family` (string) - e.g., "Helvetica Neue"
- `weights` (array[string]) - e.g., ["Regular", "Bold"]
- `usage_context` (string)

**Purpose:** Font specifications

---

### 4. Logo Node
**Properties:**
- `logo_id` (string, primary key)
- `variant_name` (string) - e.g., "Primary Horizontal"
- `url` (string)
- `min_width_px` (int)
- `clear_space_ratio` (float)

**Purpose:** Logo variants and specifications

---

### 5. Rule Node
**Properties:**
- `rule_id` (string, primary key)
- `category` (enum: visual, verbal, legal)
- `instruction` (text)
- `severity` (enum: warning, critical)
- `negative_constraint` (boolean)
- `created_at` (timestamp)

**Purpose:** Governance rules for compliance checking

---

### 6. Asset Node
**Properties:**
- `asset_id` (string, primary key)
- `job_id` (string)
- `image_url` (string)
- `prompt` (text)
- `compliance_score` (float, 0.0-1.0)
- `status` (enum: pending, approved, rejected, needs_review)
- `created_at` (timestamp)

**Purpose:** Generated assets

---

### 7. Feedback Node
**Properties:**
- `feedback_id` (string, primary key)
- `action` (enum: approve, reject)
- `reason` (text, optional)
- `timestamp` (timestamp)
- `user_id` (string, optional)

**Purpose:** User feedback events

---

### 8. Pattern Node
**Properties:**
- `pattern_id` (string, primary key)
- `pattern_type` (string) - e.g., "color_preference", "layout_style"
- `confidence_score` (float, 0.0-1.0)
- `sample_count` (int)
- `pattern_data` (jsonb) - flexible storage for pattern details
- `scope` (enum: brand, industry)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Purpose:** Learned patterns from feedback (ML insights)

---

### 9. Violation Node
**Properties:**
- `violation_id` (string, primary key)
- `category` (string)
- `severity` (enum: warning, critical)
- `description` (text)
- `detected_at` (timestamp)

**Purpose:** Specific compliance violations detected during audit

---

## Edge Types (Relationships)

### Brand Relationships

#### `OWNS_COLOR`
- **From:** Brand → Color
- **Properties:** 
  - `added_at` (timestamp)
- **Cardinality:** One-to-Many
- **Query Use:** "Get all colors for brand X"

#### `OWNS_TYPOGRAPHY`
- **From:** Brand → Typography
- **Properties:** 
  - `added_at` (timestamp)
- **Cardinality:** One-to-Many

#### `OWNS_LOGO`
- **From:** Brand → Logo
- **Properties:** 
  - `added_at` (timestamp)
- **Cardinality:** One-to-Many

#### `HAS_RULE`
- **From:** Brand → Rule
- **Properties:** 
  - `added_at` (timestamp)
  - `active` (boolean)
- **Cardinality:** One-to-Many
- **Query Use:** "Get all active rules for brand X"

#### `GENERATED_ASSET`
- **From:** Brand → Asset
- **Properties:** 
  - `generation_timestamp` (timestamp)
- **Cardinality:** One-to-Many

#### `LEARNED_PATTERN`
- **From:** Brand → Pattern
- **Properties:** 
  - `learned_at` (timestamp)
  - `active` (boolean)
- **Cardinality:** One-to-Many
- **Query Use:** "What patterns has this brand learned?"

---

### Asset Relationships

#### `USES_COLOR`
- **From:** Asset → Color
- **Properties:** 
  - `coverage_percentage` (float) - how much of the asset uses this color
  - `detected_by` (enum: vision_model, audit_node)
- **Cardinality:** Many-to-Many
- **Query Use:** "Which assets use this color?" / "What colors appear in this asset?"

#### `USES_TYPOGRAPHY`
- **From:** Asset → Typography
- **Properties:** 
  - `detected_by` (enum: vision_model, audit_node)
- **Cardinality:** Many-to-Many

#### `INCLUDES_LOGO`
- **From:** Asset → Logo
- **Properties:** 
  - `placement` (string) - e.g., "top-left"
  - `size_px` (int)
- **Cardinality:** Many-to-Many

#### `VIOLATES_RULE`
- **From:** Asset → Rule
- **Properties:** 
  - `detected_at` (timestamp)
  - `confidence` (float)
- **Cardinality:** Many-to-Many
- **Query Use:** "What rules does this asset violate?" / "Which assets violate this rule?"

#### `HAS_VIOLATION`
- **From:** Asset → Violation
- **Properties:** 
  - `detected_at` (timestamp)
- **Cardinality:** One-to-Many

#### `RECEIVED_FEEDBACK`
- **From:** Asset → Feedback
- **Properties:** None
- **Cardinality:** One-to-Many
- **Query Use:** "Get all feedback for this asset"

---

### Rule Relationships

#### `APPLIES_TO_COLOR`
- **From:** Rule → Color
- **Properties:** 
  - `constraint_type` (enum: required, forbidden, conditional)
- **Cardinality:** Many-to-Many
- **Query Use:** "Which rules govern this color?" / "Which colors does this rule apply to?"

#### `APPLIES_TO_LOGO`
- **From:** Rule → Logo
- **Properties:** 
  - `constraint_type` (enum: required, forbidden, conditional)
- **Cardinality:** Many-to-Many

#### `CONFLICTS_WITH`
- **From:** Rule → Rule
- **Properties:** 
  - `conflict_reason` (text)
  - `detected_at` (timestamp)
- **Cardinality:** Many-to-Many
- **Query Use:** "Are there conflicting rules in this brand?"

---

### Pattern Relationships

#### `INFLUENCED_BY_FEEDBACK`
- **From:** Pattern → Feedback
- **Properties:** 
  - `weight` (float) - how much this feedback contributed to the pattern
- **Cardinality:** Many-to-Many
- **Query Use:** "Which feedback events created this pattern?"

#### `SUGGESTS_COLOR`
- **From:** Pattern → Color
- **Properties:** 
  - `confidence` (float)
  - `context` (string) - when to use this color
- **Cardinality:** Many-to-Many
- **Query Use:** "What colors does this pattern recommend?"

#### `SUGGESTS_TYPOGRAPHY`
- **From:** Pattern → Typography
- **Properties:** 
  - `confidence` (float)
- **Cardinality:** Many-to-Many

#### `SIMILAR_TO`
- **From:** Pattern → Pattern
- **Properties:** 
  - `similarity_score` (float, 0.0-1.0)
  - `shared_features` (array[string])
- **Cardinality:** Many-to-Many
- **Query Use:** "Find similar patterns across brands" (industry learning)

---

### Color Relationships

#### `PAIRS_WITH`
- **From:** Color → Color
- **Properties:** 
  - `pairing_score` (float) - learned from approved assets
  - `sample_count` (int) - how many times this pairing was approved
  - `context` (string) - e.g., "primary-accent", "background-text"
- **Cardinality:** Many-to-Many
- **Query Use:** "What colors pair well with this one?" (MOAT FEATURE)

#### `FORBIDDEN_WITH`
- **From:** Color → Color
- **Properties:** 
  - `reason` (text)
- **Cardinality:** Many-to-Many
- **Query Use:** "What color combinations should be avoided?"

---

### Feedback Relationships

#### `APPROVED_ASSET`
- **From:** Feedback → Asset
- **Properties:** None
- **Cardinality:** Many-to-One
- **Inverse of:** `RECEIVED_FEEDBACK`

#### `REINFORCES_PATTERN`
- **From:** Feedback → Pattern
- **Properties:** 
  - `contribution_weight` (float)
- **Cardinality:** Many-to-Many

---

## Advanced Graph Queries (Competitive Moat)

### 1. Multi-Hop Compliance Chain
```cypher
// Find the full dependency chain for a violation
MATCH path = (a:Asset)-[:HAS_VIOLATION]->(v:Violation)
             -[:CAUSED_BY_RULE]->(r:Rule)
             -[:APPLIES_TO_COLOR]->(c:Color)
             <-[:OWNS_COLOR]-(b:Brand)
RETURN path
```

### 2. Color Pairing Intelligence
```cypher
// Find best color pairings based on approval history
MATCH (c1:Color)<-[:USES_COLOR]-(a:Asset)-[:USES_COLOR]->(c2:Color)
WHERE (a)-[:RECEIVED_FEEDBACK]->(:Feedback {action: 'approve'})
WITH c1, c2, COUNT(a) as pairing_count
WHERE pairing_count > 5
RETURN c1.name, c2.name, pairing_count
ORDER BY pairing_count DESC
```

### 3. Cross-Brand Pattern Discovery
```cypher
// Find similar patterns across brands (industry learning)
MATCH (b1:Brand)-[:LEARNED_PATTERN]->(p1:Pattern)
      -[:SIMILAR_TO {similarity_score: >0.8}]->(p2:Pattern)
      <-[:LEARNED_PATTERN]-(b2:Brand)
WHERE b1.organization_id <> b2.organization_id
  AND b1.privacy_tier = 'shared'
  AND b2.privacy_tier = 'shared'
RETURN b1.name, p1.pattern_type, b2.name, p2.pattern_type
```

### 4. Rule Conflict Detection
```cypher
// Find conflicting rules within a brand
MATCH (b:Brand)-[:HAS_RULE]->(r1:Rule)-[:CONFLICTS_WITH]->(r2:Rule)
      <-[:HAS_RULE]-(b)
RETURN r1.instruction, r2.instruction, r1.severity, r2.severity
```

### 5. Asset Genealogy
```cypher
// Trace which patterns influenced an asset's generation
MATCH (a:Asset)<-[:GENERATED_ASSET]-(b:Brand)
      -[:LEARNED_PATTERN]->(p:Pattern)
      -[:INFLUENCED_BY_FEEDBACK]->(f:Feedback)
      -[:APPROVED_ASSET]->(prev_asset:Asset)
RETURN a.asset_id, p.pattern_type, prev_asset.asset_id, f.timestamp
ORDER BY f.timestamp
```

### 6. Compliance Hotspots
```cypher
// Find which rules are violated most frequently
MATCH (r:Rule)<-[:VIOLATES_RULE]-(a:Asset)
WITH r, COUNT(a) as violation_count
WHERE violation_count > 10
RETURN r.instruction, r.severity, violation_count
ORDER BY violation_count DESC
```

---

## Monetization Opportunities

### Free Tier
- Basic list queries (backwards compatible)
- Single-hop relationships (Asset → Colors)

### Pro Tier ($99/mo)
- Multi-hop graph traversal
- Color pairing intelligence
- Pattern similarity search
- Rule conflict detection

### Enterprise Tier ($999/mo)
- Cross-brand pattern discovery (industry insights)
- Custom graph algorithms
- Real-time graph analytics
- Graph export API

### API Tier (Usage-based)
- $0.01 per graph query
- $0.10 per pattern similarity search
- $1.00 per cross-brand analysis

---

## Implementation Benefits

1. **Competitive Moat:** Graph traversal and relationship queries are significantly harder to replicate than list-based storage

2. **Network Effects:** As more brands use the system, pattern relationships become more valuable (industry learning)

3. **Advanced Analytics:** Multi-hop queries enable insights impossible with flat lists

4. **Scalability:** Graph databases are optimized for relationship queries that would require complex JOINs in SQL

5. **Flexibility:** Easy to add new node types and relationships without schema migrations

6. **ML Integration:** Graph structure naturally supports pattern propagation and similarity algorithms

---

## Next Steps

1. Evaluate graph database options (see GRAPH-DATABASE-EVALUATION.md)
2. Design migration strategy from lists → graph
3. Implement core graph operations
4. Build premium graph query endpoints
5. Add graph visualization for enterprise customers
