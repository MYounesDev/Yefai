"""Notifications router — logs, manual triggers, and channel CRUD."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from supabase import Client

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# ── Request Models ─────────────────────────────────────────────


class ChannelCreateRequest(BaseModel):
    channel_type: str
    config: dict[str, Any]
    is_enabled: bool = True


class ChannelUpdateRequest(BaseModel):
    config: dict[str, Any] | None = None
    is_enabled: bool | None = None


class TestNotificationRequest(BaseModel):
    channel_id: str


# ── Dependency ─────────────────────────────────────────────────


def _get_notification_service(supabase: Client = Depends(get_supabase_client)) -> NotificationService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return NotificationService(supabase)


# ── Logs ───────────────────────────────────────────────────────


@router.get("/logs")
async def get_logs(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_NOTIFICATIONS)),
    event_type: str | None = None,
    limit: int = Query(50, le=100),
    page: int = Query(1, ge=1),
    service: NotificationService = Depends(_get_notification_service),
) -> dict[str, Any]:
    """Get paginated notification logs."""
    return await service.get_notification_logs(org.org_id, event_type, page, limit)


# ── Triggers ───────────────────────────────────────────────────


@router.post("/trigger/anomaly/{anomaly_id}")
async def trigger_anomaly_alert(
    anomaly_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.TRIGGER_NOTIFICATION)),
    service: NotificationService = Depends(_get_notification_service),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Manually trigger an anomaly alert (Manager only)."""
    # Fetch anomaly
    anomaly_res = (
        supabase.table("anomalies")
        .select("*")
        .eq("anomaly_id", anomaly_id)
        .eq("org_id", org.org_id)
        .maybe_single()
        .execute()
    )
    if not anomaly_res.data:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    logs = await service.send_anomaly_alert(org.org_id, anomaly_res.data)
    return {"message": "Anomaly alert dispatched", "logs": logs}


@router.post("/trigger/test")
async def trigger_test_notification(
    body: TestNotificationRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    service: NotificationService = Depends(_get_notification_service),
) -> dict[str, Any]:
    """Send a test notification to a specific channel (Manager only)."""
    try:
        log = await service.send_test_notification(org.org_id, body.channel_id)
        return {"message": "Test notification dispatched", "log": log}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ── Channels ───────────────────────────────────────────────────


@router.get("/channels")
async def list_channels(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """List configured notification channels (Manager only)."""
    result = supabase.table("notification_channels").select("*").eq("org_id", org.org_id).execute()
    return {"channels": result.data or []}


@router.post("/channels", status_code=status.HTTP_201_CREATED)
async def create_channel(
    body: ChannelCreateRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Add a new notification channel (Manager only)."""
    data = {
        "org_id": org.org_id,
        "channel_type": body.channel_type,
        "config": body.config,
        "is_enabled": body.is_enabled
    }
    result = supabase.table("notification_channels").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create channel")
    return {"message": "Channel created", "channel": result.data[0]}


@router.patch("/channels/{channel_id}")
async def update_channel(
    channel_id: str,
    body: ChannelUpdateRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Update a notification channel (Manager only)."""
    data = {}
    if body.config is not None:
        data["config"] = body.config
    if body.is_enabled is not None:
        data["is_enabled"] = body.is_enabled

    if not data:
        raise HTTPException(status_code=400, detail="No updates provided")

    result = (
        supabase.table("notification_channels")
        .update(data)
        .eq("id", channel_id)
        .eq("org_id", org.org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"message": "Channel updated", "channel": result.data[0]}


@router.delete("/channels/{channel_id}")
async def delete_channel(
    channel_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    supabase: Client = Depends(get_supabase_client),
) -> dict[str, Any]:
    """Delete a notification channel (Manager only)."""
    result = (
        supabase.table("notification_channels")
        .delete()
        .eq("id", channel_id)
        .eq("org_id", org.org_id)
        .execute()
    )
    # the client might return an empty list or None on delete
    # but normally returns the deleted row if we requested it.
    return {"message": "Channel deleted"}
