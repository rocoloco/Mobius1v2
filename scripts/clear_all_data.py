"""
Clear ALL data from Supabase and Neo4j (brands, jobs, assets, etc.).
Use with EXTREME caution - this will delete everything!
"""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


async def clear_neo4j():
    """Delete everything from Neo4j."""
    from mobius.storage.graph import graph_storage
    
    if not graph_storage._is_enabled():
        print("⚠️  Neo4j is not enabled. Skipping.")
        return
    
    try:
        async with graph_storage.driver.session() as session:
            # Delete everything
            await session.run("MATCH (n) DETACH DELETE n")
            print("   ✓ Cleared Neo4j graph database")
    except Exception as e:
        print(f"   ✗ Failed to clear Neo4j: {e}")


def clear_supabase():
    """Delete all data from Supabase tables."""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Order matters due to foreign key constraints
    tables = [
        "feedback",      # References assets
        "templates",     # References brands
        "assets",        # References brands and jobs
        "jobs",          # References brands
        "brands",        # Base table
    ]
    
    for table in tables:
        try:
            # Get count first
            response = supabase.table(table).select("*", count="exact").execute()
            count = response.count
            
            if count > 0:
                # Delete all rows
                supabase.table(table).delete().neq("created_at", "1900-01-01").execute()
                print(f"   ✓ Cleared {count} rows from {table}")
            else:
                print(f"   • {table} already empty")
                
        except Exception as e:
            print(f"   ✗ Failed to clear {table}: {e}")


async def clear_everything():
    """Clear all data from both databases."""
    
    print("⚠️  WARNING: This will delete ALL data from:")
    print("   • All brands")
    print("   • All jobs")
    print("   • All assets")
    print("   • All templates")
    print("   • All feedback")
    print("   • All Neo4j graph data")
    
    confirm = input("\nType 'DELETE EVERYTHING' to confirm: ").strip()
    
    if confirm != "DELETE EVERYTHING":
        print("❌ Cancelled. No data was deleted.")
        return
    
    print("\n🗑️  Clearing all data...\n")
    
    print("Clearing Supabase...")
    clear_supabase()
    
    print("\nClearing Neo4j...")
    await clear_neo4j()
    
    print("\n✅ All data cleared from both databases!")


if __name__ == "__main__":
    asyncio.run(clear_everything())
