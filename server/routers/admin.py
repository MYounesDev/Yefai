"""Admin router — platform-level management (platform admins only)."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client

from auth.dependencies import require_platform_admin
from auth.models import CurrentUser
from db.client import get_supabase_client
from services.org_service import OrgService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Request models ─────────────────────────────────────────────


class AdminCreateOrgRequest(BaseModel):
    name: str
    plan: str = "free"
    manager_email: EmailStr


class ResolveTicketRequest(BaseModel):
    resolution: str


# ── Dependency ────────��────────────────────────────────────────


def _get_org_service(supabase: Client = Depends(get_supabase_client)) -> OrgService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return OrgService(supabase)


# ── Endpoints ──────────────────────────────────────────────────


@router.get("/stats")
async def get_platform_stats(
    admin: CurrentUser = Depends(require_platform_admin),
    service: OrgService = Depends(_get_org_service),
):
    """Get platform-wide statistics (admin only)."""
    stats = await service.admin_get_platform_stats()
    return stats


@router.get("/organizations")
async def list_organizations(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    plan: str | None = None,
    admin: CurrentUser = Depends(require_platform_admin),
    service: OrgService = Depends(_get_org_service),
):
    """List all organizations (admin only)."""
    return await service.admin_list_organizations(page, limit, search, plan)


@router.post("/organizations", status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: AdminCreateOrgRequest,
    admin: CurrentUser = Depends(require_platform_admin),
    service: OrgService = Depends(_get_org_service),
):
    """Create a new organization and invite the initial manager (admin only)."""
    try:
        result = await service.admin_create_organization(body.name, body.plan, body.manager_email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/organizations/{org_id}")
async def get_organization_admin(
    org_id: str,
    admin: CurrentUser = Depends(require_platform_admin),
    service: OrgService = Depends(_get_org_service),
):
    """Get org details + members + usage stats (admin view — no factory data)."""
    org_data = await service.admin_get_organization(org_id)
    if not org_data:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org_data


@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    admin: CurrentUser = Depends(require_platform_admin),
    service: OrgService = Depends(_get_org_service),
):
    """List all platform users (admin only)."""
    return await service.admin_list_users(page, limit, search)


# ── Support Tickets ────────────────────────────────────────────


@router.get("/support-tickets")
async def list_support_tickets(
    ticket_status: str | None = None,
    admin: CurrentUser = Depends(require_platform_admin),
    supabase: Client = Depends(get_supabase_client),
):
    """List all support tickets (admin only)."""
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")

    query = supabase.table("support_tickets").select("*, organizations(name)")

    if ticket_status:
        query = query.eq("status", ticket_status)

    result = query.order("created_at", desc=True).execute()

    tickets = []
    for row in result.data or []:
        org = row.pop("organizations", {}) or {}
        row["org_name"] = org.get("name", "")
        tickets.append(row)

    return {"tickets": tickets}


@router.post("/support-tickets/{ticket_id}/resolve")
async def resolve_support_ticket(
    ticket_id: str,
    body: ResolveTicketRequest,
    admin: CurrentUser = Depends(require_platform_admin),
    supabase: Client = Depends(get_supabase_client),
):
    """Resolve a support ticket (admin only)."""
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")

    result = (
        supabase.table("support_tickets")
        .update(
            {
                "status": "resolved",
                "resolution": body.resolution,
                "resolved_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        )
        .eq("id", ticket_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return result.data[0]
