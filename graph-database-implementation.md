# Graph Database Implementation Plan

## Overview
Implement hybrid PostgreSQL + Neo4j Aura architecture for Mobius brand governance system, enabling relationship intelligence and competitive moat through advanced graph queries.

---

## Phase 1: Infrastructure Setup (Week 1, Days 1-2)

### Task 1.1: Neo4j Aura Free Tier Setup
**Prerequisites:**
- Neo4j Aura account (free tier: 200k nodes, 400k relationships)
- Get connection URI, username, password

**Deliverables:**
- Neo4j Aura database instance
- Connection credentials stored in environment variables
- Test connection successful

### Task 1.2: Add Neo4j Dependencies
**File:** `src/mobius/api/app.py`

**Changes:**
```python
# Add to image definition packages
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    ...,
    "neo4j>=5.14.0",  # ← ADD: Neo4j Python driver
)
```

### Task 1.3: Add Configuration
**File:** `src/mobius/config.py`

**Changes:**
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Neo4j Graph Database
    neo4j_uri: str = Field(default="", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="", env="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", env="NEO4J_DATABASE")
    graph_sync_enabled: bool = Field(default=True, env="GRAPH_SYNC_ENABLED")
```

---

## Phase 2: Graph Storage Layer (Week 1, Days 3-5)

### Task 2.1: Create GraphStorage Class
**New File:** `src/mobius/storage/graph.py`

**Implementation:**
```python
"""
Graph database storage layer using Neo4j.

Maintains dual-write synchronization between PostgreSQL (source of truth)
and Neo4j (relationship queries).
"""

import asyncio
from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable
import structlog

from mobius.config import settings
from mobius.models.brand import Brand, Color
from mobius.models.asset import Asset
from mobius.models.template import Template

logger = structlog.get_logger()


