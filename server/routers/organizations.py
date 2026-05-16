"""Organizations router — list user orgs, switch org, org details, update."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from auth.dependencies import get_current_user, get_org_context
from auth.models import CurrentUser, OrgContext, Role
from auth.permissions import Permission
from db.client import get_supabase_client
from services.org_service import OrgService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


# ── Request models ─────────────────────────────────────────────


class SwitchOrgRequest(BaseModel):
    org_id: str


class UpdateOrgRequest(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    settings: dict | None = None


# ── Dependency ─────────────────────────────────────────────────


def _get_org_service(supabase: Client = Depends(get_supabase_client)) -> OrgService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return OrgService(supabase)


# ── Endpoints ──────────────────────────────────────────────────


@router.get("")
async def list_my_organizations(
    current_user: CurrentUser = Depends(get_current_user),
    service: OrgService = Depends(_get_org_service),
):
    """List all organizations the current user belongs to."""
    orgs = await service.get_user_organizations(current_user.id)
    return {"organizations": orgs}


@router.post("/switch")
async def switch_organization(
    body: SwitchOrgRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: OrgService = Depends(_get_org_service),
):
    """Switch to a different organization (validates membership)."""
    try:
        result = await service.switch_organization(current_user.id, body.org_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.get("/{org_id}")
async def get_organization_details(
    org_id: str,
    org: OrgContext = Depends(get_org_context),
    service: OrgService = Depends(_get_org_service),
):
    """Get details of the active organization."""
    details = await service.get_organization_details(org_id)
    if not details:
        raise HTTPException(status_code=404, detail="Organization not found")
    return details


@router.patch("/{org_id}")
async def update_organization(
    org_id: str,
    body: UpdateOrgRequest,
    org: OrgContext = Depends(get_org_context),
    service: OrgService = Depends(_get_org_service),
):
    """Update organization info (Manager only)."""
    if org.role != Role.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update organization settings")

    try:
        result = await service.update_organization(
            org_id, body.model_dump(exclude_none=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
