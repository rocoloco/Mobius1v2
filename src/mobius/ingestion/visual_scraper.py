"""
Visual Brand Scraper - Vision-First Onboarding

Replaces brittle HTML text scraping with Visual Scraping using:
- Playwright for high-fidelity screenshots of landing pages
- Gemini 1.5 Flash (Multimodal) for visual brand analysis

This module can be tested standalone via Modal's dashboard or CLI:
    modal run src.mobius.ingestion.visual_scraper::analyze_brand_visuals --url "https://stripe.com"

Architecture:
1. Headless browser captures screenshot (handles SPAs, JS-heavy sites)
2. Gemini Vision analyzes the visual hierarchy, colors, typography, and "vibe"
3. Returns structured JSON matching BrandGuidelines schema
"""

import modal
import json
import os
from typing import Dict, Any, Optional

# --- MODAL RUNTIME ENVIRONMENT ---
# Playwright requires system-level dependencies for Chromium
image = (
    modal.Image.debian_slim()
    .apt_install(
        # Chromium dependencies
        "libglib2.0-0",
        "libnss3",
        "libnspr4",
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libdrm2",
        "libxkbcommon0",
        "libxcomposite1",
        "libxdamage1",
        "libxrandr2",
        "libgbm1",
        "libpango-1.0-0",
        "libcairo2",
        "libasound2",
        "libxshmfence1",
        "fonts-liberation",
        "libappindicator3-1",
        "xdg-utils",
    )
    .pip_install(
        "playwright==1.48.0",
        "google-generativeai==0.8.3",
    )
    .run_commands("playwright install chromium")
)

app = modal.App("mobius-visual-scraper", image=image)

# Create a separate secret just for the visual scraper (only needs Gemini)
# Run: modal secret create visual-scraper-secret GEMINI_API_KEY=your_key


# --- EXTRACTION SCHEMA ---
# Defines the structure Gemini should return (enforces JSON schema)
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "identity_core": {
            "type": "object",
            "properties": {
                "archetype": {
                    "type": "string",
                    "description": "Jungian brand archetype inferred from visual style and messaging. Examples: 'The Sage', 'The Hero', 'The Rebel', 'The Innocent', 'The Explorer'",
                },
                "voice_vectors": {
                    "type": "object",
                    "description": "Voice dimensions as 0.0-1.0 scores",
                    "properties": {
                        "formal": {
                            "type": "number",
                            "description": "0.0 = casual/conversational, 1.0 = formal/professional",
                        },
                        "witty": {
                            "type": "number",
                            "description": "0.0 = serious/straightforward, 1.0 = playful/humorous",
                        },
                        "technical": {
                            "type": "number",
                            "description": "0.0 = accessible/simple, 1.0 = jargon-heavy/expert",
                        },
                        "urgent": {
                            "type": "number",
                            "description": "0.0 = relaxed/patient, 1.0 = time-sensitive/action-oriented",
                        },
                    },
                },
            },
        },
        "colors": {
            "type": "array",
            "description": "Brand color palette with semantic roles",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Color name (e.g., 'Ocean Blue')"},
                    "hex": {"type": "string", "description": "Hex code (e.g., '#0057B8')"},
                    "usage": {
                        "type": "string",
                        "enum": ["primary", "secondary", "accent", "neutral", "semantic"],
                        "description": "Semantic role: primary (brand identity), secondary (supporting), accent (CTAs), neutral (backgrounds), semantic (status colors)",
                    },
                    "usage_weight": {
                        "type": "number",
                        "description": "Estimated visual prominence (0.0-1.0)",
                    },
                },
            },
        },
        "typography": {
            "type": "array",
            "description": "Font families detected",
            "items": {
                "type": "object",
                "properties": {
                    "family": {"type": "string", "description": "Font family name"},
                    "usage": {
                        "type": "string",
                        "description": "Usage context (e.g., 'Headlines', 'Body text')",
                    },
                },
            },
        },
        "visual_style": {
            "type": "object",
            "description": "Overall visual aesthetic",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-5 adjectives describing the visual style (e.g., 'minimalist', 'bold', 'playful')",
                },
                "imagery_style": {
                    "type": "string",
                    "description": "Photography/illustration style (e.g., 'abstract illustrations', 'lifestyle photography', '3D renders')",
                },
            },
        },
        "confidence": {
            "type": "number",
            "description": "Confidence score for the extraction (0.0-1.0)",
        },
    },
    "required": ["identity_core", "colors", "typography", "visual_style", "confidence"],
}


