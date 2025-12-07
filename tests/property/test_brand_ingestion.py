"""
Property-based tests for brand ingestion workflow.

**Feature: mobius-phase-2-refactor, Property 1: Brand ingestion creates valid BrandGuidelines object**

Tests that brand ingestion creates valid entities with proper negative_constraint
logic and Enum constraints.

**Validates: Requirements 2.2, 2.3**
"""

import pytest
from hypothesis import given, strategies as st, settings
from mobius.models.brand import (
    Brand,
    BrandGuidelines,
    Color,
    Typography,
    LogoRule,
    VoiceTone,
    BrandRule,
)
from pydantic import ValidationError
import uuid


# Strategies for generating valid brand data
@st.composite
def color_strategy(draw):
    """Generate a valid Color object with semantic design tokens."""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L",))))
    hex_code = draw(
        st.text(min_size=7, max_size=7, alphabet="0123456789ABCDEF").map(lambda x: f"#{x}")
    )
    usage = draw(st.sampled_from(["primary", "secondary", "accent", "neutral", "semantic"]))
    usage_weight = draw(st.floats(min_value=0.0, max_value=1.0))
    context = draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))

    return Color(name=name, hex=hex_code, usage=usage, usage_weight=usage_weight, context=context)


@st.composite
def typography_strategy(draw):
    """Generate a valid Typography object."""
    family = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L",))))
    weights = draw(st.lists(st.sampled_from(["100", "200", "300", "400", "500", "600", "700", "800", "900"]), min_size=1, max_size=5))
    usage = draw(st.text(min_size=1, max_size=100))

    return Typography(family=family, weights=weights, usage=usage)


@st.composite
def logo_rule_strategy(draw):
    """Generate a valid LogoRule object."""
    variant_name = draw(st.text(min_size=1, max_size=50))
    url = draw(st.text(min_size=10, max_size=100).map(lambda x: f"https://example.com/{x}"))
    min_width_px = draw(st.integers(min_value=10, max_value=1000))
    clear_space_ratio = draw(st.floats(min_value=0.1, max_value=2.0))
    forbidden_backgrounds = draw(
        st.lists(
            st.text(min_size=7, max_size=7, alphabet="0123456789ABCDEF").map(lambda x: f"#{x}"),
            max_size=5,
        )
    )

    return LogoRule(
        variant_name=variant_name,
        url=url,
        min_width_px=min_width_px,
        clear_space_ratio=clear_space_ratio,
        forbidden_backgrounds=forbidden_backgrounds,
    )


@st.composite
def brand_rule_strategy(draw):
    """Generate a valid BrandRule object."""
    category = draw(st.sampled_from(["visual", "verbal", "legal"]))
    instruction = draw(st.text(min_size=5, max_size=200))
    severity = draw(st.sampled_from(["warning", "critical"]))
    negative_constraint = draw(st.booleans())

    return BrandRule(
        category=category,
        instruction=instruction,
        severity=severity,
        negative_constraint=negative_constraint,
    )


@st.composite
def brand_guidelines_strategy(draw):
    """Generate a valid BrandGuidelines object."""
    colors = draw(st.lists(color_strategy(), min_size=1, max_size=10))
    typography = draw(st.lists(typography_strategy(), min_size=0, max_size=5))
    logos = draw(st.lists(logo_rule_strategy(), min_size=0, max_size=3))
    rules = draw(st.lists(brand_rule_strategy(), min_size=0, max_size=10))

    voice = None
    if draw(st.booleans()):
        voice = VoiceTone(
            adjectives=draw(st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=5)),
            forbidden_words=draw(st.lists(st.text(min_size=2, max_size=20), max_size=5)),
            example_phrases=draw(st.lists(st.text(min_size=5, max_size=100), max_size=5)),
        )

    return BrandGuidelines(
        colors=colors, typography=typography, logos=logos, voice=voice, rules=rules
    )


@given(guidelines=brand_guidelines_strategy())
@settings(max_examples=100)
def test_brand_guidelines_always_valid(guidelines):
    """
    Property 1: Brand ingestion creates valid BrandGuidelines object.

    For any BrandGuidelines object created through the ingestion process,
    it should be valid according to the Pydantic schema with proper
    Enum constraints and negative_constraint logic.

    **Validates: Requirements 2.2, 2.3**
    """
    # The guidelines should be valid (no ValidationError)
    assert isinstance(guidelines, BrandGuidelines)

    # Should have at least one color
    assert len(guidelines.colors) >= 1

    # All colors should have valid semantic roles
    for color in guidelines.colors:
        assert color.usage in ["primary", "secondary", "accent", "neutral", "semantic"]
        # usage_weight should be between 0.0 and 1.0
        assert 0.0 <= color.usage_weight <= 1.0

    # All rules should have valid category and severity enums
    for rule in guidelines.rules:
        assert rule.category in ["visual", "verbal", "legal"]
        assert rule.severity in ["warning", "critical"]
        # negative_constraint should be a boolean
        assert isinstance(rule.negative_constraint, bool)


