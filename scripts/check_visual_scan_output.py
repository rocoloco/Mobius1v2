"""Check what the visual scan captured from a website."""

import requests
import json

# Test the visual scan endpoint
url = "http://localhost:8000/v1/brands/scan"
payload = {"url": "stripe.com"}

print("Testing visual scan for stripe.com...")
print("=" * 60)

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    
    # Pretty print the response
    print(json.dumps(data, indent=2))
    
    # Check for errors
    if "error" in data:
        print("\n❌ ERROR:", data["error"])
        print("Confidence:", data.get("confidence", 0))
    else:
        print("\n✅ SUCCESS!")
        print(f"URL: {data.get('url')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
        
        # Show what was extracted
        if "colors" in data:
            print(f"\nColors extracted: {len(data['colors'])}")
            for color in data['colors'][:5]:  # Show first 5
                print(f"  - {color.get('name')}: {color.get('hex')} ({color.get('usage')})")
        
        if "typography" in data:
            print(f"\nTypography extracted: {len(data['typography'])}")
            for font in data['typography'][:3]:  # Show first 3
                print(f"  - {font.get('family')} ({font.get('usage')})")
        
        if "identity_core" in data:
            print(f"\nBrand Archetype: {data['identity_core'].get('archetype')}")
            if "voice_vectors" in data['identity_core']:
                vectors = data['identity_core']['voice_vectors']
                print("Voice Vectors:")
                for key, value in vectors.items():
                    print(f"  - {key}: {value}")
        
        if "visual_style" in data:
            style = data['visual_style']
            print(f"\nVisual Style: {style.get('imagery_style')}")
            if "keywords" in style:
                print(f"Keywords: {', '.join(style['keywords'][:5])}")
else:
    print(f"❌ Request failed with status {response.status_code}")
    print(response.text)