class GraphStorage:
    """
    Neo4j graph database storage for relationship intelligence.

    Design Principles:
    - PostgreSQL remains source of truth
    - Neo4j is read-optimized for graph queries
    - Sync failures are logged but don't block PostgreSQL writes
    - All graph operations are idempotent (safe to retry)
    """

    def __init__(self):
        """Initialize Neo4j driver connection."""
        if not settings.neo4j_uri:
            logger.warning("neo4j_not_configured", message="Neo4j URI not set, graph features disabled")
            self.driver = None
            return

        self.driver: AsyncDriver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            database=settings.neo4j_database
        )

        logger.info(
            "neo4j_connected",
            uri=settings.neo4j_uri,
            database=settings.neo4j_database
        )

    async def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            await self.driver.close()

    def _is_enabled(self) -> bool:
        """Check if graph sync is enabled and configured."""
        return settings.graph_sync_enabled and self.driver is not None

    async def sync_brand(self, brand: Brand) -> None:
        """
        Create or update Brand node and its Color relationships in Neo4j.

        Creates:
        - (:Brand) node
        - (:Color) nodes for each color in guidelines
        - (Brand)-[:OWNS_COLOR]->(Color) relationships

        Idempotent: Safe to call multiple times for same brand.
        """
        if not self._is_enabled():
            return

        try:
            async with self.driver.session() as session:
                # MERGE Brand node (create or update)
                await session.run(
                    """
                    MERGE (b:Brand {brand_id: $brand_id})
                    SET b.organization_id = $organization_id,
                        b.name = $name,
                        b.learning_active = $learning_active,
                        b.feedback_count = $feedback_count,
                        b.created_at = datetime($created_at),
                        b.updated_at = datetime($updated_at)
                    """,
                    brand_id=brand.brand_id,
                    organization_id=brand.organization_id,
                    name=brand.name,
                    learning_active=brand.learning_active,
                    feedback_count=brand.feedback_count,
                    created_at=brand.created_at,
                    updated_at=brand.updated_at
                )

                # Sync Color nodes and OWNS_COLOR relationships
                if brand.guidelines and brand.guidelines.colors:
                    for color in brand.guidelines.colors:
                        await self._sync_color_relationship(
                            session, brand.brand_id, color
                        )

                logger.info(
                    "brand_synced_to_graph",
                    brand_id=brand.brand_id,
                    color_count=len(brand.guidelines.colors) if brand.guidelines else 0
                )

        except Exception as e:
            # Log error but don't fail the main operation
            logger.error(
                "graph_sync_failed",
                entity="brand",
                brand_id=brand.brand_id,
                error=str(e)
            )

    async def _sync_color_relationship(
        self, session: AsyncSession, brand_id: str, color: Color
    ) -> None:
        """
        Sync individual Color node and Brand → Color relationship.

        Creates:
        - (:Color) node with hex as primary key
        - (Brand)-[:OWNS_COLOR {usage, usage_weight}]->(Color)
        """
        await session.run(
            """
            MATCH (b:Brand {brand_id: $brand_id})
            MERGE (c:Color {hex: $hex})
            SET c.name = $name
            MERGE (b)-[r:OWNS_COLOR]->(c)
            SET r.usage = $usage,
                r.usage_weight = $usage_weight,
                r.context = $context
            """,
            brand_id=brand_id,
            hex=color.hex,
            name=color.name,
            usage=color.usage,
            usage_weight=color.usage_weight,
            context=color.context
        )

    async def sync_asset(self, asset: Asset) -> None:
        """
        Create or update Asset node and link to Brand.

        Creates:
        - (:Asset) node
        - (Brand)-[:GENERATED_ASSET]->(Asset)

        Future: Could extract colors from asset and create USES_COLOR edges
        """
        if not self._is_enabled():
            return

        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    MATCH (b:Brand {brand_id: $brand_id})
                    MERGE (a:Asset {asset_id: $asset_id})
                    SET a.prompt = $prompt,
                        a.image_url = $image_url,
                        a.compliance_score = $compliance_score,
                        a.status = $status,
                        a.created_at = datetime($created_at)
                    MERGE (b)-[:GENERATED_ASSET]->(a)
                    """,
                    brand_id=asset.brand_id,
                    asset_id=asset.asset_id,
                    prompt=asset.prompt,
                    image_url=asset.image_url,
                    compliance_score=asset.compliance_score,
                    status=asset.status,
                    created_at=asset.created_at.isoformat()
                )

                logger.info(
                    "asset_synced_to_graph",
                    asset_id=asset.asset_id,
                    brand_id=asset.brand_id
                )

        except Exception as e:
            logger.error(
                "graph_sync_failed",
                entity="asset",
                asset_id=asset.asset_id,
                error=str(e)
            )

    async def sync_feedback(
        self, feedback_id: str, asset_id: str, brand_id: str,
        action: str, reason: Optional[str], timestamp: str
    ) -> None:
        """
        Create Feedback relationship between Asset and Brand.

        Creates:
        - (Asset)-[:RECEIVED_FEEDBACK {action, reason, timestamp}]->(Asset)

        Note: Using self-loop on Asset for now. Could create User nodes later.
        """
        if not self._is_enabled():
            return

        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    MATCH (a:Asset {asset_id: $asset_id})
                    MATCH (b:Brand {brand_id: $brand_id})
                    CREATE (a)-[:RECEIVED_FEEDBACK {
                        feedback_id: $feedback_id,
                        action: $action,
                        reason: $reason,
                        timestamp: datetime($timestamp)
                    }]->(a)
                    """,
                    feedback_id=feedback_id,
                    asset_id=asset_id,
                    brand_id=brand_id,
                    action=action,
                    reason=reason,
                    timestamp=timestamp
                )

                logger.info(
                    "feedback_synced_to_graph",
                    feedback_id=feedback_id,
                    asset_id=asset_id,
                    action=action
                )

        except Exception as e:
            logger.error(
                "graph_sync_failed",
                entity="feedback",
                feedback_id=feedback_id,
                error=str(e)
            )

    async def sync_template(self, template: Template) -> None:
        """
        Create or update Template node and relationships.

        Creates:
        - (:Template) node
        - (Brand)-[:HAS_TEMPLATE]->(Template)
        - (Template)-[:BASED_ON_ASSET]->(Asset) if source_asset_id exists
        """
        if not self._is_enabled():
            return

        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    MATCH (b:Brand {brand_id: $brand_id})
                    MERGE (t:Template {template_id: $template_id})
                    SET t.name = $name,
                        t.description = $description,
                        t.created_at = datetime($created_at)
                    MERGE (b)-[:HAS_TEMPLATE]->(t)
                    """,
                    brand_id=template.brand_id,
                    template_id=template.template_id,
                    name=template.name,
                    description=template.description,
                    created_at=template.created_at.isoformat()
                )

                # Link to source asset if exists
                if template.source_asset_id:
                    await session.run(
                        """
                        MATCH (t:Template {template_id: $template_id})
                        MATCH (a:Asset {asset_id: $source_asset_id})
                        MERGE (t)-[:BASED_ON_ASSET]->(a)
                        """,
                        template_id=template.template_id,
                        source_asset_id=template.source_asset_id
                    )

                logger.info(
                    "template_synced_to_graph",
                    template_id=template.template_id,
                    brand_id=template.brand_id
                )

        except Exception as e:
            logger.error(
                "graph_sync_failed",
                entity="template",
                template_id=template.template_id,
                error=str(e)
            )

    # --- GRAPH QUERY METHODS (Read-only) ---

    async def get_brand_colors(self, brand_id: str) -> List[Dict[str, Any]]:
        """
        Get all colors for a brand with their usage context.

        Returns:
        [
            {
                "hex": "#0057B8",
                "name": "Midnight Blue",
                "usage": "primary",
                "usage_weight": 0.6,
                "context": "Headers and CTAs"
            },
            ...
        ]
        """
        if not self._is_enabled():
            return []

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (b:Brand {brand_id: $brand_id})-[r:OWNS_COLOR]->(c:Color)
                    RETURN c.hex as hex,
                           c.name as name,
                           r.usage as usage,
                           r.usage_weight as usage_weight,
                           r.context as context
                    ORDER BY r.usage_weight DESC
                    """,
                    brand_id=brand_id
                )

                return [dict(record) async for record in result]

        except Exception as e:
            logger.error(
                "graph_query_failed",
                query="get_brand_colors",
                brand_id=brand_id,
                error=str(e)
            )
            return []

    async def find_brands_using_color(self, hex: str) -> List[Dict[str, Any]]:
        """
        Find all brands using a specific color.

        Returns:
        [
            {
                "brand_id": "...",
                "brand_name": "Acme Corp",
                "usage": "primary",
                "usage_weight": 0.6
            },
            ...
        ]
        """
        if not self._is_enabled():
            return []

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (b:Brand)-[r:OWNS_COLOR]->(c:Color {hex: $hex})
                    RETURN b.brand_id as brand_id,
                           b.name as brand_name,
                           r.usage as usage,
                           r.usage_weight as usage_weight
                    ORDER BY r.usage_weight DESC
                    """,
                    hex=hex
                )

                return [dict(record) async for record in result]

        except Exception as e:
            logger.error(
                "graph_query_failed",
                query="find_brands_using_color",
                hex=hex,
                error=str(e)
            )
            return []

    async def find_color_pairings(
        self, hex: str, min_sample_count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find colors that pair well with a given color based on approved assets.

        This is a MOAT FEATURE - hard to replicate with flat lists.

        Query Logic:
        1. Find assets using color X
        2. Find other colors used in those same assets
        3. Filter for assets with approve feedback
        4. Count pairing frequency
        5. Return top color pairings

        Returns:
        [
            {
                "paired_hex": "#FFFFFF",
                "paired_name": "White",
                "pairing_count": 12,
                "avg_compliance_score": 0.92
            },
            ...
        ]
        """
        if not self._is_enabled():
            return []

        try:
            async with self.driver.session() as session:
                # Note: Requires USES_COLOR edges (future enhancement)
                # For MVP, return empty list until we extract colors from assets
                result = await session.run(
                    """
                    MATCH (c1:Color {hex: $hex})<-[:USES_COLOR]-(a:Asset)-[:USES_COLOR]->(c2:Color)
                    WHERE c1.hex <> c2.hex
                      AND (a)-[:RECEIVED_FEEDBACK {action: 'approve'}]->()
                    WITH c2, COUNT(a) as pairing_count, AVG(a.compliance_score) as avg_score
                    WHERE pairing_count >= $min_sample_count
                    RETURN c2.hex as paired_hex,
                           c2.name as paired_name,
                           pairing_count,
                           avg_score as avg_compliance_score
                    ORDER BY pairing_count DESC
                    LIMIT 10
                    """,
                    hex=hex,
                    min_sample_count=min_sample_count
                )

                return [dict(record) async for record in result]

        except Exception as e:
            logger.error(
                "graph_query_failed",
                query="find_color_pairings",
                hex=hex,
                error=str(e)
            )
            return []

    async def find_similar_brands(
        self, brand_id: str, min_shared_colors: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find brands with similar color palettes.

        Returns:
        [
            {
                "similar_brand_id": "...",
                "similar_brand_name": "...",
                "shared_colors": ["#0057B8", "#FFFFFF"],
                "shared_color_count": 3,
                "similarity_score": 0.67
            },
            ...
        ]
        """
        if not self._is_enabled():
            return []

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (b1:Brand {brand_id: $brand_id})-[:OWNS_COLOR]->(c:Color)<-[:OWNS_COLOR]-(b2:Brand)
                    WHERE b1.organization_id <> b2.organization_id
                    WITH b1, b2, COLLECT(c.hex) as shared_colors
                    WHERE SIZE(shared_colors) >= $min_shared_colors
                    MATCH (b1)-[:OWNS_COLOR]->(all_b1_colors:Color)
                    MATCH (b2)-[:OWNS_COLOR]->(all_b2_colors:Color)
                    WITH b2, shared_colors,
                         SIZE(shared_colors) as shared_count,
                         COUNT(DISTINCT all_b1_colors) as b1_total,
                         COUNT(DISTINCT all_b2_colors) as b2_total
                    RETURN b2.brand_id as similar_brand_id,
                           b2.name as similar_brand_name,
                           shared_colors,
                           shared_count as shared_color_count,
                           toFloat(shared_count) / (b1_total + b2_total - shared_count) as similarity_score
                    ORDER BY similarity_score DESC
                    LIMIT 5
                    """,
                    brand_id=brand_id,
                    min_shared_colors=min_shared_colors
                )

                return [dict(record) async for record in result]

        except Exception as e:
            logger.error(
                "graph_query_failed",
                query="find_similar_brands",
                brand_id=brand_id,
                error=str(e)
            )
            return []


