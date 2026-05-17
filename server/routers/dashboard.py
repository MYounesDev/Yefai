"""Dashboard router — aggregated overview and health."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _get_dashboard_service(supabase: Client = Depends(get_supabase_client)) -> DashboardService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return DashboardService(supabase)


@router.get("/overview")
async def get_overview(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_DASHBOARD)),
    service: DashboardService = Depends(_get_dashboard_service),
) -> dict[str, Any]:
    """Aggregated dashboard data (org-scoped)."""
    return await service.get_overview(org.org_id)


@router.get("/health")
async def get_health(
    org: OrgContext = Depends(get_org_context),
    service: DashboardService = Depends(_get_dashboard_service),
) -> dict[str, Any]:
    """System health status across all services (auth-protected)."""
    status = await service.get_health_status()
    status["last_check"] = datetime.utcnow().isoformat() + "Z"
    return status
