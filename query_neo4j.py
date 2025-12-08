"""
Query Neo4j directly without connectivity check.
"""
import asyncio
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Connecting to: {uri}")
print()


async def query():
    driver = AsyncGraphDatabase.driver(
        uri,
        auth=(user, password),
        database="neo4j"
    )

    try:
        # Skip verify_connectivity, go straight to querying
        async with driver.session(database="neo4j") as session:
            print("Querying brand count...")
            result = await session.run("MATCH (b:Brand) RETURN count(b) as count")
            record = await result.single()
            brand_count = record["count"]
            print(f"SUCCESS: Found {brand_count} brands in Neo4j")
            print()

            # Count colors
            result = await session.run("MATCH (c:Color) RETURN count(c) as count")
            record = await result.single()
            color_count = record["count"]
            print(f"Colors in Neo4j: {color_count}")

            # Count relationships
            result = await session.run("MATCH ()-[r:OWNS_COLOR]->() RETURN count(r) as count")
            record = await result.single()
            rel_count = record["count"]
            print(f"Brand->Color relationships: {rel_count}")

            print()
            print("Sample brands with colors:")
            result = await session.run("""
                MATCH (b:Brand)-[r:OWNS_COLOR]->(c:Color)
                RETURN b.name as brand, c.name as color_name, c.hex as hex, r.usage as usage
                LIMIT 5
            """)
            records = []
            async for record in result:
                records.append(record)

            if records:
                for record in records:
                    print(f"  - {record['brand']}: {record['color_name']} ({record['hex']}) - {record['usage']}")
            else:
                print("  (No brand-color relationships found)")

        await driver.close()
        print()
        print("Verification complete!")

    except Exception as e:
        print(f"Query failed: {e}")
        import traceback
        traceback.print_exc()
        await driver.close()


if __name__ == "__main__":
    asyncio.run(query())
