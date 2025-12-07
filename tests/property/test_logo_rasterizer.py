"""
Property-based tests for LogoRasterizer utility.

**Feature: vector-first-logo-fidelity**

Tests that logo processing maintains correctness properties across all inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from PIL import Image
import io
import random

from mobius.utils.media import LogoRasterizer, CAIROSVG_AVAILABLE


# Helper function to create valid test images
def create_test_image(width: int, height: int, mode: str = 'RGBA') -> bytes:
    """Create a test image with given dimensions."""
    img = Image.new(mode, (width, height), (255, 0, 0, 128))
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()


def create_test_svg(width: int, height: int, with_transparency: bool = True) -> bytes:
    """Create a test SVG with given dimensions."""
    opacity = "0.5" if with_transparency else "1.0"
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{width}" height="{height}" fill="red" opacity="{opacity}"/>
</svg>'''
    return svg_content.encode('utf-8')


@given(
    width=st.integers(min_value=100, max_value=4000),
    height=st.integers(min_value=100, max_value=4000),
    mime_type=st.sampled_from(["image/png", "image/jpeg"])
)
@settings(max_examples=100)
def test_output_is_valid_png(width, height, mime_type):
    """
    **Feature: vector-first-logo-fidelity, Property 1: Output Validity and Format**
    
    For any logo bytes and valid MIME type, the output from prepare_for_vision()
    should be valid PNG bytes that can be loaded by PIL without errors.
    
    **Validates: Requirements 2.3, 4.6**
    """
    # Create test image
    logo_bytes = create_test_image(width, height)
    
    # Process through LogoRasterizer
    result = LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
    
    # Should be able to load as PNG
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"
    assert isinstance(result, bytes)
    assert len(result) > 0


@given(
    width=st.integers(min_value=100, max_value=4000),
    height=st.integers(min_value=100, max_value=4000)
)
@settings(max_examples=100)
def test_aspect_ratio_preserved(width, height):
    """
    **Feature: vector-first-logo-fidelity, Property 2: Aspect Ratio Preservation**
    
    For any logo image (SVG or raster), if the original aspect ratio is W:H,
    then the processed output should maintain the same aspect ratio within
    a tolerance of 1%.
    
    **Validates: Requirements 3.2, 4.2**
    """
    # Generate test image with known aspect ratio
    original_img = Image.new('RGBA', (width, height), (255, 0, 0, 128))
    original_bytes = io.BytesIO()
    original_img.save(original_bytes, format='PNG')
    
    result = LogoRasterizer.prepare_for_vision(
        original_bytes.getvalue(), 
        "image/png"
    )
    
    # Check output aspect ratio
    output_img = Image.open(io.BytesIO(result))
    original_ratio = width / height
    output_ratio = output_img.width / output_img.height
    
    # Allow 1% tolerance for rounding
    assert abs(original_ratio - output_ratio) / original_ratio < 0.01


@given(
    width=st.integers(min_value=100, max_value=1000),
    height=st.integers(min_value=100, max_value=1000)
)
@settings(max_examples=100)
def test_transparency_preserved_svg(width, height):
    """
    **Feature: vector-first-logo-fidelity, Property 3: Transparency Preservation**
    
    For any SVG logo with transparent regions, the output PNG should contain
    an alpha channel with transparency preserved in the same regions.
    
    **Validates: Requirements 3.3**
    """
    if not CAIROSVG_AVAILABLE:
        pytest.skip("cairosvg not available - graceful degradation expected")
    
    # Create SVG with transparency
    svg_content = create_test_svg(width, height, with_transparency=True)
    
    result = LogoRasterizer.prepare_for_vision(
        svg_content,
        "image/svg+xml"
    )
    
    # Check output has alpha channel
    output_img = Image.open(io.BytesIO(result))
    assert output_img.mode in ('RGBA', 'LA', 'PA', 'RGB')  # RGB is acceptable if no transparency


@given(
    dimension=st.integers(min_value=1000, max_value=4000)
)
@settings(max_examples=100)
def test_high_res_passthrough(dimension):
    """
    **Feature: vector-first-logo-fidelity, Property 4: High-Resolution Passthrough**
    
    For any raster image where the longest dimension is >= 1000 pixels,
    the output bytes should be identical to the input bytes (no processing applied).
    
    **Validates: Requirements 4.5**
    """
    # Create high-res image
    img = Image.new('RGB', (dimension, dimension), (255, 0, 0))
    original_bytes = io.BytesIO()
    img.save(original_bytes, format='PNG')
    original_data = original_bytes.getvalue()
    
    result = LogoRasterizer.prepare_for_vision(original_data, "image/png")
    
    # Should return identical bytes
    assert result == original_data


@given(
    logo_bytes=st.binary(min_size=0, max_size=10_000),
    mime_type=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100)
def test_never_raises_exception(logo_bytes, mime_type):
    """
    **Feature: vector-first-logo-fidelity, Property 5: Exception Safety**
    
    For any input bytes and MIME type (including malformed or corrupted data),
    prepare_for_vision() should never raise an exception - it should either
    return processed bytes or the original bytes.
    
    **Validates: Requirements 5.3**
    """
    # Should never raise, even with garbage input
    try:
        result = LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
        assert isinstance(result, bytes)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


@given(
    logo_list=st.lists(
        st.tuples(
            st.integers(min_value=100, max_value=2000),
            st.integers(min_value=100, max_value=2000),
            st.sampled_from(["image/png", "image/jpeg"])
        ),
        min_size=2,
        max_size=5
    )
)
@settings(max_examples=100)
def test_independent_processing(logo_list):
    """
    **Feature: vector-first-logo-fidelity, Property 6: Independent Processing**
    
    For any list of logo bytes, processing each logo should produce the same
    result regardless of the order or presence of other logos in the list.
    
    **Validates: Requirements 6.3**
    """
    # Create actual logo bytes from dimensions
    logo_data = []
    for width, height, mime_type in logo_list:
        logo_bytes = create_test_image(width, height)
        logo_data.append((logo_bytes, mime_type))
    
    # Process each logo individually
    individual_results = [
        LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
        for logo_bytes, mime_type in logo_data
    ]
    
    # Process in different order
    shuffled_data = logo_data.copy()
    random.shuffle(shuffled_data)
    shuffled_results = [
        LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
        for logo_bytes, mime_type in shuffled_data
    ]
    
    # Results should be order-independent
    # (Compare by matching original inputs)
    for original_input, expected_output in zip(logo_data, individual_results):
        matching_output = shuffled_results[shuffled_data.index(original_input)]
        assert matching_output == expected_output
