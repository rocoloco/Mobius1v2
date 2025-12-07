#!/usr/bin/env python3
"""
Fix invalid color usage values in brand guidelines.

This script updates color usage values that don't match the valid enum:
'primary', 'secondary', 'accent', 'neutral', 'semantic'

Common mappings:
- 'background' -> 'neutral'
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Fix color usage values in the database."""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)
    
    client = create_client(supabase_url, supabase_key)
    
    print("Fetching brands with guidelines...")
    
    # Fetch all brands
    response = client.table("brands").select("brand_id, name, guidelines").execute()
    
    if not response.data:
        print("No brands found")
        return
    
    print(f"Found {len(response.data)} brands")
    
    # Mapping of invalid values to valid ones
    usage_mapping = {
        'background': 'neutral',
        'text': 'neutral',
        'border': 'neutral',
        'surface': 'neutral',
    }
    
    updated_count = 0
    
    for brand in response.data:
        brand_id = brand['brand_id']
        brand_name = brand['name']
        guidelines = brand['guidelines']
        
        if not guidelines or 'colors' not in guidelines:
            continue
        
        colors = guidelines['colors']
        if not isinstance(colors, list):
            continue
        
        modified = False
        
        for i, color in enumerate(colors):
            if not isinstance(color, dict) or 'usage' not in color:
                continue
            
            usage = color['usage']
            
            # Check if usage is invalid
            if usage not in ['primary', 'secondary', 'accent', 'neutral', 'semantic']:
                old_usage = usage
                new_usage = usage_mapping.get(usage, 'neutral')
                
                print(f"  Brand: {brand_name}")
                print(f"    Color {i}: {color.get('name', 'unnamed')}")
                print(f"    Changing usage: '{old_usage}' -> '{new_usage}'")
                
                color['usage'] = new_usage
                modified = True
        
        if modified:
            # Update the brand with fixed guidelines
            client.table("brands").update({
                "guidelines": guidelines
            }).eq("brand_id", brand_id).execute()
            
            updated_count += 1
            print(f"  ✓ Updated brand: {brand_name}\n")
    
    if updated_count == 0:
        print("\n✓ No invalid color usage values found")
    else:
        print(f"\n✓ Fixed {updated_count} brand(s)")

if __name__ == "__main__":
    main()
