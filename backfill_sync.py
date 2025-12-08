"""
Synchronous backfill script that bypasses SSL verification for Windows local testing.
"""
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mobius.storage.database import get_supabase_client
from mobius.models.brand import Brand

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Connecting to: {uri}")
print()

# Create driver WITHOUT SSL verification (for local Windows testing only!)
# This works around Windows SSL certificate issues
driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    encrypted=False  # Disable SSL for testing - DO NOT use in production!
)

try:
    print("Testing connection...")
    driver.verify_connectivity()
    print("Connected successfully!")
    print()

    # Get all brands from Supabase
    client = get_supabase_client()
    result = client.table("brands").select("*").is_("deleted_at", "null").execute()
    brands_data = result.data

    print(f"Found {len(brands_data)} brands to sync")
    print()

    for i, brand_data in enumerate(brands_data, 1):
        brand = Brand.model_validate(brand_data)
        print(f"[{i}/{len(brands_data)}] Syncing: {brand.name}")

        with driver.session(database="neo4j") as session:
            # MERGE Brand node
            session.run(
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
                created_at=brand.created_at.isoformat(),
                updated_at=brand.updated_at.isoformat()
            )

            # Sync colors
            if brand.guidelines and brand.guidelines.colors:
                for color in brand.guidelines.colors:
                    session.run(
                        """
                        MERGE (c:Color {hex: $hex})
                        SET c.name = $name,
                            c.updated_at = datetime()

                        WITH c
                        MATCH (b:Brand {brand_id: $brand_id})
                        MERGE (b)-[r:OWNS_COLOR]->(c)
                        SET r.usage = $usage,
                            r.updated_at = datetime()
                        """,
                        hex=color.hex,
                        name=color.name,
                        brand_id=brand.brand_id,
                        usage=color.usage
                    )

        print(f"  - Synced {len(brand.guidelines.colors) if brand.guidelines else 0} colors")

    print()
    print(f"Successfully synced {len(brands_data)} brands to Neo4j!")

    # Verify
    with driver.session(database="neo4j") as session:
        result = session.run("MATCH (b:Brand) RETURN count(b) as count")
        brand_count = result.single()["count"]

        result = session.run("MATCH (c:Color) RETURN count(c) as count")
        color_count = result.single()["count"]

        result = session.run("MATCH ()-[r:OWNS_COLOR]->() RETURN count(r) as count")
        rel_count = result.single()["count"]

        print()
        print(f"Verification:")
        print(f"  Brands: {brand_count}")
        print(f"  Colors: {color_count}")
        print(f"  Relationships: {rel_count}")

finally:
    driver.close()
