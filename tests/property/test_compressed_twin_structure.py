"""
Property-based tests for compressed twin structure.

**Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**

Tests that CompressedDigitalTwin contains only essential visual rules.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, assume
import pytest
from mobius.models.brand import CompressedDigitalTwin, BrandGuidelines, Color, Typography, LogoRule, BrandRule
import json


# Strategy for generating hex color codes
@st.composite
def hex_colors(draw):
    """Generate valid hex color codes."""
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    return f"#{r:02X}{g:02X}{b:02X}"


# Property 3: Compressed Twin Structure
@given(
    primary_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    secondary_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    accent_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    neutral_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    semantic_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    font_families=st.lists(st.text(min_size=3, max_size=30), min_size=0, max_size=10),
    visual_dos=st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=20),
    visual_donts=st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=20),
    logo_placement=st.one_of(st.none(), st.text(min_size=5, max_size=50)),
    logo_min_size=st.one_of(st.none(), st.text(min_size=5, max_size=30))
)
@hypothesis_settings(max_examples=100)
def test_compressed_twin_contains_only_essential_fields(
    primary_colors,
    secondary_colors,
    accent_colors,
    neutral_colors,
    semantic_colors,
    font_families,
    visual_dos,
    visual_donts,
    logo_placement,
    logo_min_size
):
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    *For any* brand guidelines extraction, the resulting Compressed Digital Twin should 
    contain only hex color codes, font family names, logo usage rules, and critical 
    visual constraints, excluding verbose descriptions and historical context.
    
    **Validates: Requirements 2.2, 2.3**
    
    This property test verifies that compressed twins have the correct structure.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=primary_colors,
        secondary_colors=secondary_colors,
        accent_colors=accent_colors,
        neutral_colors=neutral_colors,
        semantic_colors=semantic_colors,
        font_families=font_families,
        visual_dos=visual_dos,
        visual_donts=visual_donts,
        logo_placement=logo_placement,
        logo_min_size=logo_min_size
    )
    
    # Verify structure contains only essential fields
    model_dict = compressed_twin.model_dump()
    
    # Check that all color fields contain only hex codes (strings starting with #)
    for color_field in ['primary_colors', 'secondary_colors', 'accent_colors', 
                        'neutral_colors', 'semantic_colors']:
        colors = model_dict[color_field]
        for color in colors:
            assert isinstance(color, str), f"{color_field} should contain strings"
            # If not empty, should be hex format
            if color:
                assert color.startswith('#'), f"{color_field} should contain hex codes starting with #"
                assert len(color) == 7, f"{color_field} hex codes should be 7 characters (#RRGGBB)"
    
    # Check that font_families contains only strings (font names)
    for font in model_dict['font_families']:
        assert isinstance(font, str), "font_families should contain only strings"
    
    # Check that visual rules are concise strings
    for rule in model_dict['visual_dos']:
        assert isinstance(rule, str), "visual_dos should contain strings"
        assert len(rule) <= 200, f"visual_dos rules should be concise (<=200 chars), got {len(rule)}"
    
    for rule in model_dict['visual_donts']:
        assert isinstance(rule, str), "visual_donts should contain strings"
        assert len(rule) <= 200, f"visual_donts rules should be concise (<=200 chars), got {len(rule)}"
    
    # Check that logo fields are simple strings or None
    if model_dict['logo_placement'] is not None:
        assert isinstance(model_dict['logo_placement'], str), "logo_placement should be string or None"
        assert len(model_dict['logo_placement']) <= 100, "logo_placement should be concise"
    
    if model_dict['logo_min_size'] is not None:
        assert isinstance(model_dict['logo_min_size'], str), "logo_min_size should be string or None"
        assert len(model_dict['logo_min_size']) <= 50, "logo_min_size should be concise"
    
    print(f"✓ CompressedDigitalTwin has correct structure with {len(primary_colors)} primary colors")


def test_compressed_twin_excludes_verbose_fields():
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    Verify that CompressedDigitalTwin does NOT contain verbose fields from BrandGuidelines.
    
    **Validates: Requirements 2.2, 2.3**
    
    This test ensures proper field exclusion for compression.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#FF0000"],
        font_families=["Arial"]
    )
    
    model_dict = compressed_twin.model_dump()
    
    # Verify that verbose BrandGuidelines fields are NOT present
    verbose_fields = [
        'colors',  # Full Color objects with name, usage, context
        'typography',  # Full Typography objects with weights, usage
        'logos',  # Full LogoRule objects with URLs, ratios
        'voice',  # VoiceTone with adjectives, forbidden_words, examples
        'rules',  # BrandRule objects with categories, severity
        'source_filename',  # Metadata
        'ingested_at'  # Metadata
    ]
    
    for field in verbose_fields:
        assert field not in model_dict, (
            f"CompressedDigitalTwin should NOT contain verbose field '{field}'"
        )
    
    print("✓ CompressedDigitalTwin correctly excludes verbose BrandGuidelines fields")


def test_compressed_twin_has_semantic_color_hierarchy():
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    Verify that CompressedDigitalTwin preserves semantic color hierarchy.
    
    **Validates: Requirements 2.2, 2.3**
    
    This test ensures the structure prevents the "Confetti Problem".
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#0057B8"],
        secondary_colors=["#FF5733"],
        accent_colors=["#FFC300"],
        neutral_colors=["#FFFFFF", "#000000"],
        semantic_colors=["#10B981", "#EF4444"]
    )
    
    model_dict = compressed_twin.model_dump()
    
    # Verify all semantic color categories are present
    required_color_fields = [
        'primary_colors',
        'secondary_colors',
        'accent_colors',
        'neutral_colors',
        'semantic_colors'
    ]
    
    for field in required_color_fields:
        assert field in model_dict, (
            f"CompressedDigitalTwin must have '{field}' for semantic hierarchy"
        )
        assert isinstance(model_dict[field], list), (
            f"'{field}' should be a list"
        )
    
    print("✓ CompressedDigitalTwin preserves semantic color hierarchy")


@given(
    colors=st.lists(hex_colors(), min_size=1, max_size=20)
)
@hypothesis_settings(max_examples=100)
def test_compressed_twin_colors_are_hex_only(colors):
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    *For any* color list in CompressedDigitalTwin, all values should be hex codes only.
    
    **Validates: Requirements 2.2, 2.3**
    
    This property test verifies that colors are stored as hex codes, not full Color objects.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=colors
    )
    
    # Verify all colors are hex strings
    for color in compressed_twin.primary_colors:
        assert isinstance(color, str), "Colors should be strings"
        assert color.startswith('#'), "Colors should be hex codes starting with #"
        assert len(color) == 7, "Hex codes should be 7 characters (#RRGGBB)"
        
        # Verify it's a valid hex color
        try:
            int(color[1:], 16)
        except ValueError:
            pytest.fail(f"Invalid hex color: {color}")
    
    print(f"✓ All {len(colors)} colors are valid hex codes")


@given(
    fonts=st.lists(st.text(min_size=3, max_size=30), min_size=1, max_size=10)
)
@hypothesis_settings(max_examples=100)
def test_compressed_twin_fonts_are_names_only(fonts):
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    *For any* font list in CompressedDigitalTwin, all values should be font names only.
    
    **Validates: Requirements 2.2, 2.3**
    
    This property test verifies that fonts are stored as names, not full Typography objects.
    """
    compressed_twin = CompressedDigitalTwin(
        font_families=fonts
    )
    
    # Verify all fonts are simple strings
    for font in compressed_twin.font_families:
        assert isinstance(font, str), "Fonts should be strings"
        assert len(font) <= 50, "Font names should be concise"
    
    print(f"✓ All {len(fonts)} fonts are simple name strings")


