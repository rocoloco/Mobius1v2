# Brand Graph API - The Data Moat

## Overview

The Brand Graph API exposes your brand as a machine-readable "operating system" that creates lock-in by becoming the single source of truth for brand identity across an organization.

---

## The MOAT Strategy

### Why This Creates Lock-In

1. **Developers Integrate It** - Internal dev teams at client companies will use `GET /v1/brands/{id}/graph` to fetch official hex codes, fonts, and rules for their apps
2. **Single Source of Truth** - The Brand Graph becomes the authoritative definition of the brand, not the PDF
3. **Hard to Migrate** - Competitors would need to replicate the entire structured schema, not just generate images
4. **Network Effects** - More integrations = more lock-in = higher switching costs

---

## API Endpoint

### GET /v1/brands/{brand_id}/graph

Returns the complete Brand Graph with all structured brand data.

**Example Request:**
```bash
curl https://api.mobius.com/v1/brands/b_123/graph \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "brand_id": "b_123",
  "name": "Acme Corp",
  "version": "2.1.0",
  
  "identity_core": {
    "archetype": "The Sage",
    "voice_vectors": {
      "formal": 0.8,
      "witty": 0.2,
      "urgent": 0.0,
      "technical": 0.6
    },
    "negative_constraints": [
      "No drop shadows",
      "No neon colors",
      "Never use gradients on text"
    ]
  },
  
  "visual_tokens": {
    "colors": [
      {
        "hex": "#FF5733",
        "name": "Acme Red",
        "semantic_role": "primary",
        "usage_weight": 0.6,
        "context": "Use for CTAs and headers"
      },
      {
        "hex": "#FFFFFF",
        "name": "White",
        "semantic_role": "neutral",
        "usage_weight": 0.3,
        "context": "Backgrounds and negative space"
      }
    ],
    "typography": [
      {
        "family": "Inter",
        "weights": ["400", "700"],
        "usage": "Headings and body text"
      }
    ],
    "logos": [
      {
        "variant": "primary",
        "url": "https://cdn.mobius.com/brands/b_123/logo_main.svg",
        "min_width_px": 100,
        "clear_space_ratio": 0.25,
        "forbidden_backgrounds": ["#FF0000", "#00FF00"]
      }
    ]
  },
  
  "contextual_rules": [
    {
      "context": "social_media_linkedin",
      "rule": "Images must contain human subjects; 20% overlay opacity maximum",
      "priority": 10,
      "applies_to": ["image"]
    },
    {
      "context": "print_packaging",
      "rule": "CMYK only; minimal whitespace 15mm",
      "priority": 8,
      "applies_to": ["image", "document"]
    }
  ],
  
  "asset_graph": {
    "logos": {
      "primary": "https://cdn.mobius.com/brands/b_123/logo_main.svg",
      "reversed": "https://cdn.mobius.com/brands/b_123/logo_white.svg",
      "icon": "https://cdn.mobius.com/brands/b_123/logo_icon.png"
    },
    "templates": {
      "social_post": "https://cdn.mobius.com/brands/b_123/template_social.json",
      "email_header": "https://cdn.mobius.com/brands/b_123/template_email.json"
    },
    "patterns": {
      "background_texture": "https://cdn.mobius.com/brands/b_123/texture_bg.png"
    },
    "photography_style": "https://cdn.mobius.com/brands/b_123/photo_guide.pdf"
  },
  
  "relationships": {
    "color_count": 5,
    "colors_with_usage": [
      {
        "hex": "#FF5733",
        "name": "Acme Red",
        "usage": "primary",
        "usage_weight": 0.6
      }
    ]
  },
  
  "metadata": {
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-02-20T14:22:00Z",
    "source_filename": "acme_brand_guidelines_v2.pdf",
    "ingested_at": "2025-01-15T10:35:00Z"
  }
}
```

---

## Use Cases (Lock-In Scenarios)

### 1. Internal Design System Integration

**Scenario:** Client's design team builds a React component library

```javascript
// Client's internal code becomes dependent on Mobius API
import { useBrandGraph } from '@acme/design-system';

function Button({ variant }) {
  const { visual_tokens } = useBrandGraph('b_123');
  const color = variant === 'primary' 
    ? visual_tokens.colors.find(c => c.semantic_role === 'primary').hex
    : visual_tokens.colors.find(c => c.semantic_role === 'secondary').hex;
  
  return <button style={{ backgroundColor: color }}>Click Me</button>;
}
```

**Lock-In:** Their entire component library now depends on your API. Switching would require rewriting all components.

---

### 2. Marketing Automation Platform

**Scenario:** Client's marketing team uses HubSpot/Marketo with custom integration

