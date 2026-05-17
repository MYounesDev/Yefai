"""Files router — avatar upload, org file management via Supabase Storage."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from supabase import Client

from auth.dependencies import get_current_user, get_org_context, require_role
from auth.models import CurrentUser, OrgContext, Role
from db.client import get_supabase_client
from services.file_service import FileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])


# ── Dependency ─────────────────────────────────────────────────


def _get_file_service(supabase: Client = Depends(get_supabase_client)) -> FileService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return FileService(supabase)


# ── Endpoints ──────────────────────────────────────────────────


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    service: FileService = Depends(_get_file_service),
):
    """Upload or replace user avatar."""
    if not file.content_type:
        raise HTTPException(status_code=400, detail="File content type required")

    file_data = await file.read()
    try:
        url = await service.upload_avatar(current_user.id, file_data, file.content_type)
        return {"avatar_url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("")
async def list_org_files(
    category: str | None = None,
    page: int = 1,
    limit: int = 20,
    org: OrgContext = Depends(get_org_context),
    service: FileService = Depends(_get_file_service),
):
    """List files for the active organization."""
    return await service.get_org_files(org.org_id, category, page, limit)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_org_file(
    file: UploadFile = File(...),
    category: str = "general",
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: FileService = Depends(_get_file_service),
):
    """Upload a file to the organization (Manager only)."""
    if not file.content_type or not file.filename:
        raise HTTPException(status_code=400, detail="File name and content type required")

    file_data = await file.read()
    try:
        result = await service.upload_org_file(
            org.org_id, org.user.id, file_data, file.filename, file.content_type, category
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: FileService = Depends(_get_file_service),
):
    """Delete a file (Manager only)."""
    try:
        await service.delete_file(file_id, org.org_id)
        return {"message": "File deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{file_id}/url")
async def get_file_download_url(
    file_id: str,
    org: OrgContext = Depends(get_org_context),
    service: FileService = Depends(_get_file_service),
):
    """Generate a signed download URL for a private file."""
    try:
        url = await service.get_signed_url(file_id, org.org_id)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