# Global instance
graph_storage = GraphStorage()
```

### Task 2.2: Add Dual-Write to BrandStorage
**File:** `src/mobius/storage/brands.py`

**Changes:**
```python
from mobius.storage.graph import graph_storage  # ADD import

class BrandStorage:
    async def create_brand(self, brand: Brand) -> Brand:
        # ... existing PostgreSQL insert ...
        result = self.client.table("brands").insert(data).execute()
        created_brand = Brand.model_validate(result.data[0])

        # ADD: Sync to Neo4j (non-blocking)
        try:
            await graph_storage.sync_brand(created_brand)
        except Exception as e:
            logger.warning("graph_sync_skipped", brand_id=created_brand.brand_id, error=str(e))

        return created_brand

    async def update_brand(self, brand_id: str, updates: dict) -> Brand:
        # ... existing PostgreSQL update ...
        result = self.client.table("brands").update(updates).execute()
        updated_brand = Brand.model_validate(result.data[0])

        # ADD: Sync to Neo4j
        try:
            await graph_storage.sync_brand(updated_brand)
        except Exception as e:
            logger.warning("graph_sync_skipped", brand_id=brand_id, error=str(e))

        return updated_brand
```

### Task 2.3: Add Dual-Write to AssetStorage
**File:** `src/mobius/storage/assets.py`

**Changes:**
```python
from mobius.storage.graph import graph_storage  # ADD import

