"""Anomalies router — listing and updating anomalies."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from supabase import Client

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


class AnomalyStatusUpdate(BaseModel):
    status: str
    notes: str | None = None


@router.get("")
async def list_anomalies(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_ANOMALIES)),
    severity: str | None = None,
    wear_type: str | None = None,
    machine_id: str | None = None,
    status: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Paginated anomaly list."""
    query = supabase.table("anomalies").select("*").eq("org_id", org.org_id)

    if severity:
        query = query.eq("severity", severity)
    if wear_type:
        query = query.eq("wear_type", wear_type)
    if machine_id:
        query = query.eq("machine_id", machine_id)
    if status:
        query = query.eq("status", status)

    result = query.order("detected_at", desc=True).range(offset, offset + limit - 1).execute()
    return {"anomalies": result.data or []}


@router.get("/{anomaly_id}")
async def get_anomaly(
    anomaly_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_ANOMALIES)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Full anomaly detail."""
    result = (
        supabase.table("anomalies")
        .select("*")
        .eq("anomaly_id", anomaly_id)
        .eq("org_id", org.org_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return result.data


@router.patch("/{anomaly_id}/status")
async def update_anomaly_status(
    anomaly_id: str,
    body: AnomalyStatusUpdate,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MARK_ANOMALY_REVIEWED)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Update anomaly status and add notes."""
    if body.status not in ["new", "reviewed", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    data = {"status": body.status, "reviewed_by": org.user.id, "reviewed_at": "now()"}
    if body.notes is not None:
        data["notes"] = body.notes

    result = (
        supabase.table("anomalies")
        .update(data)
        .eq("anomaly_id", anomaly_id)
        .eq("org_id", org.org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return {"message": "Anomaly updated", "anomaly": result.data[0]}
