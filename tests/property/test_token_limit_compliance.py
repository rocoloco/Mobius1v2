"""
Property-based tests for CompressedDigitalTwin token limit compliance.

**Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**

Tests that CompressedDigitalTwin serialization stays under 60k token limit.
"""

from hypothesis import given, strategies as st, settings, assume, HealthCheck
import pytest
from mobius.models.brand import CompressedDigitalTwin


# Strategy for generating hex color codes
@st.composite
def hex_colors(draw):
    """Generate valid hex color codes."""
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    return f"#{r:02X}{g:02X}{b:02X}"


# Strategy for generating font family names
font_families_strategy = st.sampled_from([
    "Helvetica Neue",
    "Arial",
    "Georgia",
    "Times New Roman",
    "Courier New",
    "Verdana",
    "Trebuchet MS",
    "Comic Sans MS",
    "Impact",
    "Palatino",
    "Garamond",
    "Bookman",
    "Avant Garde",
    "Roboto",
    "Open Sans",
    "Lato",
    "Montserrat",
    "Source Sans Pro",
    "Raleway",
    "PT Sans"
])


# Strategy for generating concise visual rules
visual_rules_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")),
    min_size=10,
    max_size=100
).filter(lambda x: x.strip() != "")


# Property 4: Token Limit Compliance
@given(
    primary_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    secondary_colors=st.lists(hex_colors(), min_size=0, max_size=10),
    font_families=st.lists(font_families_strategy, min_size=0, max_size=10),
    visual_dos=st.lists(visual_rules_strategy, min_size=0, max_size=50),
    visual_donts=st.lists(visual_rules_strategy, min_size=0, max_size=50),
    logo_placement=st.one_of(st.none(), st.text(min_size=5, max_size=50)),
    logo_min_size=st.one_of(st.none(), st.text(min_size=5, max_size=30))
)
@settings(max_examples=100)
def test_compressed_twin_token_limit_compliance(
    primary_colors,
    secondary_colors,
    font_families,
    visual_dos,
    visual_donts,
    logo_placement,
    logo_min_size
):
    """
    **Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**
    
    *For any* Compressed Digital Twin serialization, the JSON representation should be under 60,000 tokens.
    
    **Validates: Requirements 2.4**
    
    This property test verifies that all compressed twins fit within the Vision Model's context window.
    """
    # Create compressed twin with generated data
    compressed_twin = CompressedDigitalTwin(
        primary_colors=primary_colors,
        secondary_colors=secondary_colors,
        font_families=font_families,
        visual_dos=visual_dos,
        visual_donts=visual_donts,
        logo_placement=logo_placement,
        logo_min_size=logo_min_size
    )
    
    # Estimate token count
    token_count = compressed_twin.estimate_tokens()
    
    # Verify token count is under 60k
    assert token_count < 60000, (
        f"CompressedDigitalTwin exceeds 60k token limit: {token_count} tokens. "
        f"Primary colors: {len(primary_colors)}, Secondary colors: {len(secondary_colors)}, "
        f"Fonts: {len(font_families)}, Visual dos: {len(visual_dos)}, "
        f"Visual donts: {len(visual_donts)}"
    )
    
    # Verify validate_size() method returns True
    assert compressed_twin.validate_size(), (
        f"validate_size() returned False for {token_count} tokens"
    )


@given(
    primary_colors=st.lists(hex_colors(), min_size=0, max_size=5),
    secondary_colors=st.lists(hex_colors(), min_size=0, max_size=5),
    font_families=st.lists(font_families_strategy, min_size=0, max_size=5)
)
@settings(max_examples=100)
def test_minimal_compressed_twin_always_valid(
    primary_colors,
    secondary_colors,
    font_families
):
    """
    **Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**
    
    *For any* minimal Compressed Digital Twin (only colors and fonts), 
    the token count should be well under the limit.
    
    **Validates: Requirements 2.4**
    
    This property test verifies that even with minimal data, the model works correctly.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=primary_colors,
        secondary_colors=secondary_colors,
        font_families=font_families
    )
    
    token_count = compressed_twin.estimate_tokens()
    
    # Minimal twins should be well under the limit (< 1000 tokens)
    assert token_count < 1000, (
        f"Minimal CompressedDigitalTwin has unexpectedly high token count: {token_count}"
    )
    
    assert compressed_twin.validate_size()


def test_empty_compressed_twin_is_valid():
    """
    **Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**
    
    Verify that an empty CompressedDigitalTwin is valid and under token limit.
    
    **Validates: Requirements 2.4**
    
    This test ensures the model handles edge cases correctly.
    """
    compressed_twin = CompressedDigitalTwin()
    
    token_count = compressed_twin.estimate_tokens()
    
    # Empty twin should have very few tokens (just the JSON structure)
    assert token_count < 100, (
        f"Empty CompressedDigitalTwin has unexpectedly high token count: {token_count}"
    )
    
    assert compressed_twin.validate_size()
    
    print(f"✓ Empty CompressedDigitalTwin has {token_count} tokens")


def test_estimate_tokens_is_deterministic():
    """
    **Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**
    
    Verify that estimate_tokens() returns consistent results for the same input.
    
    **Validates: Requirements 2.4**
    
    This test ensures token counting is deterministic.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#0057B8", "#FF5733"],
        secondary_colors=["#C70039"],
        font_families=["Helvetica Neue", "Georgia"],
        visual_dos=["Use primary colors for headers"],
        visual_donts=["Never use Comic Sans"]
    )
    
    # Call estimate_tokens multiple times
    token_count_1 = compressed_twin.estimate_tokens()
    token_count_2 = compressed_twin.estimate_tokens()
    token_count_3 = compressed_twin.estimate_tokens()
    
    # All counts should be identical
    assert token_count_1 == token_count_2 == token_count_3, (
        f"estimate_tokens() is not deterministic: {token_count_1}, {token_count_2}, {token_count_3}"
    )
    
    print(f"✓ estimate_tokens() is deterministic: {token_count_1} tokens")


@given(
    # Generate a very large compressed twin to test the upper boundary
    visual_dos=st.lists(
        st.text(min_size=50, max_size=100),
        min_size=50,
        max_size=100
    ),
    visual_donts=st.lists(
        st.text(min_size=50, max_size=100),
        min_size=50,
        max_size=100
    )
)
@settings(
    max_examples=50, 
    suppress_health_check=[HealthCheck.large_base_example, HealthCheck.data_too_large]
)
def test_large_compressed_twin_boundary(visual_dos, visual_donts):
    """
    **Feature: gemini-3-dual-architecture, Property 4: Token Limit Compliance**
    
    *For any* large Compressed Digital Twin with many rules, verify token counting works.
    
    **Validates: Requirements 2.4**
    
    This property test explores the upper boundary of the token limit.
    """
    compressed_twin = CompressedDigitalTwin(
        primary_colors=["#0057B8"] * 10,
        secondary_colors=["#FF5733"] * 10,
        font_families=["Helvetica Neue"] * 10,
        visual_dos=visual_dos,
        visual_donts=visual_donts
    )
    
    token_count = compressed_twin.estimate_tokens()
    
    # This might exceed the limit, which is expected for very large inputs
    # The test verifies that estimate_tokens() works correctly
    if token_count >= 60000:
        # validate_size() should return False
        assert not compressed_twin.validate_size(), (
            f"validate_size() should return False for {token_count} tokens"
        )
    else:
        # validate_size() should return True
        assert compressed_twin.validate_size(), (
            f"validate_size() should return True for {token_count} tokens"
        )