class AssetStorage:
    async def create_asset(self, asset: Asset) -> Asset:
        # ... existing PostgreSQL insert ...
        result = self.client.table("assets").insert(data).execute()
        created_asset = Asset.model_validate(result.data[0])

        # ADD: Sync to Neo4j
        try:
            await graph_storage.sync_asset(created_asset)
        except Exception as e:
            logger.warning("graph_sync_skipped", asset_id=created_asset.asset_id, error=str(e))

        return created_asset
```

### Task 2.4: Add Dual-Write to FeedbackStorage
**File:** `src/mobius/storage/feedback.py`

**Changes:**
```python
from mobius.storage.graph import graph_storage  # ADD import

class FeedbackStorage:
    async def create_feedback(self, asset_id: str, brand_id: str, action: str, reason: Optional[str] = None) -> Feedback:
        # ... existing PostgreSQL insert ...
        result = self.client.table("feedback").insert(data).execute()
        created_feedback = Feedback.model_validate(result.data[0])

        # ADD: Sync to Neo4j
        try:
            await graph_storage.sync_feedback(
                feedback_id=created_feedback.feedback_id,
                asset_id=asset_id,
                brand_id=brand_id,
                action=action,
                reason=reason,
                timestamp=created_feedback.created_at.isoformat()
            )
        except Exception as e:
            logger.warning("graph_sync_skipped", feedback_id=created_feedback.feedback_id, error=str(e))

        return created_feedback