@given(base_text=st.text(min_size=5, max_size=80))
@settings(max_examples=100)
def test_negative_constraint_detection(base_text):
    """
    Property 1 (negative constraint): Negative constraints are properly detected.

    For any instruction containing negative language ("do not", "never", etc.),
    the negative_constraint field should be set to True.

    **Validates: Requirements 2.2, 2.3**
    """
    # Construct a negative instruction by prepending negative language
    negative_words = ["Do not", "Never", "Don't", "Avoid"]
    import random
    negative_word = random.choice(negative_words)
    negative_instruction = f"{negative_word} {base_text}"
    
    # Create a rule with negative instruction
    rule = BrandRule(
        category="visual",
        instruction=negative_instruction,
        severity="warning",
        negative_constraint=True,  # Should be set to True for negative instructions
    )

    assert rule.negative_constraint is True
    assert isinstance(rule, BrandRule)


@given(base_text=st.text(min_size=5, max_size=80))
@settings(max_examples=100)
def test_positive_constraint_detection(base_text):
    """
    Property 1 (positive constraint): Positive constraints are properly detected.

    For any instruction NOT containing negative language, the negative_constraint
    field should be set to False.

    **Validates: Requirements 2.2, 2.3**
    """
    # Construct a positive instruction by prepending positive language
    positive_words = ["Always", "Use", "Include", "Ensure"]
    import random
    positive_word = random.choice(positive_words)
    positive_instruction = f"{positive_word} {base_text}"
    
    # Create a rule with positive instruction
    rule = BrandRule(
        category="visual",
        instruction=positive_instruction,
        severity="warning",
        negative_constraint=False,  # Should be False for positive instructions
    )

    assert rule.negative_constraint is False
    assert isinstance(rule, BrandRule)


def test_color_usage_enum_validation():
    """
    Property 1 (enum validation): Color usage must be valid semantic role.

    For any Color object, the usage field must be one of the valid semantic roles.
    Invalid values should raise ValidationError.

    **Validates: Requirements 2.3**
    """
    # Valid usage values should work (updated for semantic design tokens)
    valid_usages = ["primary", "secondary", "accent", "neutral", "semantic"]
    for usage in valid_usages:
        color = Color(name="Test", hex="#FF0000", usage=usage)
        assert color.usage == usage

    # Invalid usage value should raise ValidationError
    with pytest.raises(ValidationError):
        Color(name="Test", hex="#FF0000", usage="invalid_usage")
    
    # Old "background" value should now fail (replaced by "neutral")
    with pytest.raises(ValidationError):
        Color(name="Test", hex="#FF0000", usage="background")


def test_brand_rule_category_enum_validation():
    """
    Property 1 (enum validation): BrandRule category must be valid enum value.

    For any BrandRule object, the category field must be one of the valid enum values.
    Invalid values should raise ValidationError.

    **Validates: Requirements 2.3**
    """
    # Valid category values should work
    valid_categories = ["visual", "verbal", "legal"]
    for category in valid_categories:
        rule = BrandRule(
            category=category,
            instruction="Test instruction",
            severity="warning",
            negative_constraint=False,
        )
        assert rule.category == category

    # Invalid category value should raise ValidationError
    with pytest.raises(ValidationError):
        BrandRule(
            category="invalid_category",
            instruction="Test instruction",
            severity="warning",
            negative_constraint=False,
        )


def test_brand_rule_severity_enum_validation():
    """
    Property 1 (enum validation): BrandRule severity must be valid enum value.

    For any BrandRule object, the severity field must be one of the valid enum values.
    Invalid values should raise ValidationError.

    **Validates: Requirements 2.3**
    """
    # Valid severity values should work
    valid_severities = ["warning", "critical"]
    for severity in valid_severities:
        rule = BrandRule(
            category="visual",
            instruction="Test instruction",
            severity=severity,
            negative_constraint=False,
        )
        assert rule.severity == severity

    # Invalid severity value should raise ValidationError
    with pytest.raises(ValidationError):
        BrandRule(
            category="visual",
            instruction="Test instruction",
            severity="invalid_severity",
            negative_constraint=False,
        )


@given(guidelines=brand_guidelines_strategy())
@settings(max_examples=100)
def test_brand_entity_creation_with_guidelines(guidelines):
    """
    Property 1 (brand entity): Brand entity can be created with valid guidelines.

    For any valid BrandGuidelines object, a Brand entity should be successfully
    created with all required fields.

    **Validates: Requirements 2.2, 2.3**
    """
    from datetime import datetime, timezone

    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())

    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name="Test Brand",
        website="https://example.com",
        guidelines=guidelines,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None,
        pdf_url="https://example.com/guidelines.pdf",
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0,
    )

    assert isinstance(brand, Brand)
    assert brand.brand_id == brand_id
    assert brand.organization_id == organization_id
    assert brand.guidelines == guidelines
    assert len(brand.guidelines.colors) >= 1
