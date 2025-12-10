# Neo4j MOAT Verification Queries

These queries demonstrate the competitive moat created by your Brand Graph architecture. Run these in the Neo4j Browser or use the Python script below.

## 1. BASIC VERIFICATION QUERIES

### Show All Node Types
```cypher
// See what types of data you have
MATCH (n)
RETURN DISTINCT labels(n) as NodeType, count(*) as Count
ORDER BY Count DESC
```

### Show Complete Brand Graph
```cypher
// Visualize the entire brand graph structure
MATCH (b:Brand)
OPTIONAL MATCH (b)-[r]->(n)
RETURN b, r, n
LIMIT 100
```

### Brand Overview with Counts
```cypher
// Get a summary of each brand's data richness
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
```

---

## 2. IDENTITY CORE QUERIES (Strategic Positioning MOAT)

### Find Brands by Archetype
```cypher
// Group brands by their strategic archetype
MATCH (b:Brand)-[:HAS_ARCHETYPE]->(a:Archetype)
RETURN a.name as Archetype, collect(b.name) as Brands, count(b) as BrandCount
ORDER BY BrandCount DESC
```

### Get Brand Voice Profile
```cypher
// Show the complete voice vector profile for a brand
MATCH (b:Brand {name: "stripe.com"})-[v:HAS_VOICE_VECTOR]->(b)
RETURN v.dimension as Dimension, v.score as Score
ORDER BY v.score DESC
```

### Find Brands with Similar Voice Profiles
```cypher
// Find brands with similar voice characteristics (within 0.2 on each dimension)
MATCH (b1:Brand {name: "stripe.com"})-[v1:HAS_VOICE_VECTOR]->(b1)
MATCH (b2:Brand)-[v2:HAS_VOICE_VECTOR]->(b2)
WHERE b1 <> b2 
  AND v1.dimension = v2.dimension
  AND abs(v1.score - v2.score) < 0.2
WITH b2, count(*) as matching_dimensions
WHERE matching_dimensions >= 3
RETURN b2.name as SimilarBrand, matching_dimensions as MatchingVoiceVectors
ORDER BY matching_dimensions DESC
```

### Show Brand Negative Constraints
```cypher
// What does this brand forbid?
MATCH (b:Brand {name: "stripe.com"})-[f:FORBIDS]->(b)
RETURN b.name as Brand, collect(f.constraint) as ForbiddenThings
```

---

## 3. COLOR INTELLIGENCE QUERIES (Visual DNA MOAT)

### Color Usage by Semantic Role
```cypher
// Show how colors are used across brands (primary, secondary, accent, etc.)
MATCH (b:Brand)-[r:OWNS_COLOR]->(c:Color)
RETURN 
  r.usage as ColorRole,
  count(DISTINCT c) as UniqueColors,
  count(DISTINCT b) as BrandsUsingRole,
  collect(DISTINCT c.hex)[0..5] as SampleHexCodes
ORDER BY BrandsUsingRole DESC
```

### Find Brands Using Similar Colors
```cypher
// Find brands that share color palettes
MATCH (b1:Brand {name: "stripe.com"})-[:OWNS_COLOR]->(c:Color)<-[:OWNS_COLOR]-(b2:Brand)
WHERE b1 <> b2
WITH b2, collect(DISTINCT c.hex) as SharedColors
RETURN b2.name as SimilarBrand, SharedColors, size(SharedColors) as SharedColorCount
ORDER BY SharedColorCount DESC
```

### Color Pairing Analysis (MOAT Feature)
```cypher
// Find which colors are commonly used together
MATCH (b:Brand)-[:OWNS_COLOR]->(c1:Color)
MATCH (b)-[:OWNS_COLOR]->(c2:Color)
WHERE c1.hex < c2.hex  // Avoid duplicates
WITH c1, c2, count(b) as BrandsUsingBoth
WHERE BrandsUsingBoth > 1
RETURN 
  c1.name as Color1, c1.hex as Hex1,
  c2.name as Color2, c2.hex as Hex2,
  BrandsUsingBoth
ORDER BY BrandsUsingBoth DESC
LIMIT 10
```

### Primary Color Distribution
```cypher
// What are the most popular primary colors?
MATCH (b:Brand)-[r:OWNS_COLOR {usage: "primary"}]->(c:Color)
RETURN c.hex as PrimaryColor, c.name as ColorName, count(b) as BrandCount
ORDER BY BrandCount DESC
LIMIT 10
```

---

## 4. TYPOGRAPHY INTELLIGENCE QUERIES

### Most Popular Fonts
```cypher
// Which fonts are most commonly used?
MATCH (b:Brand)-[:USES_TYPOGRAPHY]->(t:Typography)
RETURN t.family as Font, count(b) as BrandCount, collect(b.name)[0..5] as SampleBrands
ORDER BY BrandCount DESC
```

