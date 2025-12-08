"""
Graph database storage layer using Neo4j.

Maintains dual-write synchronization between PostgreSQL (source of truth)
and Neo4j (relationship queries).
"""

import asyncio
import ssl
from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable
import structlog
import certifi

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

        # For neo4j+s:// URIs (Neo4j Aura), SSL is handled automatically
        # We just need to ensure Python can find CA certificates
        # Monkey-patch the default SSL context to use certifi's CA bundle
        import ssl as ssl_module
        original_create_default_context = ssl_module.create_default_context

        def custom_create_default_context(*args, **kwargs):
            ctx = original_create_default_context(*args, **kwargs)
            ctx.load_verify_locations(certifi.where())
            return ctx

        ssl_module.create_default_context = custom_create_default_context

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
