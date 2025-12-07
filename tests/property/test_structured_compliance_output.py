"""
Property-based tests for structured compliance output.

**Feature: gemini-3-dual-architecture, Property 13: Structured Compliance Output**

Tests that audit operations return structured compliance scores with category 
breakdowns and violation details.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import BrandGuidelines, Color, Typography, LogoRule, VoiceTone, BrandRule
from mobius.models.compliance import ComplianceScore, CategoryScore, Violation, Severity


# Strategy for generating image URIs
@st.composite
def image_uri_strategy(draw):
    """Generate various image URI formats."""
    uri_type = draw(st.sampled_from(['http', 'https', 'data']))
    
    if uri_type in ['http', 'https']:
        domain = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=20))
        path = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=30))
        return f"{uri_type}://{domain}.com/{path}.jpg"
    else:
        # data URI
        import base64
        data = draw(st.binary(min_size=10, max_size=100))
        encoded = base64.b64encode(data).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"


# Strategy for generating BrandGuidelines
@st.composite
def brand_guidelines_strategy(draw):
    """Generate random BrandGuidelines with various components."""
    # Generate colors
    num_colors = draw(st.integers(min_value=0, max_value=5))
    colors = []
    for _ in range(num_colors):
        hex_code = draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))
        colors.append(Color(
            name=draw(st.text(min_size=3, max_size=20)),
            hex=f"#{hex_code}",
            usage=draw(st.sampled_from(['primary', 'secondary', 'accent', 'neutral', 'semantic'])),
            usage_weight=draw(st.floats(min_value=0.0, max_value=1.0)),
            context=draw(st.one_of(st.none(), st.text(min_size=5, max_size=50)))
        ))
    
    # Generate typography
    num_fonts = draw(st.integers(min_value=0, max_value=3))
    typography = []
    for _ in range(num_fonts):
        typography.append(Typography(
            family=draw(st.text(min_size=3, max_size=20)),
            weights=draw(st.lists(st.text(min_size=3, max_size=10), min_size=1, max_size=3)),
            usage=draw(st.text(min_size=5, max_size=50))
        ))
    
    # Generate logos
    num_logos = draw(st.integers(min_value=0, max_value=2))
    logos = []
    for _ in range(num_logos):
        logos.append(LogoRule(
            variant_name=draw(st.text(min_size=3, max_size=20)),
            url=f"https://example.com/logo-{draw(st.integers(min_value=1, max_value=100))}.png",
            min_width_px=draw(st.integers(min_value=50, max_value=500)),
            clear_space_ratio=draw(st.floats(min_value=0.1, max_value=1.0)),
            forbidden_backgrounds=draw(st.lists(st.text(min_size=7, max_size=7), min_size=0, max_size=3))
        ))
    
    # Generate voice
    voice = None
    if draw(st.booleans()):
        voice = VoiceTone(
            adjectives=draw(st.lists(st.text(min_size=3, max_size=15), min_size=1, max_size=5)),
            forbidden_words=draw(st.lists(st.text(min_size=3, max_size=15), min_size=0, max_size=3)),
            example_phrases=draw(st.lists(st.text(min_size=5, max_size=50), min_size=0, max_size=3))
        )
    
    # Generate rules
    num_rules = draw(st.integers(min_value=0, max_value=5))
    rules = []
    for _ in range(num_rules):
        rules.append(BrandRule(
            category=draw(st.sampled_from(['visual', 'verbal', 'legal'])),
            instruction=draw(st.text(min_size=10, max_size=100)),
            severity=draw(st.sampled_from(['warning', 'critical'])),
            negative_constraint=draw(st.booleans())
        ))
    
    return BrandGuidelines(
        colors=colors,
        typography=typography,
        logos=logos,
        voice=voice,
        rules=rules
    )


# Strategy for generating valid ComplianceScore responses
@st.composite
def compliance_score_response_strategy(draw):
    """Generate a valid ComplianceScore for mocking."""
    # Generate 1-4 category scores
    num_categories = draw(st.integers(min_value=1, max_value=4))
    categories = []
    
    for _ in range(num_categories):
        category_name = draw(st.sampled_from(['colors', 'typography', 'layout', 'logo_usage']))
        score = draw(st.floats(min_value=0.0, max_value=100.0))
        passed = score >= 80.0
        
        # Generate 0-3 violations
        num_violations = draw(st.integers(min_value=0, max_value=3))
        violations = []
        for _ in range(num_violations):
            violations.append(Violation(
                category=category_name,
                description=draw(st.text(min_size=10, max_size=100)),
                severity=draw(st.sampled_from(list(Severity))),
                fix_suggestion=draw(st.text(min_size=10, max_size=100))
            ))
        
        categories.append(CategoryScore(
            category=category_name,
            score=score,
            passed=passed,
            violations=violations
        ))
    
    # Calculate overall score as average
    overall_score = sum(cat.score for cat in categories) / len(categories)
    approved = overall_score >= 80.0
    
    return ComplianceScore(
        overall_score=overall_score,
        categories=categories,
        approved=approved,
        summary=draw(st.text(min_size=20, max_size=200))
    )


# Property 13: Structured Compliance Output
@given(
    image_uri=image_uri_strategy(),
    guidelines=brand_guidelines_strategy(),
    expected_response=compliance_score_response_strategy()
)
@hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_returns_structured_compliance_score(
    image_uri: str,
    guidelines: BrandGuidelines,
    expected_response: ComplianceScore
):
    """
    **Feature: gemini-3-dual-architecture, Property 13: Structured Compliance Output**
    
    *For any* completed audit, the system should return a structured compliance score 
    containing category breakdowns and violation details.
    
    **Validates: Requirements 4.4**
    
    This property test verifies that audit_compliance returns a properly structured
    ComplianceScore with all required fields.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client for image download
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance
        
        # Mock the generate_content method to return the expected ComplianceScore
        mock_result = MagicMock()
        mock_result.text = expected_response.model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance
        result = await client.audit_compliance(image_uri, guidelines)
        
        # Verify result is a ComplianceScore instance
        assert isinstance(result, ComplianceScore), (
            f"audit_compliance should return ComplianceScore, got {type(result)}"
        )
        
        # Verify overall_score is present and bounded
        assert hasattr(result, 'overall_score'), "ComplianceScore must have overall_score"
        assert 0 <= result.overall_score <= 100, (
            f"overall_score must be between 0 and 100, got {result.overall_score}"
        )
        
        # Verify categories list is present
        assert hasattr(result, 'categories'), "ComplianceScore must have categories"
        assert isinstance(result.categories, list), "categories must be a list"
        
        # Verify each category has required structure
        for category in result.categories:
            assert isinstance(category, CategoryScore), (
                f"Each category must be CategoryScore, got {type(category)}"
            )
            assert hasattr(category, 'category'), "CategoryScore must have category name"
            assert hasattr(category, 'score'), "CategoryScore must have score"
            assert hasattr(category, 'passed'), "CategoryScore must have passed flag"
            assert hasattr(category, 'violations'), "CategoryScore must have violations list"
            
            # Verify category score is bounded
            assert 0 <= category.score <= 100, (
                f"Category score must be between 0 and 100, got {category.score}"
            )
            
            # Verify violations structure
            assert isinstance(category.violations, list), "violations must be a list"
            for violation in category.violations:
                assert isinstance(violation, Violation), (
                    f"Each violation must be Violation, got {type(violation)}"
                )
                assert hasattr(violation, 'category'), "Violation must have category"
                assert hasattr(violation, 'description'), "Violation must have description"
                assert hasattr(violation, 'severity'), "Violation must have severity"
                assert hasattr(violation, 'fix_suggestion'), "Violation must have fix_suggestion"
        
        # Verify approved flag is present
        assert hasattr(result, 'approved'), "ComplianceScore must have approved flag"
        assert isinstance(result.approved, bool), "approved must be a boolean"
        
        # Verify summary is present
        assert hasattr(result, 'summary'), "ComplianceScore must have summary"
        assert isinstance(result.summary, str), "summary must be a string"
        
        print(f"✓ audit_compliance returns structured ComplianceScore with {len(result.categories)} categories")


