"""
Async verification script for Neo4j connection and data.
"""
import asyncio
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print()


async def verify():
    driver = AsyncGraphDatabase.driver(
        uri,
        auth=(user, password),
        database="neo4j",
        max_connection_lifetime=3600
    )

    try:
        print("Verifying connectivity...")
        await driver.verify_connectivity()
        print("Connection successful!")
        print()

        async with driver.session(database="neo4j") as session:
            # Count brands
            result = await session.run("MATCH (b:Brand) RETURN count(b) as count")
            record = await result.single()
            brand_count = record["count"]
            print(f"Brands in Neo4j: {brand_count}")

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
            async for record in result:
                print(f"  - {record['brand']}: {record['color_name']} ({record['hex']}) - {record['usage']}")

        await driver.close()
        print()
        print("All data successfully verified in Neo4j!")

    except Exception as e:
        print(f"Connection failed: {e}")
        await driver.close()


if __name__ == "__main__":
    asyncio.run(verify())
