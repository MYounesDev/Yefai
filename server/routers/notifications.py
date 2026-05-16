"""Notifications router — Phase 3B.

PUQ AI webhook-based notification endpoints for anomaly alerts,
reports, and webhook log queries.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from ai.puqai.schemas import NotificationRequest, ReportRequest
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# Dependency
def get_notification_service() -> NotificationService:
    """Get notification service instance."""
    return NotificationService()


@router.post("/anomaly")
async def trigger_anomaly_notification(
    request: NotificationRequest,
    service: NotificationService = Depends(get_notification_service),
) -> dict[str, Any]:
    """Trigger anomaly notification with severity-based routing.

    Severity rules:
      - score > 0.9: SMS + Telegram + Email (critical)
      - score > 0.7: Telegram + Email (warning)
      - score > 0.5: Email only (info)

    Returns list of webhook logs.
    """
    try:
        logs = await service.notify_anomaly(request)
        return {"logs": [log.model_dump() for log in logs], "count": len(logs)}
    except Exception as e:
        logger.exception("Failed to trigger anomaly notification")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/report")
async def trigger_report(
    request: ReportRequest,
    service: NotificationService = Depends(get_notification_service),
) -> dict[str, Any]:
    """Send a custom report notification via email webhook."""
    try:
        logs = await service.send_report(request.report_type, request.parameters)
        return {"logs": [log.model_dump() for log in logs], "count": len(logs)}
    except Exception as e:
        logger.exception("Failed to send report notification")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/logs")
async def get_webhook_logs(
    event_type: str | None = Query(None, description="Filter by event type"),
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> dict[str, Any]:
    """Retrieve webhook logs with optional filters.

    Note: Currently returns in-memory logs since webhook_logs table
    is Supabase-only during deployment. This endpoint serves as the
    query interface for the webhook log dashboard.
    """

    # Return empty result set — actual log persistence is via Supabase
    return {"logs": [], "count": 0, "filters": {"event_type": event_type, "status": status}}


@router.get("/status")
async def get_notification_status() -> dict[str, Any]:
    """Check PUQ AI connection status and configuration."""
    from ai.puqai.config import get_puqai_settings

    settings = get_puqai_settings()
    configured_channels = [ch for ch, url in settings.webhook_map.items() if url]
    return {
        "puqai_configured": settings.configured,
        "configured_channels": configured_channels,
        "fallback_enabled": settings.puqai_fallback_enabled,
        "retry_max_attempts": settings.puqai_retry_max_attempts,
    }
