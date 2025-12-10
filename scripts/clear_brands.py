"""
Clear all brands from both Supabase and Neo4j.
Use with caution - this will delete all brand data!
"""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def clear_neo4j_brands():
    """Delete all brands from Neo4j graph database."""
    from mobius.storage.graph import graph_storage
    
    if not graph_storage._is_enabled():
        print("⚠️  Neo4j is not enabled or configured. Skipping Neo4j cleanup.")
        return 0
    
    try:
        async with graph_storage.driver.session() as session:
            # Count brands first
            result = await session.run("MATCH (b:Brand) RETURN count(b) as count")
            record = await result.single()
            count = record["count"]
            
            if count == 0:
                print("✅ No brands found in Neo4j.")
                return 0
            
            print(f"📊 Found {count} brands in Neo4j")
            
            # Delete all brands and their relationships
            await session.run("""
                MATCH (b:Brand)
                DETACH DELETE b
            """)
            
            # Also delete orphaned colors
            await session.run("""
                MATCH (c:Color)
                WHERE NOT (c)<--()
                DELETE c
            """)
            
            print(f"   ✓ Deleted {count} brands from Neo4j")
            return count
            
    except Exception as e:
        print(f"   ✗ Failed to clear Neo4j: {e}")
        return 0


def clear_supabase_brands():
    """Delete all brands from Supabase."""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return 0
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Get all brands
    response = supabase.table("brands").select("brand_id, name").execute()
    brands = response.data
    
    if not brands:
        print("✅ No brands found in Supabase.")
        return 0
    
    print(f"📊 Found {len(brands)} brands in Supabase:")
    for brand in brands:
        print(f"   - {brand['name']} ({brand['brand_id']})")
    
    # Delete all brands
    for brand in brands:
        brand_id = brand['brand_id']
        try:
            supabase.table("brands").delete().eq("brand_id", brand_id).execute()
            print(f"   ✓ Deleted: {brand['name']}")
        except Exception as e:
            print(f"   ✗ Failed to delete {brand['name']}: {e}")
    
    return len(brands)


async def clear_all_brands():
    """Delete all brands from both Supabase and Neo4j."""
    
    print("🔍 Checking databases...\n")
    
    # Check both databases first
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    response = supabase.table("brands").select("brand_id, name").execute()
    supabase_count = len(response.data)
    
    from mobius.storage.graph import graph_storage
    neo4j_count = 0
    if graph_storage._is_enabled():
        async with graph_storage.driver.session() as session:
            result = await session.run("MATCH (b:Brand) RETURN count(b) as count")
            record = await result.single()
            neo4j_count = record["count"]
    
    total = supabase_count + neo4j_count
    
    if total == 0:
        print("✅ No brands found in either database. Already clean!")
        return
    
    print(f"Found brands:")
    print(f"  • Supabase: {supabase_count}")
    print(f"  • Neo4j: {neo4j_count}")
    print(f"  • Total: {total}")
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Delete all {total} brands from BOTH databases? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("❌ Cancelled. No brands were deleted.")
        return
    
    print("\n🗑️  Deleting brands...\n")
    
    # Clear Supabase first (source of truth)
    supabase_deleted = clear_supabase_brands()
    
    print()
    
    # Clear Neo4j
    neo4j_deleted = await clear_neo4j_brands()
    
    print(f"\n✅ Successfully deleted:")
    print(f"   • {supabase_deleted} brands from Supabase")
    print(f"   • {neo4j_deleted} brands from Neo4j")
    print("💡 You can now upload fresh brands.")

if __name__ == "__main__":
    asyncio.run(clear_all_brands())