```

### Task 2.5: Add Dual-Write to TemplateStorage
**File:** `src/mobius/storage/templates.py`

**Changes:**
```python
from mobius.storage.graph import graph_storage  # ADD import

class TemplateStorage:
    async def create_template(self, template: Template) -> Template:
        # ... existing PostgreSQL insert ...
        result = self.client.table("templates").insert(data).execute()
        created_template = Template.model_validate(result.data[0])

        # ADD: Sync to Neo4j
        try:
            await graph_storage.sync_template(created_template)
        except Exception as e:
            logger.warning("graph_sync_skipped", template_id=created_template.template_id, error=str(e))

        return created_template
```

---

## Phase 3: Graph Query API Endpoints (Week 2, Days 1-3)

### Task 3.1: Add Graph Query Route Handlers
**File:** `src/mobius/api/routes.py`

**Add new handlers:**
```python
from mobius.storage.graph import graph_storage

async def get_brand_graph_handler(request: dict) -> dict:
    """
    GET /v1/brands/{brand_id}/graph

    Get graph relationships for a brand.
    """
    brand_id = request["path_params"]["brand_id"]
    request_id = request.get("headers", {}).get("x-request-id", "unknown")

    logger.info(
        "brand_graph_request",
        request_id=request_id,
        brand_id=brand_id
    )

    # Get brand colors from graph
    colors = await graph_storage.get_brand_colors(brand_id)

    return {
        "brand_id": brand_id,
        "colors": colors,
        "relationships": {
            "color_count": len(colors)
        }
    }

async def find_color_relationships_handler(request: dict) -> dict:
    """
    GET /v1/colors/{hex}/brands

    Find all brands using a specific color.
    """
    hex_code = request["path_params"]["hex"]
    if not hex_code.startswith("#"):
        hex_code = f"#{hex_code}"

    request_id = request.get("headers", {}).get("x-request-id", "unknown")

    logger.info(
        "color_relationships_request",
        request_id=request_id,
        hex=hex_code
    )

    brands = await graph_storage.find_brands_using_color(hex_code)

    return {
        "color": hex_code,
        "brands": brands,
        "brand_count": len(brands)
    }

async def find_similar_brands_handler(request: dict) -> dict:
    """
    GET /v1/brands/{brand_id}/similar

    Find brands with similar color palettes.
    """
    brand_id = request["path_params"]["brand_id"]
    min_shared_colors = int(request.get("query_params", {}).get("min_shared_colors", 3))
    request_id = request.get("headers", {}).get("x-request-id", "unknown")

    logger.info(
        "similar_brands_request",
        request_id=request_id,
        brand_id=brand_id,
        min_shared_colors=min_shared_colors
    )

    similar_brands = await graph_storage.find_similar_brands(
        brand_id, min_shared_colors
    )

    return {
        "brand_id": brand_id,
        "similar_brands": similar_brands,
        "count": len(similar_brands)
    }

async def find_color_pairings_handler(request: dict) -> dict:
    """
    GET /v1/colors/{hex}/pairings

    Find colors that pair well with a given color.
    MOAT FEATURE - relationship intelligence.
    """
    hex_code = request["path_params"]["hex"]
    if not hex_code.startswith("#"):
        hex_code = f"#{hex_code}"

    min_samples = int(request.get("query_params", {}).get("min_samples", 5))
    request_id = request.get("headers", {}).get("x-request-id", "unknown")

    logger.info(
        "color_pairings_request",
        request_id=request_id,
        hex=hex_code,
        min_samples=min_samples
    )

    pairings = await graph_storage.find_color_pairings(hex_code, min_samples)

    return {
        "color": hex_code,
        "pairings": pairings,
        "pairing_count": len(pairings)
    }