@given(
    image_uri=image_uri_strategy(),
    guidelines=brand_guidelines_strategy()
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_categories_include_standard_types(
    image_uri: str,
    guidelines: BrandGuidelines
):
    """
    **Feature: gemini-3-dual-architecture, Property 13: Structured Compliance Output**
    
    *For any* audit result, the categories should include standard compliance types
    (colors, typography, layout, logo_usage).
    
    **Validates: Requirements 4.4**
    
    This property test verifies that audit results contain expected category types.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance
        
        # Create a compliance score with standard categories
        standard_categories = [
            CategoryScore(
                category="colors",
                score=85.0,
                passed=True,
                violations=[]
            ),
            CategoryScore(
                category="typography",
                score=90.0,
                passed=True,
                violations=[]
            ),
            CategoryScore(
                category="layout",
                score=80.0,
                passed=True,
                violations=[]
            ),
            CategoryScore(
                category="logo_usage",
                score=95.0,
                passed=True,
                violations=[]
            )
        ]
        
        compliance_score = ComplianceScore(
            overall_score=87.5,
            categories=standard_categories,
            approved=True,
            summary="All categories meet brand standards"
        )
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = compliance_score.model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance
        result = await client.audit_compliance(image_uri, guidelines)
        
        # Extract category names
        category_names = {cat.category for cat in result.categories}
        
        # Verify standard categories are present
        expected_categories = {'colors', 'typography', 'layout', 'logo_usage'}
        assert expected_categories.issubset(category_names), (
            f"Audit should include standard categories {expected_categories}, got {category_names}"
        )
        
        print(f"✓ Audit includes standard categories: {category_names}")


@given(
    image_uri=image_uri_strategy(),
    guidelines=brand_guidelines_strategy()
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_violations_have_fix_suggestions(
    image_uri: str,
    guidelines: BrandGuidelines
):
    """
    **Feature: gemini-3-dual-architecture, Property 13: Structured Compliance Output**
    
    *For any* audit result with violations, each violation should include a fix suggestion.
    
    **Validates: Requirements 4.4**
    
    This property test verifies that violations include actionable fix suggestions.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance
        
        # Create a compliance score with violations
        categories_with_violations = [
            CategoryScore(
                category="colors",
                score=65.0,
                passed=False,
                violations=[
                    Violation(
                        category="colors",
                        description="Using unapproved color #FF00FF",
                        severity=Severity.HIGH,
                        fix_suggestion="Replace with approved primary color #0057B8"
                    ),
                    Violation(
                        category="colors",
                        description="Insufficient contrast ratio",
                        severity=Severity.MEDIUM,
                        fix_suggestion="Increase contrast to at least 4.5:1"
                    )
                ]
            ),
            CategoryScore(
                category="typography",
                score=70.0,
                passed=False,
                violations=[
                    Violation(
                        category="typography",
                        description="Using Comic Sans font",
                        severity=Severity.CRITICAL,
                        fix_suggestion="Use approved font family: Helvetica Neue"
                    )
                ]
            )
        ]
        
        compliance_score = ComplianceScore(
            overall_score=67.5,
            categories=categories_with_violations,
            approved=False,
            summary="Multiple violations detected"
        )
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = compliance_score.model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance
        result = await client.audit_compliance(image_uri, guidelines)
        
        # Verify all violations have fix suggestions
        total_violations = 0
        for category in result.categories:
            for violation in category.violations:
                total_violations += 1
                assert violation.fix_suggestion, (
                    f"Violation '{violation.description}' must have a fix_suggestion"
                )
                assert len(violation.fix_suggestion) > 0, (
                    f"fix_suggestion must not be empty for violation '{violation.description}'"
                )
        
        # Verify we actually tested some violations
        assert total_violations > 0, "Test should include violations to verify fix suggestions"
        
        print(f"✓ All {total_violations} violations include fix suggestions")


def test_compliance_score_json_serialization():
    """
    **Feature: gemini-3-dual-architecture, Property 13: Structured Compliance Output**
    
    Verify that ComplianceScore can be serialized to and from JSON.
    
    **Validates: Requirements 4.4**
    
    This test ensures the structured output can be properly serialized for API responses.
    """
    # Create a sample compliance score
    compliance_score = ComplianceScore(
        overall_score=85.5,
        categories=[
            CategoryScore(
                category="colors",
                score=90.0,
                passed=True,
                violations=[]
            ),
            CategoryScore(
                category="typography",
                score=75.0,
                passed=False,
                violations=[
                    Violation(
                        category="typography",
                        description="Font family does not match brand guidelines",
                        severity=Severity.MEDIUM,
                        fix_suggestion="Use Arial or Helvetica"
                    )
                ]
            )
        ],
        approved=True,
        summary="Asset meets brand standards with minor typography issues"
    )
    
    # Serialize to JSON
    json_str = compliance_score.model_dump_json()
    assert isinstance(json_str, str), "model_dump_json should return a string"
    assert len(json_str) > 0, "JSON string should not be empty"
    
    # Deserialize from JSON
    deserialized = ComplianceScore.model_validate_json(json_str)
    assert isinstance(deserialized, ComplianceScore), "Should deserialize to ComplianceScore"
    
    # Verify round-trip preserves data
    assert deserialized.overall_score == compliance_score.overall_score
    assert len(deserialized.categories) == len(compliance_score.categories)
    assert deserialized.approved == compliance_score.approved
    assert deserialized.summary == compliance_score.summary
    
    print("✓ ComplianceScore serializes and deserializes correctly")
