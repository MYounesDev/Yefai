# Phase B3 — Supabase Storage & Files

> Set up Supabase Storage buckets for profile pictures, org reports/docs. Create `files` table to track uploads. This is SEPARATE from the MATWI image storage (which stays on local disk).

## Key Rule

**MATWI images (`images` table with `file_path` → local disk) are NOT affected.** Supabase Storage is only for:
- User profile pictures (avatars)
- Organization reports/documents
- General file uploads from the dashboard

## Task

### 1. Supabase Storage Buckets

Create via Supabase dashboard or API:
- **`avatars`** — Public bucket for profile pictures. Max 2MB per file. Allowed types: image/jpeg, image/png, image/webp.
- **`org-files`** — Private bucket for org documents/reports. Max 10MB per file. Allowed types: image/*, application/pdf, text/csv, application/vnd.openxmlformats-officedocument.*.

### 2. Files Table (`005_auth_tables.sql` — add to existing migration or new)

```sql
CREATE TABLE IF NOT EXISTS files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by     UUID NOT NULL,   -- auth.users(id)
    bucket          TEXT NOT NULL,    -- 'avatars' or 'org-files'
    storage_path    TEXT NOT NULL,    -- Path within Supabase Storage bucket
    file_url        TEXT NOT NULL,    -- Full public/signed URL
    file_name       TEXT NOT NULL,    -- Original filename
    file_size       BIGINT,          -- Size in bytes
    mime_type       TEXT,
    category        TEXT DEFAULT 'general'
                    CHECK (category IN ('avatar', 'report', 'document', 'export', 'general')),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_files_org_id ON files(org_id);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_files_category ON files(category);
```

### 3. File Service (`services/file_service.py`)

```python
class FileService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def upload_avatar(self, user_id: str, file_data: bytes, content_type: str) -> str:
        """Upload user avatar to 'avatars' bucket. Returns public URL.
        Path: avatars/{user_id}/avatar.{ext}
        Updates profiles.avatar_url"""

    async def upload_org_file(
        self, org_id: str, user_id: str, file_data: bytes,
        filename: str, content_type: str, category: str = "general"
    ) -> dict:
        """Upload file to 'org-files' bucket. Returns file record.
        Path: org-files/{org_id}/{category}/{timestamp}_{filename}
        Creates row in files table."""

    async def get_org_files(self, org_id: str, category: str = None) -> list[dict]:
        """List files for an org, optionally filtered by category."""

    async def delete_file(self, file_id: str, org_id: str) -> bool:
        """Delete file from storage and files table."""

    async def get_signed_url(self, file_id: str, expires_in: int = 3600) -> str:
        """Generate signed URL for private file access."""
```

### 4. Files Router (`routers/files.py`)

```python
router = APIRouter(prefix="/api/files", tags=["files"])

POST /api/files/avatar
  Auth: Bearer token
  Body: multipart/form-data (file)
  → Upload avatar to Supabase Storage, update profile, return URL

GET /api/files
  Auth: Bearer token + org member
  Query: category, page, limit
  → List org files from files table

POST /api/files/upload
  Auth: Bearer token + Manager role
  Body: multipart/form-data (file, category)
  → Upload to org-files bucket, create files row, return file record

DELETE /api/files/{file_id}
  Auth: Bearer token + Manager role
  → Delete from storage + files table

GET /api/files/{file_id}/url
  Auth: Bearer token + org member
  → Generate signed URL for download (private files)
```

## Deliverables

- [ ] Supabase Storage buckets created (avatars, org-files)
- [ ] `files` table added to migration
- [ ] `services/file_service.py` — upload, list, delete, signed URL
- [ ] `routers/files.py` — avatar upload, org file upload/list/delete
- [ ] Avatar upload updates `profiles.avatar_url`
- [ ] Files are properly org-scoped
- [ ] File size/type validation