```

### Task 3.2: Register Graph Endpoints
**File:** `src/mobius/api/app.py`

**Add endpoints:**
```python
@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-brand-graph")
async def v1_brand_graph(request: dict):
    """GET /v1/brands/{brand_id}/graph - Get brand graph relationships"""
    from mobius.api.routes import get_brand_graph_handler
    return await get_brand_graph_handler(request)

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-color-relationships")
async def v1_color_relationships(request: dict):
    """GET /v1/colors/{hex}/brands - Find brands using a color"""
    from mobius.api.routes import find_color_relationships_handler
    return await find_color_relationships_handler(request)

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-similar-brands")
async def v1_similar_brands(request: dict):
    """GET /v1/brands/{brand_id}/similar - Find similar brands"""
    from mobius.api.routes import find_similar_brands_handler
    return await find_similar_brands_handler(request)

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-color-pairings")
async def v1_color_pairings(request: dict):
    """GET /v1/colors/{hex}/pairings - Color pairing intelligence (MOAT)"""
    from mobius.api.routes import find_color_pairings_handler
    return await find_color_pairings_handler(request)
```

---

## Phase 4: Data Migration & Backfill (Week 2, Days 4-5)

### Task 4.1: Create Migration Script
**New File:** `scripts/backfill_graph_database.py`

**Purpose:** Backfill existing PostgreSQL data into Neo4j

```python
"""
Backfill existing PostgreSQL data into Neo4j graph database.

Usage:
    python scripts/backfill_graph_database.py --dry-run
    python scripts/backfill_graph_database.py --execute
"""

import asyncio
import argparse
from mobius.storage.brands import BrandStorage
from mobius.storage.assets import AssetStorage
from mobius.storage.feedback import FeedbackStorage
from mobius.storage.templates import TemplateStorage
from mobius.storage.graph import graph_storage
import structlog

logger = structlog.get_logger()

async def backfill_brands(dry_run: bool = True):
    """Backfill all brands and their colors."""
    brand_storage = BrandStorage()
    brands = await brand_storage.list_brands()

    logger.info("backfill_brands_start", count=len(brands))

    for brand in brands:
        if dry_run:
            logger.info("dry_run_would_sync_brand", brand_id=brand.brand_id)
        else:
            await graph_storage.sync_brand(brand)
            logger.info("brand_synced", brand_id=brand.brand_id)

    logger.info("backfill_brands_complete", count=len(brands))

async def backfill_assets(dry_run: bool = True):
    """Backfill all assets."""
    asset_storage = AssetStorage()
    # Note: AssetStorage doesn't have list_all method
    # Would need to add this or query PostgreSQL directly
    logger.info("backfill_assets_start")
    # TODO: Implement asset listing and backfill
    logger.info("backfill_assets_complete")

async def main():
    parser = argparse.ArgumentParser(description="Backfill graph database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")
    parser.add_argument("--execute", action="store_true", help="Actually sync data")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Must specify --dry-run or --execute")
        return

    dry_run = args.dry_run

    logger.info("backfill_start", dry_run=dry_run)

    await backfill_brands(dry_run)
    # await backfill_assets(dry_run)
    # await backfill_feedback(dry_run)
    # await backfill_templates(dry_run)

    await graph_storage.close()

    logger.info("backfill_complete")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 5: Testing & Monitoring (Week 3)

### Task 5.1: Add Graph Health Check
**File:** `src/mobius/api/routes.py`

```python
async def graph_health_check_handler(request: dict) -> dict:
    """
    GET /v1/health/graph

    Check Neo4j graph database health and stats.
    """
    from mobius.storage.graph import graph_storage

    if not graph_storage._is_enabled():
        return {
            "status": "disabled",
            "message": "Graph database not configured"
        }

    try:
        async with graph_storage.driver.session() as session:
            # Test query
            result = await session.run("MATCH (n) RETURN COUNT(n) as node_count")
            record = await result.single()
            node_count = record["node_count"]

            # Get stats by label
            result = await session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, COUNT(n) as count
                ORDER BY count DESC
            """)
            stats = [dict(record) async for record in result]

            return {
                "status": "healthy",
                "node_count": node_count,
                "stats_by_label": stats,
                "database": graph_storage.driver._config.database
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Task 5.2: Add Integration Tests
**New File:** `tests/integration/test_graph_storage.py`

```python
import pytest
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.storage.graph import graph_storage

