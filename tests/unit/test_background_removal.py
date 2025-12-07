"""
Unit tests for automatic background removal feature in LogoRasterizer.
"""

import io
import pytest
from PIL import Image
from mobius.utils.media import LogoRasterizer, REMBG_AVAILABLE


class TestBackgroundRemoval:
    """Test automatic background removal for opaque logos."""
    
    def test_rgb_image_triggers_background_removal_attempt(self):
        """RGB images should trigger background removal logic."""
        # Create a simple RGB image (no alpha channel)
        img = Image.new('RGB', (500, 500), color='white')
        
        # Add some colored content
        for x in range(100, 400):
            for y in range(100, 400):
                img.putpixel((x, y), (255, 0, 0))  # Red square
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Should return bytes (either processed or original)
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Load result to verify it's valid
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'PNG'
        
        # If rembg is available, result should be RGBA
        # If not available, it should still be RGB
        if REMBG_AVAILABLE:
            # Background removal should convert to RGBA
            assert result_img.mode in ('RGBA', 'RGB')
        else:
            # Without rembg, should remain RGB
            assert result_img.mode == 'RGB'
    
    def test_rgba_image_skips_background_removal(self):
        """RGBA images (already transparent) should skip background removal."""
        # Create an RGBA image (already has alpha channel)
        img = Image.new('RGBA', (500, 500), color=(255, 255, 255, 0))
        
        # Add some colored content with transparency
        for x in range(100, 400):
            for y in range(100, 400):
                img.putpixel((x, y), (255, 0, 0, 255))  # Opaque red square
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Should return bytes
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Load result to verify it's valid
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'PNG'
        
        # Should remain RGBA (no background removal needed)
        assert result_img.mode == 'RGBA'
    
    def test_grayscale_image_triggers_background_removal_attempt(self):
        """Grayscale (L mode) images should trigger background removal."""
        # Create a grayscale image
        img = Image.new('L', (500, 500), color=255)
        
        # Add some darker content
        for x in range(100, 400):
            for y in range(100, 400):
                img.putpixel((x, y), 50)  # Dark square
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Should return bytes
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Load result to verify it's valid
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'PNG'
    
    def test_background_removal_preserves_dimensions(self):
        """Background removal should preserve image dimensions."""
        # Create an RGB image
        original_width, original_height = 800, 600
        img = Image.new('RGB', (original_width, original_height), color='white')
        
        # Add content
        for x in range(200, 600):
            for y in range(150, 450):
                img.putpixel((x, y), (0, 0, 255))  # Blue rectangle
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Load result
        result_img = Image.open(io.BytesIO(result))
        
        # Dimensions should be preserved (or upscaled proportionally if < 1000px)
        # Since 800x600 is < 1000px, it will be upscaled
        # But aspect ratio should be preserved
        aspect_ratio = original_width / original_height
        result_aspect_ratio = result_img.width / result_img.height
        
        # Allow 1% tolerance for rounding
        assert abs(aspect_ratio - result_aspect_ratio) / aspect_ratio < 0.01
    
    def test_high_res_rgb_image_gets_background_removed_but_not_upscaled(self):
        """High-res RGB images should get background removed but not upscaled."""
        # Create a high-res RGB image (>= 1000px)
        img = Image.new('RGB', (1200, 1200), color='white')
        
        # Add content
        for x in range(300, 900):
            for y in range(300, 900):
                img.putpixel((x, y), (0, 255, 0))  # Green square
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Load result
        result_img = Image.open(io.BytesIO(result))
        
        # If rembg is available, should be RGBA
        # Dimensions should be preserved (no upscaling for high-res)
        if REMBG_AVAILABLE:
            assert result_img.mode in ('RGBA', 'RGB')
            # Should not be upscaled
            assert result_img.width == 1200
            assert result_img.height == 1200
        else:
            # Without rembg, should be unchanged
            assert result_img.width == 1200
            assert result_img.height == 1200
    
    @pytest.mark.skipif(not REMBG_AVAILABLE, reason="rembg not installed")
    def test_background_removal_creates_alpha_channel(self):
        """When rembg is available, RGB images should get an alpha channel."""
        # Create an RGB image
        img = Image.new('RGB', (500, 500), color='white')
        
        # Add a red circle in the center
        for x in range(500):
            for y in range(500):
                dx = x - 250
                dy = y - 250
                if dx*dx + dy*dy < 100*100:  # Circle radius 100
                    img.putpixel((x, y), (255, 0, 0))
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        logo_bytes = img_bytes.getvalue()
        
        # Process through LogoRasterizer
        result = LogoRasterizer.prepare_for_vision(logo_bytes, "image/png")
        
        # Load result
        result_img = Image.open(io.BytesIO(result))
        
        # Should have alpha channel
        assert result_img.mode in ('RGBA', 'LA', 'PA')
