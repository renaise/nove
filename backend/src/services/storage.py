import base64
import logging
from dataclasses import dataclass
from uuid import uuid4

import aioboto3

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    success: bool
    url: str | None = None
    key: str | None = None
    error: str | None = None


class StorageService:
    """Service for storing images in Cloudflare R2 (S3-compatible)."""

    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.r2_bucket_name
        self.public_url = settings.r2_public_url
        self.endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"

    def _get_client_config(self):
        return {
            "service_name": "s3",
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": settings.r2_access_key_id,
            "aws_secret_access_key": settings.r2_secret_access_key,
            "region_name": "auto",
        }

    async def upload_image(
        self,
        image_data: bytes,
        folder: str = "try-on",
        content_type: str = "image/jpeg",
    ) -> UploadResult:
        """
        Upload an image to R2 storage.

        Args:
            image_data: Raw image bytes
            folder: Folder path in the bucket
            content_type: MIME type of the image

        Returns:
            UploadResult with the public URL or error
        """
        try:
            # Generate unique filename
            extension = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
            key = f"{folder}/{uuid4()}.{extension}"

            async with self.session.client(**self._get_client_config()) as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=image_data,
                    ContentType=content_type,
                )

            url = f"{self.public_url}/{key}"
            logger.info(f"Uploaded image to {url}")

            return UploadResult(
                success=True,
                url=url,
                key=key,
            )

        except Exception as e:
            logger.exception("Failed to upload image")
            return UploadResult(
                success=False,
                error=str(e),
            )

    async def upload_base64_image(
        self,
        base64_data: str,
        folder: str = "try-on",
        content_type: str = "image/jpeg",
    ) -> UploadResult:
        """Upload a base64-encoded image."""
        try:
            image_data = base64.b64decode(base64_data)
            return await self.upload_image(image_data, folder, content_type)
        except Exception as e:
            logger.exception("Failed to decode base64 image")
            return UploadResult(
                success=False,
                error=f"Invalid base64 data: {e}",
            )

    async def delete_image(self, key: str) -> bool:
        """Delete an image from R2 storage."""
        try:
            async with self.session.client(**self._get_client_config()) as client:
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key,
                )
            logger.info(f"Deleted image: {key}")
            return True
        except Exception as e:
            logger.exception(f"Failed to delete image: {key}")
            return False


# Singleton instance
storage_service = StorageService()