```python
# Client's marketing automation script
import requests

def create_email_campaign(subject, body):
    # Fetch brand colors from Mobius
    brand = requests.get('https://api.mobius.com/v1/brands/b_123/graph').json()
    primary_color = next(c['hex'] for c in brand['visual_tokens']['colors'] 
                         if c['semantic_role'] == 'primary')
    
    # Apply brand colors to email template
    email_html = f"""
    <html>
      <body style="background: {primary_color}">
        {body}
      </body>
    </html>
    """
    
    # Send via HubSpot
    send_email(email_html)
```

**Lock-In:** Their entire marketing automation depends on your API for brand consistency.

---

### 3. Multi-Brand Enterprise Dashboard

**Scenario:** Enterprise client with 50+ brands needs centralized brand management

```typescript
// Client's internal brand dashboard
async function BrandDashboard() {
  const brands = await Promise.all(
    brandIds.map(id => 
      fetch(`https://api.mobius.com/v1/brands/${id}/graph`).then(r => r.json())
    )
  );
  
  return (
    <div>
      {brands.map(brand => (
        <BrandCard 
          key={brand.brand_id}
          name={brand.name}
          colors={brand.visual_tokens.colors}
          archetype={brand.identity_core.archetype}
        />
      ))}
    </div>
  );
}
```

**Lock-In:** Their entire brand management infrastructure is built on your API.

---

### 4. Context-Aware Asset Generation

**Scenario:** Client needs different rules for LinkedIn vs. Instagram

```python
# Client's social media automation tool
def generate_social_post(platform: str, content: str):
    brand = requests.get('https://api.mobius.com/v1/brands/b_123/graph').json()
    
    # Get context-specific rules
    context = f"social_media_{platform.lower()}"
    rules = [r for r in brand['contextual_rules'] if r['context'] == context]
    
    # Apply rules to generation
    for rule in sorted(rules, key=lambda r: r['priority'], reverse=True):
        print(f"Applying rule: {rule['rule']}")
    
    # Generate with Mobius
    return requests.post('https://api.mobius.com/v1/generate', json={
        'brand_id': 'b_123',
        'prompt': content,
        'context': context
    })
```

**Lock-In:** Their social media automation is tightly coupled to your contextual rules.

---

## Schema Evolution (Version Control)

The Brand Graph includes a `version` field to support schema evolution:

```json
{
  "version": "2.1.0",
  "identity_core": { ... }
}
```

**Versioning Strategy:**
- **Major version** (2.0.0 → 3.0.0): Breaking changes to schema
- **Minor version** (2.0.0 → 2.1.0): New fields added (backward compatible)
- **Patch version** (2.1.0 → 2.1.1): Bug fixes or data corrections

This allows clients to pin to specific versions while you evolve the schema.

---

## Monetization Tiers

### Free Tier
- Basic Brand Graph (colors, typography, logos)
- 1,000 API calls/month
- Single brand

### Pro Tier ($99/mo)
- Full Brand Graph (identity core, contextual rules, asset graph)
- 50,000 API calls/month
- Up to 10 brands
- Webhook notifications on brand updates

### Enterprise Tier ($999/mo)
- Unlimited API calls
- Unlimited brands
- Custom voice vectors
- Dedicated support
- SLA guarantees
- On-premise deployment option

---

## Migration Difficulty (Why Competitors Can't Replicate)

To migrate away from Mobius, a client would need to:

1. **Extract all structured data** - Not just the PDF, but the entire Brand Graph
2. **Replicate the schema** - Build equivalent Pydantic models with all fields
3. **Rewrite all integrations** - Update every internal tool that calls the API
4. **Migrate contextual rules** - Manually recreate channel-specific governance
5. **Rebuild asset graph** - Re-upload and re-link all brand assets
6. **Update voice vectors** - Recalibrate tone settings for new platform

**Estimated migration cost:** 200-500 engineering hours = $50k-$150k

**Result:** Clients stay because switching is too expensive.

---

## Next Steps

1. ✅ **Schema implemented** - New fields added to `BrandGuidelines` model
2. ✅ **API endpoint enhanced** - `GET /v1/brands/{id}/graph` returns full graph
3. 🔄 **Update ingestion** - Modify PDF parser to extract identity core and contextual rules
4. 🔄 **Add webhooks** - Notify clients when brand graph changes
5. 🔄 **Build SDKs** - Create JavaScript/Python SDKs for easy integration
6. 🔄 **Documentation** - Publish integration guides for common use cases

---

## Competitive Advantage

**Midjourney/DALL-E:** Just generate images, no structured brand data
**Canva:** Templates only, no programmatic API for brand system
**Figma:** Design tool, not a brand operating system
**Adobe Express:** Closed ecosystem, no API access

**Mobius:** The only platform that exposes the brand as a machine-readable graph with an API, creating true lock-in through developer integrations.