def test_compressed_twin_serialization_is_compact():
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    Verify that CompressedDigitalTwin JSON serialization is compact.
    
    **Validates: Requirements 2.2, 2.3**
    
    This test ensures the serialized format is optimized for token efficiency.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#0057B8", "#1E3A8A"],
        secondary_colors=["#FF5733"],
        accent_colors=["#FFC300"],
        neutral_colors=["#FFFFFF", "#000000"],
        font_families=["Helvetica Neue", "Georgia"],
        visual_dos=["Use primary colors for headers"],
        visual_donts=["Never use Comic Sans"]
    )
    
    # Serialize to JSON
    json_str = json.dumps(compressed_twin.model_dump(), indent=2)
    
    # Verify JSON doesn't contain verbose field names from BrandGuidelines
    verbose_terms = [
        'usage_weight',  # From Color model
        'weights',  # From Typography model
        'variant_name',  # From LogoRule model
        'forbidden_backgrounds',  # From LogoRule model
        'adjectives',  # From VoiceTone model
        'forbidden_words',  # From VoiceTone model
        'category',  # From BrandRule model
        'severity',  # From BrandRule model
        'negative_constraint'  # From BrandRule model
    ]
    
    for term in verbose_terms:
        assert term not in json_str, (
            f"CompressedDigitalTwin JSON should not contain verbose term '{term}'"
        )
    
    print(f"✓ CompressedDigitalTwin JSON is compact ({len(json_str)} chars)")


