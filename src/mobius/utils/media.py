"""Media processing utilities for logo preparation."""

import io
import structlog
from typing import Optional

# Optional import for SVG rasterization
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    # ImportError: cairosvg not installed
    # OSError: cairo system library not available (e.g., on Windows without GTK)
    CAIROSVG_AVAILABLE = False

# Optional import for automatic background removal
try:
    from rembg import remove as remove_background
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

from PIL import Image

logger = structlog.get_logger()


class LogoRasterizer:
    """
    Utility for preparing logo images for Vision Model consumption.
    
    Handles:
    - SVG to PNG rasterization at high resolution
    - Raster image upscaling with aspect ratio preservation
    - Graceful degradation when dependencies are missing
    """
    
    @staticmethod
    def prepare_for_vision(
        logo_bytes: bytes,
        mime_type: str,
        target_dim: int = 2048
    ) -> bytes:
        """
        Prepare logo for Vision Model by rasterizing or upscaling.
        
        Args:
            logo_bytes: Raw logo file bytes
            mime_type: MIME type (e.g., "image/svg+xml", "image/png")
            target_dim: Maximum dimension for output (default: 2048px)
            
        Returns:
            Processed logo bytes (always PNG format)
            
        Raises:
            Never raises - returns original bytes on error
        """
        try:
            # Detect if this is an SVG
            if "svg" in mime_type.lower():
                return LogoRasterizer._rasterize_svg(logo_bytes, target_dim)
            else:
                return LogoRasterizer._upscale_raster(logo_bytes, mime_type, target_dim)
        except Exception as e:
            logger.error(
                "logo_processing_failed",
                operation_type="prepare_for_vision",
                mime_type=mime_type,
                error_message=str(e),
                error_type=type(e).__name__,
                logo_size_bytes=len(logo_bytes)
            )
            return logo_bytes
    
    @staticmethod
    def _rasterize_svg(logo_bytes: bytes, target_dim: int) -> bytes:
        """
        Rasterize SVG to PNG at high resolution.
        
        Args:
            logo_bytes: SVG file bytes
            target_dim: Maximum dimension for output
            
        Returns:
            PNG bytes with transparency preserved
        """
        try:
            if not CAIROSVG_AVAILABLE:
                logger.error(
                    "cairosvg_not_available",
                    operation_type="svg_rasterization",
                    error_message="cairosvg library not installed",
                    error_type="ImportError"
                )
                return logo_bytes
            
            # Parse SVG to get dimensions
            # We'll use a simple approach: render at target_dim and let cairosvg handle aspect ratio
            # For more precise control, we could parse the SVG XML, but cairosvg handles this well
            
            # Convert SVG to PNG with target dimensions
            # cairosvg will preserve aspect ratio if we only specify one dimension
            # But for better control, we'll calculate both dimensions
            
            # First, render at a standard size to get aspect ratio
            try:
                # Render SVG to get dimensions
                png_bytes = cairosvg.svg2png(
                    bytestring=logo_bytes,
                    output_width=target_dim
                )
                
                logger.info(
                    "rasterizing_vector_logo",
                    operation_type="svg_rasterization",
                    target_dimension=target_dim
                )
                
                return png_bytes
                
            except Exception as e:
                logger.error(
                    "svg_parsing_failed",
                    operation_type="svg_rasterization",
                    mime_type="image/svg+xml",
                    error_message=str(e),
                    error_type=type(e).__name__
                )
                return logo_bytes
                
        except Exception as e:
            logger.error(
                "svg_rasterization_failed",
                operation_type="svg_rasterization",
                mime_type="image/svg+xml",
                error_message=str(e),
                error_type=type(e).__name__
            )
            return logo_bytes
    
    @staticmethod
    def _upscale_raster(logo_bytes: bytes, mime_type: str, target_dim: int) -> bytes:
        """
        Upscale raster image if needed, preserving aspect ratio.
        Automatically removes background from opaque images (RGB/L mode).
        
        Args:
            logo_bytes: Raster image bytes
            mime_type: MIME type of the image
            target_dim: Maximum dimension for output
            
        Returns:
            PNG bytes (original or upscaled, with transparency if needed)
        """
        try:
            # Load image with PIL
            try:
                img = Image.open(io.BytesIO(logo_bytes))
            except Exception as e:
                logger.error(
                    "corrupted_logo_detected",
                    operation_type="raster_upscaling",
                    mime_type=mime_type,
                    logo_size_bytes=len(logo_bytes),
                    error_message=str(e),
                    error_type=type(e).__name__,
                    solution="Re-ingest brand with valid logo file"
                )
                # Return original bytes - will fail downstream but with better error message
                return logo_bytes
            
            original_mode = img.mode
            
            # SMART TRANSPARENCY: Auto-remove background from opaque images
            # If image is opaque (RGB/L), strip the background automatically
            background_removed = False
            if REMBG_AVAILABLE and img.mode in ('RGB', 'L'):
                logger.info(
                    "removing_background_auto",
                    operation_type="background_removal",
                    mime_type=mime_type,
                    original_mode=img.mode
                )
                
                try:
                    # Convert PIL image to bytes for rembg
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    input_bytes = img_byte_arr.getvalue()
                    
                    # Magic happens here: remove background
                    output_bytes = remove_background(input_bytes)
                    
                    # Reload as RGBA for downstream processing
                    img = Image.open(io.BytesIO(output_bytes))
                    background_removed = True
                    
                    logger.info(
                        "background_removed_success",
                        operation_type="background_removal",
                        original_mode=original_mode,
                        new_mode=img.mode
                    )
                except Exception as e:
                    logger.warning(
                        "background_removal_failed",
                        operation_type="background_removal",
                        error_message=str(e),
                        error_type=type(e).__name__,
                        fallback="continuing_with_original"
                    )
                    # Reload original image if background removal failed
                    img = Image.open(io.BytesIO(logo_bytes))
            elif not REMBG_AVAILABLE and img.mode in ('RGB', 'L'):
                logger.warning(
                    "rembg_not_available",
                    operation_type="background_removal",
                    message="rembg library not installed, skipping auto-transparency",
                    original_mode=img.mode
                )
            
            # Get dimensions
            width, height = img.size
            longest_dim = max(width, height)
            
            # Check if upscaling is needed
            if longest_dim >= 1000:
                # High-resolution passthrough optimization
                # But if we removed background, we need to save the result
                if background_removed:
                    logger.info(
                        "saving_background_removed_logo",
                        operation_type="raster_passthrough",
                        width=width,
                        height=height,
                        background_removed=True
                    )
                    output = io.BytesIO()
                    img.save(output, format='PNG')
                    return output.getvalue()
                else:
                    logger.info(
                        "using_original_logo",
                        operation_type="raster_passthrough",
                        width=width,
                        height=height,
                        reason="already_high_resolution"
                    )
                    return logo_bytes
            
            # Calculate new dimensions preserving aspect ratio
            aspect_ratio = width / height
            if width > height:
                new_width = target_dim
                new_height = int(target_dim / aspect_ratio)
            else:
                new_height = target_dim
                new_width = int(target_dim * aspect_ratio)
            
            logger.info(
                "upscaling_low_res_logo",
                operation_type="raster_upscaling",
                original_width=width,
                original_height=height,
                target=target_dim,
                new_width=new_width,
                new_height=new_height,
                background_removed=background_removed
            )
            
            # Resize using Lanczos resampling
            upscaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as PNG to preserve transparency
            output = io.BytesIO()
            upscaled_img.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            logger.error(
                "raster_processing_failed",
                operation_type="raster_upscaling",
                mime_type=mime_type,
                error_message=str(e),
                error_type=type(e).__name__,
                logo_size_bytes=len(logo_bytes)
            )
            return logo_bytes
