"""Test Neo4j connection and diagnose routing issues."""

import asyncio
from neo4j import AsyncGraphDatabase
import certifi
import ssl as ssl_module
import structlog

logger = structlog.get_logger()

# Patch SSL context
original_create_default_context = ssl_module.create_default_context

def custom_create_default_context(*args, **kwargs):
    ctx = original_create_default_context(*args, **kwargs)
    ctx.load_verify_locations(certifi.where())
    return ctx

ssl_module.create_default_context = custom_create_default_context


async def test_connection():
    """Test Neo4j connection."""
    from mobius.config import settings
    
    print(f"Testing connection to: {settings.neo4j_uri}")
    print(f"Database: {settings.neo4j_database}")
    print(f"User: {settings.neo4j_user}")
    
    try:
        driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            database=settings.neo4j_database
        )
        
        print("✓ Driver created successfully")
        
        # Test connection with a simple query
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            record = await result.single()
            print(f"✓ Connection successful! Test query returned: {record['test']}")
            
            # Check database info
            result = await session.run("CALL dbms.components() YIELD name, versions, edition")
            async for record in result:
                print(f"✓ Neo4j {record['edition']}: {record['name']} {record['versions']}")
        
        await driver.close()
        print("\n✓ All tests passed! Neo4j is accessible.")
        
    except Exception as e:
        print(f"\n✗ Connection failed: {type(e).__name__}")
        print(f"  Error: {str(e)}")
        print("\nPossible causes:")
        print("  1. Neo4j Aura database is paused (check console.neo4j.io)")
        print("  2. Network connectivity issues")
        print("  3. Invalid credentials")
        print("  4. Firewall blocking port 7687")


if __name__ == "__main__":
    asyncio.run(test_connection())
