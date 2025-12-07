"""
Unit tests for LogoRasterizer utility.

Tests SVG rasterization, raster upscaling, error handling, and graceful degradation.
"""

import io
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

from mobius.utils.media import LogoRasterizer, CAIROSVG_AVAILABLE


# Test fixtures - SVG content
VALID_SVG_WIDE = b'''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="100" fill="red"/>
</svg>'''

VALID_SVG_TALL = b'''<svg width="100" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="200" fill="blue"/>
</svg>'''

VALID_SVG_SQUARE = b'''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" fill="green"/>
</svg>'''

VALID_SVG_WITH_TRANSPARENCY = b'''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" fill="red" opacity="0.5"/>
</svg>'''

MALFORMED_SVG = b'''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" fill="red"
</svg>'''


def create_test_image(width: int, height: int, color: tuple = (255, 0, 0), mode: str = 'RGB') -> bytes:
    """Helper to create test raster images."""
    img = Image.new(mode, (width, height), color)
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()


class TestSVGRasterization:
    """Test SVG to PNG conversion."""
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_svg_to_png_conversion_valid_input(self):
        """Test SVG to PNG conversion with valid SVG input."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg+xml")
        
        # Should return PNG bytes
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_aspect_ratio_preservation_wide_svg(self):
        """Test aspect ratio preservation for wide SVG (2:1 ratio)."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_WIDE, "image/svg+xml", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Original aspect ratio is 2:1 (200:100)
        aspect_ratio = width / height
        expected_ratio = 2.0
        
        # Allow 1% tolerance
        assert abs(aspect_ratio - expected_ratio) / expected_ratio < 0.01
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_aspect_ratio_preservation_tall_svg(self):
        """Test aspect ratio preservation for tall SVG (1:2 ratio)."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_TALL, "image/svg+xml", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Original aspect ratio is 1:2 (100:200)
        aspect_ratio = width / height
        expected_ratio = 0.5
        
        # Allow 1% tolerance
        assert abs(aspect_ratio - expected_ratio) / expected_ratio < 0.01
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_aspect_ratio_preservation_square_svg(self):
        """Test aspect ratio preservation for square SVG (1:1 ratio)."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg+xml", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Original aspect ratio is 1:1 (100:100)
        aspect_ratio = width / height
        expected_ratio = 1.0
        
        # Allow 1% tolerance
        assert abs(aspect_ratio - expected_ratio) / expected_ratio < 0.01
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_transparency_preservation_in_svg_output(self):
        """Test transparency preservation in SVG output."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_WITH_TRANSPARENCY, "image/svg+xml")
        
        img = Image.open(io.BytesIO(result))
        
        # PNG should have alpha channel
        assert img.mode in ('RGBA', 'LA', 'PA'), f"Expected alpha channel, got mode: {img.mode}"


class TestRasterUpscaling:
    """Test raster image upscaling."""
    
    def test_raster_upscaling_for_small_images(self):
        """Test raster upscaling for images < 1000px."""
        # Create a 500x500 image
        small_image = create_test_image(500, 500)
        
        result = LogoRasterizer.prepare_for_vision(small_image, "image/png", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Should be upscaled to target_dim
        assert max(width, height) == 2048
        
        # Should maintain aspect ratio (square)
        assert width == height
    
    def test_passthrough_for_high_res_images(self):
        """Test passthrough for images >= 1000px."""
        # Create a 1500x1500 image
        large_image = create_test_image(1500, 1500)
        
        result = LogoRasterizer.prepare_for_vision(large_image, "image/png", target_dim=2048)
        
        # Should return original bytes unchanged
        assert result == large_image
    
    def test_passthrough_at_threshold(self):
        """Test passthrough for images exactly at 1000px threshold."""
        # Create a 1000x1000 image
        threshold_image = create_test_image(1000, 1000)
        
        result = LogoRasterizer.prepare_for_vision(threshold_image, "image/png", target_dim=2048)
        
        # Should return original bytes unchanged
        assert result == threshold_image
    
    def test_upscaling_preserves_aspect_ratio_wide(self):
        """Test upscaling preserves aspect ratio for wide images."""
        # Create a 800x400 image (2:1 ratio)
        wide_image = create_test_image(800, 400)
        
        result = LogoRasterizer.prepare_for_vision(wide_image, "image/png", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Should maintain 2:1 aspect ratio
        aspect_ratio = width / height
        expected_ratio = 2.0
        
        # Allow 1% tolerance
        assert abs(aspect_ratio - expected_ratio) / expected_ratio < 0.01
    
    def test_upscaling_preserves_aspect_ratio_tall(self):
        """Test upscaling preserves aspect ratio for tall images."""
        # Create a 400x800 image (1:2 ratio)
        tall_image = create_test_image(400, 800)
        
        result = LogoRasterizer.prepare_for_vision(tall_image, "image/png", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        width, height = img.size
        
        # Should maintain 1:2 aspect ratio
        aspect_ratio = width / height
        expected_ratio = 0.5
        
        # Allow 1% tolerance
        assert abs(aspect_ratio - expected_ratio) / expected_ratio < 0.01


class TestMIMETypeDetection:
    """Test MIME type detection for various formats."""
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_svg_mime_type_standard(self):
        """Test standard SVG MIME type detection."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg+xml")
        
        # Should process as SVG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_svg_mime_type_short(self):
        """Test short SVG MIME type detection."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg")
        
        # Should process as SVG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_svg_mime_type_case_insensitive(self):
        """Test case-insensitive SVG MIME type detection."""
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "IMAGE/SVG+XML")
        
        # Should process as SVG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    def test_png_mime_type(self):
        """Test PNG MIME type detection."""
        png_image = create_test_image(500, 500)
        result = LogoRasterizer.prepare_for_vision(png_image, "image/png", target_dim=2048)
        
        # Should process as raster
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    def test_jpeg_mime_type(self):
        """Test JPEG MIME type detection."""
        # Create JPEG image
        img = Image.new('RGB', (500, 500), (255, 0, 0))
        output = io.BytesIO()
        img.save(output, format='JPEG')
        jpeg_image = output.getvalue()
        
        result = LogoRasterizer.prepare_for_vision(jpeg_image, "image/jpeg", target_dim=2048)
        
        # Should process as raster and convert to PNG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    def test_webp_mime_type(self):
        """Test WEBP MIME type detection."""
        # Create WEBP image
        img = Image.new('RGB', (500, 500), (255, 0, 0))
        output = io.BytesIO()
        img.save(output, format='WEBP')
        webp_image = output.getvalue()
        
        result = LogoRasterizer.prepare_for_vision(webp_image, "image/webp", target_dim=2048)
        
        # Should process as raster and convert to PNG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"


class TestErrorHandling:
    """Test error handling with malformed inputs."""
    
    @pytest.mark.skipif(not CAIROSVG_AVAILABLE, reason="cairosvg not available")
    def test_malformed_svg_returns_original(self):
        """Test error handling with malformed SVG."""
        result = LogoRasterizer.prepare_for_vision(MALFORMED_SVG, "image/svg+xml")
        
        # Should return original bytes on error
        assert result == MALFORMED_SVG
    
    def test_corrupted_raster_image_returns_original(self):
        """Test error handling with corrupted raster image."""
        corrupted_data = b"This is not a valid image file"
        
        result = LogoRasterizer.prepare_for_vision(corrupted_data, "image/png")
        
        # Should return original bytes on error
        assert result == corrupted_data
    
    def test_empty_bytes_returns_original(self):
        """Test error handling with empty bytes."""
        empty_data = b""
        
        result = LogoRasterizer.prepare_for_vision(empty_data, "image/png")
        
        # Should return original bytes on error
        assert result == empty_data
    
    def test_invalid_mime_type_returns_original(self):
        """Test error handling with invalid MIME type."""
        test_data = b"some random data"
        
        result = LogoRasterizer.prepare_for_vision(test_data, "application/octet-stream")
        
        # Should return original bytes on error
        assert result == test_data


class TestGracefulDegradation:
    """Test graceful degradation when cairosvg is missing."""
    
    def test_svg_without_cairosvg_returns_original(self):
        """Test graceful degradation when cairosvg is missing."""
        # Mock CAIROSVG_AVAILABLE to False
        with patch('mobius.utils.media.CAIROSVG_AVAILABLE', False):
            result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg+xml")
            
            # Should return original bytes when cairosvg is not available
            assert result == VALID_SVG_SQUARE
    
    def test_raster_processing_works_without_cairosvg(self):
        """Test that raster processing still works without cairosvg."""
        # Mock CAIROSVG_AVAILABLE to False
        with patch('mobius.utils.media.CAIROSVG_AVAILABLE', False):
            small_image = create_test_image(500, 500)
            result = LogoRasterizer.prepare_for_vision(small_image, "image/png", target_dim=2048)
            
            # Should still upscale raster images
            img = Image.open(io.BytesIO(result))
            width, height = img.size
            assert max(width, height) == 2048


class TestOutputFormat:
    """Test that output is always PNG format."""
    
    def test_svg_output_is_png(self):
        """Test that SVG processing outputs PNG."""
        if not CAIROSVG_AVAILABLE:
            pytest.skip("cairosvg not available")
        
        result = LogoRasterizer.prepare_for_vision(VALID_SVG_SQUARE, "image/svg+xml")
        
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    def test_jpeg_converted_to_png(self):
        """Test that JPEG is converted to PNG."""
        # Create JPEG image
        img = Image.new('RGB', (500, 500), (255, 0, 0))
        output = io.BytesIO()
        img.save(output, format='JPEG')
        jpeg_image = output.getvalue()
        
        result = LogoRasterizer.prepare_for_vision(jpeg_image, "image/jpeg", target_dim=2048)
        
        # Output should be PNG
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
    
    def test_png_remains_png(self):
        """Test that PNG remains PNG."""
        png_image = create_test_image(500, 500)
        result = LogoRasterizer.prepare_for_vision(png_image, "image/png", target_dim=2048)
        
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
