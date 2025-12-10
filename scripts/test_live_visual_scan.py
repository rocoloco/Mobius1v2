"""Test the live visual scan endpoint on Modal."""

import requests
import json

# Use the deployed Modal endpoint
API_URL = "https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1/brands/scan"

def test_visual_scan(url: str):
    """Test visual scan for a given URL."""
    print(f"\n{'='*60}")
    print(f"Testing Visual Scan: {url}")
    print(f"{'='*60}\n")
    
    print("Sending request to Modal endpoint...")
    print(f"API: {API_URL}")
    
    try:
        response = requests.post(
            API_URL,
            json={"url": url},
            timeout=30  # Visual scan takes 8-12 seconds
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors in response
            if "error" in data:
                print(f"\n❌ ERROR: {data['error']}")
                print(f"Confidence: {data.get('confidence', 0)}")
                return
            
            # Success - show what was captured
            print("\n✅ SUCCESS! Visual scan completed.\n")
            
            # Basic info
            print(f"URL: {data.get('url', url)}")
            print(f"Confidence: {(data.get('confidence', 0) * 100):.0f}%")
            
            # Brand archetype
            if "identity_core" in data:
                archetype = data['identity_core'].get('archetype', 'Unknown')
                print(f"Brand Archetype: {archetype}")
                
                # Voice vectors
                if "voice_vectors" in data['identity_core']:
                    print("\nVoice Profile:")
                    for key, value in data['identity_core']['voice_vectors'].items():
                        bar = "█" * int(value * 20)
                        print(f"  {key:12} {bar:20} {value:.2f}")
            
            # Colors
            if "colors" in data:
                print(f"\nColors Extracted: {len(data['colors'])}")
                for i, color in enumerate(data['colors'][:8], 1):
                    name = color.get('name', 'Unnamed')
                    hex_code = color.get('hex', '#000000')
                    usage = color.get('usage', 'unknown')
                    weight = color.get('usage_weight', 0)
                    print(f"  {i}. {name:20} {hex_code:8} {usage:15} ({weight*100:.0f}%)")
            
            # Typography
            if "typography" in data:
                print(f"\nTypography: {len(data['typography'])} fonts")
                for font in data['typography'][:5]:
                    family = font.get('family', 'Unknown')
                    usage = font.get('usage', 'unknown')
                    print(f"  • {family} ({usage})")
            
            # Visual style
            if "visual_style" in data:
                style = data['visual_style']
                if "keywords" in style:
                    print(f"\nVisual Keywords: {', '.join(style['keywords'][:8])}")
                if "imagery_style" in style:
                    print(f"Imagery Style: {style['imagery_style']}")
            
            # Save full JSON
            filename = f"visual_scan_{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full JSON saved to: {filename}")
            
        else:
            print(f"\n❌ Request failed")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (visual scan takes 8-12 seconds)")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    # Test with Stripe
    test_visual_scan("stripe.com")
    
    # Uncomment to test other sites
    # test_visual_scan("airbnb.com")
    # test_visual_scan("notion.so")
