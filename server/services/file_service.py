"""File service — Supabase Storage operations for avatars and org files.

NOT for MATWI images — those stay on local disk via images.file_path.
This handles:
  - User avatars (public bucket: avatars)
  - Org reports, documents, exports (private bucket: org-files)
"""

import logging
import time

from supabase import Client

logger = logging.getLogger(__name__)


class FileService:
    """Wraps Supabase Storage for file upload, download, and management."""

    AVATAR_BUCKET = "avatars"
    ORG_FILES_BUCKET = "org-files"
    AVATAR_MAX_SIZE = 2 * 1024 * 1024  # 2 MB
    ORG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_DOC_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def upload_avatar(
        self,
        user_id: str,
        file_data: bytes,
        content_type: str,
    ) -> str:
        """Upload user avatar to the avatars bucket.

        Replaces any existing avatar. Updates profiles.avatar_url.

        Returns:
            Public URL of the uploaded avatar.
        """
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(self.ALLOWED_IMAGE_TYPES)}")

        if len(file_data) > self.AVATAR_MAX_SIZE:
            raise ValueError(f"File too large. Maximum: {self.AVATAR_MAX_SIZE // (1024 * 1024)} MB")

        ext = content_type.split("/")[-1]
        if ext == "jpeg":
            ext = "jpg"
        storage_path = f"{user_id}/avatar.{ext}"

        # Upload (upsert to replace existing)
        self.supabase.storage.from_(self.AVATAR_BUCKET).upload(
            storage_path,
            file_data,
            file_options={"content-type": content_type, "upsert": "true"},
        )

        # Get public URL
        public_url = self.supabase.storage.from_(self.AVATAR_BUCKET).get_public_url(storage_path)

        # Update profile
        try:
            self.supabase.table("profiles").update({"avatar_url": public_url}).eq(
                "id", user_id
            ).execute()
        except Exception as e:
            logger.warning("Failed to update profile avatar_url: %s", e)

        return public_url

    async def upload_org_file(
        self,
        org_id: str,
        user_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
        category: str = "general",
    ) -> dict:
        """Upload a file to the org-files bucket.

        Creates a row in the files table to track metadata.

        Returns:
            File record dict.
        """
        if content_type not in self.ALLOWED_DOC_TYPES:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(self.ALLOWED_DOC_TYPES)}")

        if len(file_data) > self.ORG_FILE_MAX_SIZE:
            raise ValueError(
                f"File too large. Maximum: {self.ORG_FILE_MAX_SIZE // (1024 * 1024)} MB"
            )

        timestamp = int(time.time())
        safe_filename = filename.replace(" ", "_")
        storage_path = f"{org_id}/{category}/{timestamp}_{safe_filename}"

        # Upload
        self.supabase.storage.from_(self.ORG_FILES_BUCKET).upload(
            storage_path,
            file_data,
            file_options={"content-type": content_type},
        )

        # Generate signed URL (1 hour default)
        signed = self.supabase.storage.from_(self.ORG_FILES_BUCKET).create_signed_url(
            storage_path, 3600
        )
        file_url = signed.get("signedURL", "") if isinstance(signed, dict) else ""

        # Insert file record
        file_record = {
            "org_id": org_id,
            "uploaded_by": user_id,
            "bucket": self.ORG_FILES_BUCKET,
            "storage_path": storage_path,
            "file_url": file_url,
            "file_name": filename,
            "file_size": len(file_data),
            "mime_type": content_type,
            "category": category,
        }

        result = self.supabase.table("files").insert(file_record).execute()
        return result.data[0] if result.data else file_record

    async def get_org_files(
        self,
        org_id: str,
        category: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """List files for an organization, optionally filtered by category."""
        query = self.supabase.table("files").select("*", count="exact").eq("org_id", org_id)

        if category:
            query = query.eq("category", category)

        offset = (page - 1) * limit
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

        return {
            "files": result.data or [],
            "total": result.count or 0,
            "page": page,
            "limit": limit,
        }

    async def delete_file(self, file_id: str, org_id: str) -> bool:
        """Delete a file from storage and the files table."""
        # Get file record
        result = (
            self.supabase.table("files")
            .select("bucket, storage_path")
            .eq("id", file_id)
            .eq("org_id", org_id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise ValueError("File not found")

        bucket = result.data["bucket"]
        path = str(result.data["storage_path"])

        # Delete from storage
        try:
            self.supabase.storage.from_(bucket).remove([path])
        except Exception as e:
            logger.warning("Failed to delete from storage: %s", e)

        # Delete from files table
        self.supabase.table("files").delete().eq("id", file_id).execute()

        return True

    async def get_signed_url(self, file_id: str, org_id: str, expires_in: int = 3600) -> str:
        """Generate a signed URL for private file access."""
        result = (
            self.supabase.table("files")
            .select("bucket, storage_path")
            .eq("id", file_id)
            .eq("org_id", org_id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise ValueError("File not found")

        signed = self.supabase.storage.from_(result.data["bucket"]).create_signed_url(
            result.data["storage_path"], expires_in
        )

        return signed.get("signedURL", "") if isinstance(signed, dict) else ""
