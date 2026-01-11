"""
Cloud Storage Service
Handles profile picture uploads to AWS S3 or Cloudflare R2.

Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-003, FR-045)
"""

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
from app.config import settings
import uuid
from pathlib import Path


class StorageService:
    """Service for uploading files to cloud storage (S3/R2)."""

    def __init__(self):
        """Initialize S3 client with configuration from settings."""
        if not settings.S3_BUCKET_NAME:
            self.s3_client = None
            return

        # Create S3 client (works for both AWS S3 and Cloudflare R2)
        self.s3_client = boto3.client(
            's3',
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL  # Required for Cloudflare R2
        )

        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL or settings.S3_ENDPOINT_URL

    def is_configured(self) -> bool:
        """Check if cloud storage is configured."""
        return self.s3_client is not None

    async def upload_profile_picture(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Upload profile picture to cloud storage.

        Args:
            file: Uploaded file from FastAPI
            user_id: User ID for organizing files

        Returns:
            str: Public URL of uploaded image

        Raises:
            HTTPException 400: Invalid file type or size
            HTTPException 503: Cloud storage not configured or upload failed
        """
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud storage is not configured"
            )

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )

        # Read file content
        content = await file.read()

        # Validate file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of 5MB (got {len(content) / 1024 / 1024:.2f}MB)"
            )

        # Generate unique filename
        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"profiles/user-{user_id}/{uuid.uuid4()}{file_extension}"

        # Upload to S3/R2
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=content,
                ContentType=file.content_type,
                ACL='public-read'  # Make publicly accessible
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to cloud storage: {str(e)}"
            )

        # Construct public URL
        if self.public_url:
            public_url = f"{self.public_url.rstrip('/')}/{self.bucket_name}/{unique_filename}"
        else:
            # Fallback to standard S3 URL format
            public_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{unique_filename}"

        return public_url


# Singleton instance
storage_service = StorageService()
