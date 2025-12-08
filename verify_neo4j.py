from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print()

try:
    # Connect to Neo4j (SSL will use system certificates by default)
    driver = GraphDatabase.driver(
        uri,
        auth=(user, password),
        max_connection_lifetime=3600,
        keep_alive=True,
        connection_timeout=30
    )

    print("Verifying connectivity...")
    driver.verify_connectivity()
    print("Connection successful!")
    print()

    with driver.session(database="neo4j") as session:
        # Count brands
        result = session.run("MATCH (b:Brand) RETURN count(b) as count")
        brand_count = result.single()["count"]
        print(f"Brands in Neo4j: {brand_count}")

        # Count colors
        result = session.run("MATCH (c:Color) RETURN count(c) as count")
        color_count = result.single()["count"]
        print(f"Colors in Neo4j: {color_count}")

        # Count relationships
        result = session.run("MATCH ()-[r:OWNS_COLOR]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
        print(f"Brand->Color relationships: {rel_count}")

        print()
        print("Sample brands with colors:")
        result = session.run("""
            MATCH (b:Brand)-[r:OWNS_COLOR]->(c:Color)
            RETURN b.name as brand, c.name as color_name, c.hex as hex, r.usage as usage
            LIMIT 5
        """)
        for record in result:
            print(f"  - {record['brand']}: {record['color_name']} ({record['hex']}) - {record['usage']}")

    driver.close()
    print()
    print("All data successfully loaded into Neo4j!")

except Exception as e:
    print(f"Connection failed: {e}")
