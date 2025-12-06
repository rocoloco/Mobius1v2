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