@given(
    visual_dos=st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=30),
    visual_donts=st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=30)
)
@hypothesis_settings(max_examples=100)
def test_compressed_twin_rules_are_concise(visual_dos, visual_donts):
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    *For any* visual rules in CompressedDigitalTwin, all rules should be concise strings.
    
    **Validates: Requirements 2.2, 2.3**
    
    This property test verifies that rules are compressed, not verbose BrandRule objects.
    """
    compressed_twin = CompressedDigitalTwin(
        visual_dos=visual_dos,
        visual_donts=visual_donts
    )
    
    # Verify all rules are concise strings
    for rule in compressed_twin.visual_dos:
        assert isinstance(rule, str), "visual_dos should be strings"
        assert len(rule) <= 200, f"visual_dos should be concise, got {len(rule)} chars"
    
    for rule in compressed_twin.visual_donts:
        assert isinstance(rule, str), "visual_donts should be strings"
        assert len(rule) <= 200, f"visual_donts should be concise, got {len(rule)} chars"
    
    print(f"✓ All {len(visual_dos) + len(visual_donts)} rules are concise strings")


def test_compressed_twin_vs_brand_guidelines_size():
    """
    **Feature: gemini-3-dual-architecture, Property 3: Compressed Twin Structure**
    
    Verify that CompressedDigitalTwin is significantly smaller than BrandGuidelines.
    
    **Validates: Requirements 2.2, 2.3**
    
    This test ensures compression actually reduces size.
    """
    # Create a full BrandGuidelines object
    brand_guidelines = BrandGuidelines(
        colors=[
            Color(
                name="Primary Blue",
                hex="#0057B8",
                usage="primary",
                usage_weight=0.3,
                context="Use for headers and logos"
            ),
            Color(
                name="Secondary Red",
                hex="#FF5733",
                usage="secondary",
                usage_weight=0.2,
                context="Use for supporting elements"
            )
        ],
        typography=[
            Typography(
                family="Helvetica Neue",
                weights=["400", "700", "900"],
                usage="Use for all body text and headers"
            )
        ],
        logos=[
            LogoRule(
                variant_name="Primary Logo",
                url="https://example.com/logo.png",
                min_width_px=100,
                clear_space_ratio=0.25,
                forbidden_backgrounds=["#FF0000", "#00FF00"]
            )
        ],
        rules=[
            BrandRule(
                category="visual",
                instruction="Never use Comic Sans",
                severity="critical",
                negative_constraint=True
            )
        ]
    )
    
    # Create equivalent CompressedDigitalTwin
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#0057B8"],
        secondary_colors=["#FF5733"],
        font_families=["Helvetica Neue"],
        visual_donts=["Never use Comic Sans"],
        logo_min_size="100px width"
    )
    
    # Compare serialized sizes
    guidelines_json = json.dumps(brand_guidelines.model_dump())
    compressed_json = json.dumps(compressed_twin.model_dump())
    
    guidelines_size = len(guidelines_json)
    compressed_size = len(compressed_json)
    
    # Compressed should be significantly smaller
    assert compressed_size < guidelines_size, (
        f"CompressedDigitalTwin ({compressed_size} chars) should be smaller than "
        f"BrandGuidelines ({guidelines_size} chars)"
    )
    
    compression_ratio = compressed_size / guidelines_size
    print(f"✓ CompressedDigitalTwin is {compression_ratio:.1%} the size of BrandGuidelines")
    print(f"  BrandGuidelines: {guidelines_size} chars")
    print(f"  CompressedDigitalTwin: {compressed_size} chars")
