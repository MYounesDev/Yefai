"""Notification Service — multi-channel dispatch, logging, and PUQ AI integration."""

import logging
from typing import Any

from supabase import Client

logger = logging.getLogger(__name__)


class PUQAIClient:
    """Mock PUQ AI client — logs notifications, returns success."""

    async def send(self, channel_type: str, payload: dict) -> dict[str, Any]:
        logger.info(f"[MOCK PUQ AI] {channel_type}: {payload}")
        return {"status": "sent", "mock": True}


class NotificationService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.puq_client = PUQAIClient()

    async def send_anomaly_alert(self, org_id: str, anomaly_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Send anomaly alert through all enabled channels for the org."""
        return await self._dispatch(org_id, "anomaly_detected", anomaly_data)

    async def send_crisis_alert(self, org_id: str, crisis_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Send crisis/spare parts alert."""
        return await self._dispatch(org_id, "crisis_alert", crisis_data)

    async def send_test_notification(self, org_id: str, channel_id: str) -> dict[str, Any]:
        """Send test notification to verify channel config."""
        channel_res = (
            self.supabase.table("notification_channels")
            .select("*")
            .eq("id", channel_id)
            .eq("org_id", org_id)
            .maybe_single()
            .execute()
        )
        if not channel_res.data:
            raise ValueError("Channel not found")

        channel = channel_res.data
        result = await self.puq_client.send(channel["channel_type"], {"message": "Test Notification"})

        # Log
        log_data = {
            "org_id": org_id,
            "channel_type": channel["channel_type"],
            "event_type": "test",
            "payload": {"message": "Test Notification"},
            "status": result["status"],
            "sent_at": "now()" if result["status"] == "sent" else None
        }
        log_res = self.supabase.table("notification_logs").insert(log_data).execute()
        
        if not log_res.data:
            raise ValueError("Failed to create log entry")

        return log_res.data[0]

    async def _dispatch(self, org_id: str, event_type: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Core dispatch logic: fetches channels, sends via PUQ AI, and logs."""
        channels_res = (
            self.supabase.table("notification_channels")
            .select("*")
            .eq("org_id", org_id)
            .eq("is_enabled", True)
            .execute()
        )
        channels = channels_res.data or []

        logs = []
        for channel in channels:
            status = "failed"
            error = None
            try:
                # Merge channel config with payload so PUQ AI knows destination
                full_payload = {**payload, "config": channel["config"]}
                res = await self.puq_client.send(channel["channel_type"], full_payload)
                status = res["status"]
            except Exception as e:
                error = str(e)
                logger.error(f"Failed to send notification via {channel['channel_type']}: {error}")

            log_data = {
                "org_id": org_id,
                "channel_type": channel["channel_type"],
                "event_type": event_type,
                "payload": payload,
                "status": status,
                "error_message": error,
                "sent_at": "now()" if status == "sent" else None
            }
            log_res = self.supabase.table("notification_logs").insert(log_data).execute()
            if log_res.data:
                logs.append(log_res.data[0])

        return logs

    async def get_notification_logs(
        self, org_id: str, event_type: str | None = None, page: int = 1, limit: int = 50
    ) -> dict[str, Any]:
        """Paginated notification logs for an org."""
        offset = (page - 1) * limit
        query = self.supabase.table("notification_logs").select("*").eq("org_id", org_id)
        if event_type:
            query = query.eq("event_type", event_type)

        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return {"logs": result.data or []}