### Find Brands with Similar Typography
```cypher
// Brands using the same fonts
MATCH (b1:Brand {name: "stripe.com"})-[:USES_TYPOGRAPHY]->(t:Typography)<-[:USES_TYPOGRAPHY]-(b2:Brand)
WHERE b1 <> b2
WITH b2, collect(t.family) as SharedFonts
RETURN b2.name as SimilarBrand, SharedFonts, size(SharedFonts) as SharedFontCount
ORDER BY SharedFontCount DESC
```

---

## 5. GOVERNANCE QUERIES (Rules & Compliance MOAT)

### Rule Categories Distribution
```cypher
// What types of rules do brands have?
MATCH (b:Brand)-[:HAS_RULE]->(r:Rule)
RETURN r.category as RuleCategory, r.severity as Severity, count(*) as RuleCount
ORDER BY RuleCount DESC
```

### Critical Rules Across Brands
```cypher
// Show all critical rules (high-priority governance)
MATCH (b:Brand)-[:HAS_RULE]->(r:Rule {severity: "critical"})
RETURN b.name as Brand, r.category as Category, r.instruction as Rule
ORDER BY b.name
```

### Negative Constraint Rules
```cypher
// "Do Not" rules (negative constraints)
MATCH (b:Brand)-[:HAS_RULE]->(r:Rule {negative_constraint: true})
RETURN b.name as Brand, r.instruction as DoNotRule
ORDER BY b.name
```

---

## 6. CONTEXTUAL RULES QUERIES (Channel-Specific MOAT)

### Rules by Context/Channel
```cypher
// Show rules organized by channel (LinkedIn, Instagram, print, etc.)
MATCH (b:Brand)-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
RETURN 
  cr.context as Channel,
  count(DISTINCT b) as BrandsWithRules,
  collect(DISTINCT b.name)[0..3] as SampleBrands
ORDER BY BrandsWithRules DESC
```

### LinkedIn-Specific Rules
```cypher
// What are the LinkedIn-specific brand rules?
MATCH (b:Brand)-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
WHERE cr.context CONTAINS "linkedin"
RETURN b.name as Brand, cr.rule as LinkedInRule, cr.priority as Priority
ORDER BY cr.priority DESC
```

### High-Priority Contextual Rules
```cypher
// Show the most important channel-specific rules
MATCH (b:Brand)-[:HAS_CONTEXTUAL_RULE]->(cr:ContextualRule)
WHERE cr.priority >= 8
RETURN b.name as Brand, cr.context as Channel, cr.rule as Rule, cr.priority as Priority
ORDER BY cr.priority DESC, b.name
```

---

## 7. ASSET GRAPH QUERIES (Asset Inventory MOAT)

### Logo Variants by Brand
```cypher
// Show all logo variants for each brand
MATCH (b:Brand)-[l:HAS_LOGO]->(b)
RETURN b.name as Brand, collect(l.variant) as LogoVariants, count(l) as VariantCount
ORDER BY VariantCount DESC
```

### Template Inventory
```cypher
// Show all templates across brands
MATCH (b:Brand)-[t:HAS_TEMPLATE]->(b)
RETURN b.name as Brand, collect(t.name) as Templates, count(t) as TemplateCount
ORDER BY TemplateCount DESC
```

### Complete Asset Inventory
```cypher
// Full asset inventory for a brand
MATCH (b:Brand {name: "stripe.com"})
OPTIONAL MATCH (b)-[l:HAS_LOGO]->(b)
OPTIONAL MATCH (b)-[t:HAS_TEMPLATE]->(b)
OPTIONAL MATCH (b)-[p:HAS_PATTERN]->(b)
RETURN 
  b.name as Brand,
  collect(DISTINCT l.variant) as LogoVariants,
  collect(DISTINCT t.name) as Templates,
  collect(DISTINCT p.name) as Patterns
```

---

## 8. CROSS-BRAND INTELLIGENCE QUERIES (Network Effects MOAT)

### Brand Similarity Score
```cypher
// Calculate similarity between brands based on multiple factors
MATCH (b1:Brand {name: "stripe.com"})
MATCH (b2:Brand)
WHERE b1 <> b2

// Shared colors
OPTIONAL MATCH (b1)-[:OWNS_COLOR]->(c:Color)<-[:OWNS_COLOR]-(b2)
WITH b1, b2, count(DISTINCT c) as SharedColors

// Shared fonts
OPTIONAL MATCH (b1)-[:USES_TYPOGRAPHY]->(t:Typography)<-[:USES_TYPOGRAPHY]-(b2)
WITH b1, b2, SharedColors, count(DISTINCT t) as SharedFonts

// Shared archetype
OPTIONAL MATCH (b1)-[:HAS_ARCHETYPE]->(a:Archetype)<-[:HAS_ARCHETYPE]-(b2)
WITH b1, b2, SharedColors, SharedFonts, count(a) as SameArchetype

// Calculate similarity score
WITH b2, 
     (SharedColors * 2 + SharedFonts * 3 + SameArchetype * 5) as SimilarityScore
WHERE SimilarityScore > 0
RETURN b2.name as SimilarBrand, SimilarityScore
ORDER BY SimilarityScore DESC
LIMIT 10
```

