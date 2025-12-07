"""
File storage operations.

Provides operations for Supabase Storage (PDFs and images).
"""

from mobius.storage.database import get_supabase_client
from mobius.constants import BRANDS_BUCKET, ASSETS_BUCKET
from typing import BinaryIO, Optional
import httpx
import structlog

logger = structlog.get_logger()


class FileStorage:
    """Storage operations for files in Supabase Storage."""

    def __init__(self):
        self.client = get_supabase_client()

    async def upload_pdf(self, file: bytes, brand_id: str, filename: str = "guidelines.pdf") -> str:
        """
        Upload brand guidelines PDF to Supabase Storage.

        Args:
            file: PDF file bytes
            brand_id: UUID of the brand
            filename: Name of the file (default: guidelines.pdf)

        Returns:
            Public CDN URL for the uploaded file

        Raises:
            Exception: If upload fails
        """
        logger.info("uploading_pdf", brand_id=brand_id, size_bytes=len(file))

        path = f"{brand_id}/{filename}"

        try:
            # Upload to Supabase Storage
            result = self.client.storage.from_(BRANDS_BUCKET).upload(
                path, file, {"content-type": "application/pdf"}
            )

            # Get public URL
            url = self.client.storage.from_(BRANDS_BUCKET).get_public_url(path)

            logger.info("pdf_uploaded", brand_id=brand_id, url=url)
            return url

        except Exception as e:
            logger.error("pdf_upload_failed", brand_id=brand_id, error=str(e))
            raise

    async def upload_logo(self, file: bytes, brand_id: str, filename: str = "logo.png") -> str:
        """
        Upload brand logo image to Supabase Storage.
        
        Uses the assets bucket since brands bucket is configured for PDFs only.

        Args:
            file: Image file bytes (PNG format)
            brand_id: UUID of the brand
            filename: Name of the file (default: logo.png)

        Returns:
            Public CDN URL for the uploaded file

        Raises:
            Exception: If upload fails or file is invalid
        """
        logger.info("uploading_logo", brand_id=brand_id, size_bytes=len(file), filename=filename)

        # Determine if this is an SVG file
        is_svg = filename.lower().endswith(".svg")
        
        # If SVG, convert to PNG since Supabase Storage doesn't support SVG mime type
        if is_svg:
            try:
                file_str = file.decode('utf-8', errors='ignore')[:200]
                if '<svg' not in file_str.lower() and '<?xml' not in file_str.lower():
                    raise ValueError("File does not appear to be a valid SVG")
                logger.info("svg_validation_passed", brand_id=brand_id, size_bytes=len(file))
                
                # Convert SVG to PNG for storage (Supabase doesn't support SVG mime type)
                from mobius.utils.media import LogoRasterizer
                file = LogoRasterizer.prepare_for_vision(file, "image/svg+xml", target_dim=2048)
                filename = filename.replace(".svg", ".png")
                logger.info("svg_converted_to_png", brand_id=brand_id, new_filename=filename, size_bytes=len(file))
            except Exception as e:
                logger.error("svg_processing_failed", brand_id=brand_id, error=str(e))
                raise ValueError(f"Invalid or corrupted SVG file: {str(e)}")
        
        # Validate raster images (including converted SVGs)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(file))
            img.verify()  # Verify it's a valid image
            logger.info("logo_validation_passed", brand_id=brand_id, format=img.format if hasattr(img, 'format') else 'PNG', size=(img.width if hasattr(img, 'width') else 0, img.height if hasattr(img, 'height') else 0))
        except Exception as e:
            logger.error("logo_validation_failed", brand_id=brand_id, error=str(e), error_type=type(e).__name__)
            raise ValueError(f"Invalid image file: {str(e)}")

        # Determine content type from filename (after potential SVG conversion)
        content_type = "image/png"
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            content_type = "image/jpeg"
        elif filename.lower().endswith(".webp"):
            content_type = "image/webp"

        # Use assets bucket for images (brands bucket is PDF-only)
        path = f"logos/{brand_id}/{filename}"

        try:
            # Upload to assets bucket (accepts images)
            result = self.client.storage.from_(ASSETS_BUCKET).upload(
                path, 
                file,
                {
                    "content-type": content_type,
                    "upsert": "true"  # Allow overwriting if file exists
                }
            )

            # Get public URL
            url = self.client.storage.from_(ASSETS_BUCKET).get_public_url(path)

            logger.info("logo_uploaded", brand_id=brand_id, url=url, content_type=content_type, bucket=ASSETS_BUCKET)
            return url

        except Exception as e:
            logger.error("logo_upload_failed", brand_id=brand_id, error=str(e))
            raise

    async def upload_image(
        self, image_url: str, asset_id: str, filename: str = "image.png"
    ) -> str:
        """
        Download image from generation service and upload to Supabase Storage.

        Args:
            image_url: URL of the generated image
            asset_id: UUID of the asset
            filename: Name of the file (default: image.png)

        Returns:
            Public CDN URL for the uploaded file

        Raises:
            Exception: If download or upload fails
        """
        logger.info("uploading_image", asset_id=asset_id, source_url=image_url)

        try:
            # Download from generation service
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content

            logger.debug(
                "image_downloaded", asset_id=asset_id, size_bytes=len(image_bytes)
            )

            # Upload to Supabase Storage
            path = f"{asset_id}/{filename}"

            # Determine content type from filename
            content_type = "image/png"
            if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif filename.endswith(".webp"):
                content_type = "image/webp"

            result = self.client.storage.from_(ASSETS_BUCKET).upload(
                path, image_bytes, {"content-type": content_type}
            )

            # Get public CDN URL
            url = self.client.storage.from_(ASSETS_BUCKET).get_public_url(path)

            logger.info("image_uploaded", asset_id=asset_id, url=url)
            return url

        except Exception as e:
            logger.error("image_upload_failed", asset_id=asset_id, error=str(e))
            raise

    async def delete_file(self, bucket: str, path: str) -> bool:
        """
        Delete a file from Supabase Storage.

        Args:
            bucket: Storage bucket name ('brands' or 'assets')
            path: File path within the bucket

        Returns:
            True if successful

        Raises:
            Exception: If delete fails
        """
        logger.info("deleting_file", bucket=bucket, path=path)

        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info("file_deleted", bucket=bucket, path=path)
            return True

        except Exception as e:
            logger.error("file_delete_failed", bucket=bucket, path=path, error=str(e))
            raise

    async def get_file_url(self, bucket: str, path: str) -> str:
        """
        Get public CDN URL for a file.

        Args:
            bucket: Storage bucket name ('brands' or 'assets')
            path: File path within the bucket

        Returns:
            Public CDN URL
        """
        url = self.client.storage.from_(bucket).get_public_url(path)
        return url

    async def list_files(self, bucket: str, prefix: str = "") -> list:
        """
        List files in a bucket with optional prefix filter.

        Args:
            bucket: Storage bucket name ('brands' or 'assets')
            prefix: Optional path prefix to filter by

        Returns:
            List of file metadata dictionaries
        """
        logger.debug("listing_files", bucket=bucket, prefix=prefix)

        try:
            result = self.client.storage.from_(bucket).list(prefix)
            return result

        except Exception as e:
            logger.error("file_list_failed", bucket=bucket, prefix=prefix, error=str(e))
            raise