@pytest.mark.asyncio
async def test_sync_brand_creates_node():
    """Test that syncing a brand creates Brand and Color nodes."""
    brand = Brand(
        brand_id="test-brand-123",
        organization_id="test-org",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Blue", hex="#0000FF", usage="primary", usage_weight=0.6),
                Color(name="White", hex="#FFFFFF", usage="secondary", usage_weight=0.3)
            ]
        ),
        ...
    )

    await graph_storage.sync_brand(brand)

    # Verify Brand node exists
    colors = await graph_storage.get_brand_colors("test-brand-123")
    assert len(colors) == 2
    assert colors[0]["hex"] == "#0000FF"
    assert colors[0]["usage"] == "primary"
```

---

## Critical Files Summary

### New Files to Create
1. `src/mobius/storage/graph.py` - Graph storage layer (~500 lines)
2. `scripts/backfill_graph_database.py` - Data migration script
3. `tests/integration/test_graph_storage.py` - Integration tests

### Files to Modify
1. `src/mobius/api/app.py` - Add neo4j dependency, register endpoints
2. `src/mobius/config.py` - Add Neo4j settings
3. `src/mobius/storage/brands.py` - Add dual-write calls (2 methods)
4. `src/mobius/storage/assets.py` - Add dual-write call (1 method)
5. `src/mobius/storage/feedback.py` - Add dual-write call (1 method)
6. `src/mobius/storage/templates.py` - Add dual-write call (1 method)
7. `src/mobius/api/routes.py` - Add graph query handlers (4 methods)

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Neo4j Aura instance running
- ✅ Connection successful from local environment
- ✅ Environment variables configured

### Phase 2 Complete When:
- ✅ GraphStorage class implemented
- ✅ Dual-write working for brands
- ✅ Dual-write working for assets
- ✅ Dual-write working for feedback
- ✅ All writes logged (success and failure)

### Phase 3 Complete When:
- ✅ 4 graph query endpoints live
- ✅ Can retrieve brand colors via graph
- ✅ Can find brands by color
- ✅ Can find similar brands
- ✅ Color pairing query ready (awaiting USES_COLOR edges)

### Phase 4 Complete When:
- ✅ All existing brands backfilled to Neo4j
- ✅ All existing assets backfilled to Neo4j
- ✅ Graph database in sync with PostgreSQL

### Phase 5 Complete When:
- ✅ Health check endpoint working
- ✅ Integration tests passing
- ✅ Monitoring alerts configured
- ✅ Documentation updated

---

## Rollback Plan

If graph integration causes issues:

1. **Immediate:** Set `GRAPH_SYNC_ENABLED=false` in environment
2. **Short-term:** Remove dual-write calls (comment out)
3. **Long-term:** Drop Neo4j instance, revert code changes

PostgreSQL remains source of truth - no data loss risk.

---

## Future Enhancements (Post-MVP)

### Phase 6: Advanced Features
1. **Asset Color Extraction** - Use Vision model to extract colors from generated images
2. **USES_COLOR Edges** - Link Asset → Color based on extraction
3. **Color Pairing Intelligence** - Enable full color pairing queries (MOAT feature)
4. **Pattern Nodes** - Add learning patterns to graph
5. **Cross-Brand Discovery** - Industry-level pattern queries (Enterprise tier)
6. **Graph Visualization** - Neo4j Bloom integration for dashboard
7. **CDC (Change Data Capture)** - Replace dual-write with PostgreSQL triggers

---

## Cost Projection

| Month | Brands | Assets | Nodes | Relationships | Neo4j Tier | Cost |
|-------|--------|--------|-------|---------------|------------|------|
| 1-2 | 10 | 100 | ~1,500 | ~3,000 | Free | $0 |
| 3-4 | 50 | 500 | ~7,500 | ~15,000 | Free | $0 |
| 5-6 | 100 | 1,000 | ~15,000 | ~30,000 | Free | $0 |
| 7+ | 200+ | 2,000+ | 200k+ | 400k+ | Pro | $65/mo |

Free tier sufficient for first 6 months at current growth rate.
