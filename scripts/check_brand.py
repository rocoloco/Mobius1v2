"""Check brand status in database."""
import os
from supabase import create_client

# Get credentials from environment
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    exit(1)

client = create_client(url, key)

# Query all brands for the default org
result = client.table("brands").select("*").eq("organization_id", "00000000-0000-0000-0000-000000000000").execute()

print(f"\nFound {len(result.data)} brands:\n")
for brand in result.data:
    print(f"Brand ID: {brand['brand_id']}")
    print(f"Name: {brand['name']}")
    print(f"Deleted At: {brand.get('deleted_at', 'NULL')}")
    print(f"Created At: {brand['created_at']}")
    print("-" * 50)