# --- EXTRACTION PROMPT ---
EXTRACTION_PROMPT = """You are an expert Brand Strategist analyzing a website screenshot.

Your task is to infer the brand's identity by analyzing:
1. **Visual Hierarchy**: What elements dominate? What's emphasized?
2. **Color Psychology**: What emotions do the colors evoke?
3. **Typography**: What does the font choice communicate?
4. **Imagery Style**: What's the photography/illustration aesthetic?
5. **Copy Tone**: Analyze headlines and CTAs for voice characteristics

CRITICAL INSTRUCTIONS:
- Focus on the "above the fold" content (first screen)
- Identify the PRIMARY brand color (used for logos/headers)
- Identify ACCENT colors (used for buttons/CTAs)
- Infer the Jungian archetype based on visual + verbal cues
- Estimate voice vectors by analyzing headline tone and word choice
- Assign usage_weight based on visual prominence (0.0-1.0)

ARCHETYPE GUIDE:
- The Sage: Wisdom, expertise, thought leadership (e.g., universities, consultancies)
- The Hero: Achievement, courage, making an impact (e.g., Nike, sports brands)
- The Rebel: Disruption, revolution, breaking rules (e.g., Harley-Davidson, Tesla)
- The Innocent: Simplicity, purity, nostalgia (e.g., Dove, Coca-Cola)
- The Explorer: Freedom, discovery, adventure (e.g., Patagonia, Jeep)
- The Creator: Innovation, imagination, self-expression (e.g., Adobe, Lego)
- The Ruler: Control, leadership, responsibility (e.g., Mercedes-Benz, Rolex)
- The Magician: Transformation, vision, making dreams reality (e.g., Disney, Apple)
- The Lover: Intimacy, passion, sensuality (e.g., Chanel, Godiva)
- The Caregiver: Service, compassion, nurturing (e.g., Johnson & Johnson, UNICEF)
- The Jester: Joy, humor, living in the moment (e.g., Ben & Jerry's, Old Spice)
- The Everyman: Belonging, authenticity, down-to-earth (e.g., IKEA, Target)

Return strict JSON matching the schema. Be decisive - make your best inference even with limited information.
"""


@app.function(
    secrets=[modal.Secret.from_name("visual-scraper-secret")],
    timeout=60,  # 60 second timeout
)
def analyze_brand_visuals(url: str) -> Dict[str, Any]:
    """
    Analyze a website's visual brand identity using Playwright + Gemini Vision.
    
    Args:
        url: Website URL to analyze (e.g., "https://stripe.com")
    
    Returns:
        Dictionary with extracted brand identity data matching BrandGuidelines schema
        
    Example:
        result = analyze_brand_visuals.remote("https://stripe.com")
        print(result["identity_core"]["archetype"])  # "The Sage"
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    import google.generativeai as genai
    
    print(f"🌐 Analyzing brand visuals for: {url}")
    
    # --- STEP 1: CAPTURE SCREENSHOT ---
    screenshot_bytes = None
    screenshot_error = None
    
    try:
        with sync_playwright() as p:
            print("  → Launching headless browser...")
            browser = p.chromium.launch(
                args=[
                    "--disable-blink-features=AutomationControlled",  # Evade bot detection
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ]
            )
            
            context = browser.new_context(
                viewport={"width": 1280, "height": 1024},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            
            page = context.new_page()
            
            try:
                print(f"  → Visiting {url}...")
                # wait_until="networkidle" ensures SPAs/React apps are fully rendered
                page.goto(url, wait_until="networkidle", timeout=15000)
                
                # Wait an additional 2 seconds for animations/lazy loading
                page.wait_for_timeout(2000)
                
                print("  → Capturing screenshot...")
                # Capture "above the fold" content (first 2000px)
                screenshot_bytes = page.screenshot(
                    clip={"x": 0, "y": 0, "width": 1280, "height": 2000},
                    type="jpeg",
                    quality=85,  # Balance quality vs. token cost
                )
                
                print(f"  ✓ Screenshot captured ({len(screenshot_bytes)} bytes)")
                
            except PlaywrightTimeout:
                screenshot_error = "Page load timeout (15s exceeded)"
                print(f"  ✗ {screenshot_error}")
            except Exception as e:
                screenshot_error = f"Navigation failed: {str(e)}"
                print(f"  ✗ {screenshot_error}")
            finally:
                browser.close()
                
    except Exception as e:
        screenshot_error = f"Browser launch failed: {str(e)}"
        print(f"  ✗ {screenshot_error}")
    
    # If screenshot failed, return error
    if screenshot_bytes is None:
        return {
            "error": screenshot_error or "Screenshot capture failed",
            "url": url,
            "confidence": 0.0,
        }
    
    # --- STEP 2: GEMINI VISION ANALYSIS ---
    print("🧠 Analyzing with Gemini Vision...")
    
    try:
        # Initialize Gemini
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Generate analysis
        response = model.generate_content(
            contents=[
                EXTRACTION_PROMPT,
                {
                    "mime_type": "image/jpeg",
                    "data": screenshot_bytes,
                },
            ],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=EXTRACTION_SCHEMA,
                temperature=0.3,  # Lower temperature for more consistent extraction
            ),
        )
        
        # Parse response
        result = json.loads(response.text)
        result["url"] = url
        result["screenshot_size_bytes"] = len(screenshot_bytes)
        
        print(f"  ✓ Analysis complete (confidence: {result.get('confidence', 0.0):.2f})")
        print(f"  → Archetype: {result.get('identity_core', {}).get('archetype', 'Unknown')}")
        print(f"  → Colors extracted: {len(result.get('colors', []))}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ Gemini analysis failed: {e}")
        return {
            "error": f"Vision analysis failed: {str(e)}",
            "url": url,
            "confidence": 0.0,
        }


@app.local_entrypoint()
def main(url: str = "https://stripe.com"):
    """
    Test the visual scraper locally.
    
    Usage:
        modal run src.mobius.ingestion.visual_scraper --url "https://stripe.com"
    """
    print(f"\n{'='*60}")
    print(f"MOBIUS VISUAL BRAND SCRAPER - TEST MODE")
    print(f"{'='*60}\n")
    
    result = analyze_brand_visuals.remote(url)
    
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=2))
    
    if "error" not in result:
        print(f"\n✅ SUCCESS - Brand identity extracted")
        print(f"   Archetype: {result['identity_core']['archetype']}")
        print(f"   Confidence: {result['confidence']:.1%}")
    else:
        print(f"\n❌ FAILED - {result['error']}")