### Industry Trend Analysis
```cypher
// What are the most common brand characteristics?
MATCH (b:Brand)
OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
OPTIONAL MATCH (b)-[r:OWNS_COLOR {usage: "primary"}]->(c:Color)
RETURN 
  a.name as MostCommonArchetype,
  count(DISTINCT b) as BrandCount,
  collect(DISTINCT c.hex)[0..5] as CommonPrimaryColors
ORDER BY BrandCount DESC
LIMIT 5
```

### Brand Complexity Score
```cypher
// Measure brand governance complexity
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
```

---

## 9. MOAT VALIDATION QUERIES

### Check MOAT Structure Completeness
```cypher
// Verify which brands have complete MOAT structure
MATCH (b:Brand)
OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
OPTIONAL MATCH (b)-[v:HAS_VOICE_VECTOR]->(b)
OPTIONAL MATCH (b)-[f:FORBIDS]->(b)
OPTIONAL MATCH (b)-[:HAS_CONTEXTUAL_RULE]->(cr)
OPTIONAL MATCH (b)-[l:HAS_LOGO]->(b)
RETURN 
  b.name as Brand,
  CASE WHEN a IS NOT NULL THEN '✓' ELSE '✗' END as HasArchetype,
  count(DISTINCT v) as VoiceVectors,
  count(DISTINCT f) as NegativeConstraints,
  count(DISTINCT cr) as ContextualRules,
  count(DISTINCT l) as LogoVariants,
  CASE 
    WHEN a IS NOT NULL AND count(DISTINCT v) > 0 THEN 'COMPLETE'
    ELSE 'INCOMPLETE'
  END as MOATStatus
ORDER BY b.created_at DESC
```

### Data Richness Report
```cypher
// Show how much data each brand has (lock-in strength)
MATCH (b:Brand)
OPTIONAL MATCH (b)-[r]->(n)
WITH b, type(r) as RelType, count(n) as RelCount
RETURN 
  b.name as Brand,
  collect(RelType + ': ' + RelCount) as DataInventory,
  sum(RelCount) as TotalDataPoints
ORDER BY TotalDataPoints DESC
```

---

## 10. COMPETITIVE ADVANTAGE QUERIES

### Unique Brand Insights
```cypher
// What makes each brand unique?
MATCH (b:Brand)
OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
OPTIONAL MATCH (b)-[r:OWNS_COLOR {usage: "primary"}]->(c:Color)
OPTIONAL MATCH (b)-[:USES_TYPOGRAPHY]->(t:Typography)
RETURN 
  b.name as Brand,
  a.name as Archetype,
  collect(DISTINCT c.hex)[0..3] as PrimaryColors,
  collect(DISTINCT t.family)[0..2] as Fonts
ORDER BY b.name
```

### Migration Difficulty Score
```cypher
// Calculate how hard it would be for a client to leave (MOAT strength)
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
```

---

## HOW TO RUN THESE QUERIES

### Option 1: Neo4j Browser
1. Go to https://console.neo4j.io/
2. Open your database
3. Click "Query" tab
4. Copy/paste any query above
5. Click "Run" or press Ctrl+Enter

### Option 2: Python Script (see below)

### Option 3: Neo4j Bloom (Visual Exploration)
1. Open Neo4j Bloom
2. Search for "Brand"
3. Expand relationships visually
4. Use natural language: "Show me brands with similar colors"

---

## EXPECTED RESULTS (After Full MOAT Implementation)

With complete MOAT structure, you should see:

✅ **Identity Core**
- Archetype nodes shared across brands
- Voice vector self-loops on Brand nodes
- Negative constraint self-loops

✅ **Visual DNA**
- Color nodes with semantic roles (primary, secondary, accent)
- Typography nodes with usage context

✅ **Governance**
- Rule nodes with severity levels
- ContextualRule nodes for channel-specific rules

✅ **Asset Graph**
- Logo variant self-loops (primary, reversed, icon)
- Template self-loops
- Pattern self-loops

✅ **Relationship Intelligence**
- Brand similarity queries work
- Color pairing analysis shows patterns
- Voice profile matching finds similar brands

---

## MOAT VALUE DEMONSTRATION

Run these queries to show stakeholders:

1. **"Find brands like ours"** → Brand Similarity Score query
2. **"What colors work well together?"** → Color Pairing Analysis
3. **"Show LinkedIn-specific rules"** → Contextual Rules by Channel
4. **"How complex is our brand?"** → Brand Complexity Score
5. **"How hard to migrate?"** → Migration Difficulty Score

These queries demonstrate value that competitors (Midjourney, DALL-E, Canva) **cannot provide** because they don't have the structured Brand Graph.
