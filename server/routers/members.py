"""Members router — invite, list, update role, remove members (Manager only)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client

from auth.dependencies import get_org_context, require_role
from auth.models import OrgContext, Role
from db.client import get_supabase_client
from services.org_service import OrgService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/organizations/{org_id}/members",
    tags=["members"],
)


# ── Request models ─────────────────────────────────────────────


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str  # manager, operator, technician, procurement, viewer


class UpdateRoleRequest(BaseModel):
    role: str


# ── Dependency ─────────────────────────────────────────────────


def _get_org_service(supabase: Client = Depends(get_supabase_client)) -> OrgService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return OrgService(supabase)


# ── Endpoints ──────────────────────────────────────────────────


@router.get("")
async def list_members(
    org_id: str,
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: OrgService = Depends(_get_org_service),
):
    """List all members of the organization (Manager only)."""
    members = await service.get_org_members(org_id)
    return {"members": members}


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: str,
    body: InviteMemberRequest,
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: OrgService = Depends(_get_org_service),
):
    """Invite a new member to the organization (Manager only)."""
    # Validate role
    valid_roles = {"manager", "operator", "technician", "procurement", "viewer"}
    if body.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    try:
        result = await service.invite_member(org_id, body.email, body.role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{user_id}")
async def update_member_role(
    org_id: str,
    user_id: str,
    body: UpdateRoleRequest,
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: OrgService = Depends(_get_org_service),
):
    """Change a member's role (Manager only)."""
    valid_roles = {"manager", "operator", "technician", "procurement", "viewer"}
    if body.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    try:
        result = await service.update_member_role(org_id, user_id, body.role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{user_id}")
async def remove_member(
    org_id: str,
    user_id: str,
    org: OrgContext = Depends(get_org_context),
    _manager: None = Depends(require_role(Role.MANAGER)),
    service: OrgService = Depends(_get_org_service),
):
    """Remove a member from the organization (Manager only)."""
    try:
        result = await service.remove_member(org_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
