"""Notification Service — multi-channel dispatch, logging, and PUQ AI integration."""

import logging
from datetime import datetime
from typing import Any

from supabase import Client

from ai.puqai.client import PuqAIWebhookClient
from ai.puqai.config import get_puqai_settings
from ai.puqai.schemas import (
    NotificationRequest,
    PurchaseOrderPayload,
    SparePartsCrisisPayload,
    WebhookLog,
)

logger = logging.getLogger(__name__)


class PUQAIClient:
    """Mock PUQ AI client — logs notifications, returns success."""

    async def send(self, channel_type: str, payload: dict) -> dict[str, Any]:
        logger.info(f"[MOCK PUQ AI] {channel_type}: {payload}")
        return {"status": "sent", "mock": True}


class NotificationService:
    def __init__(
        self, supabase: Client | None = None, client: PuqAIWebhookClient | None = None
    ) -> None:
        # Main file initialization priorities
        self._client = client or PuqAIWebhookClient()
        self._settings = get_puqai_settings()
        self._last_sent: dict[int, float] = {}

        # ABC file initialization
        self.supabase = supabase
        self.puq_client = PUQAIClient()

    # ==========================================
    # MAIN FILE LOGIC (Priority)
    # ==========================================

    async def notify_anomaly(self, request: NotificationRequest) -> list[WebhookLog]:
        if self._should_throttle(request.anomaly_id):
            logger.info("Throttled notification for anomaly_id=%d", request.anomaly_id)
            return []

        score = request.score
        logs: list[WebhookLog] = []

        try:
            if score > 0.9:
                logs += await self._client.send_anomaly_alert(request)
                logs += await self._client.send_detail_report(request)
                if self._settings.puqai_sms_webhook:
                    sms_payload = {
                        "event": "critical_alert",
                        "timestamp": datetime.utcnow().isoformat(),
                        "machine": request.machine,
                        "anomaly": {
                            "image_id": request.anomaly_id,
                            "score": score,
                            "wear_type": request.wear_type,
                            "wear_value_um": request.wear_value_um,
                            "set_id": request.set_id,
                        },
                        "severity": "critical",
                    }
                    result = await self._client._post_webhook(
                        self._settings.puqai_sms_webhook, sms_payload, "sms"
                    )
                    logs.append(result)
            elif score > 0.7:
                logs += await self._client.send_anomaly_alert(request)
                logs += await self._client.send_detail_report(request)
            elif score > 0.5:
                logs += await self._client.send_detail_report(request)
        except Exception:
            logger.exception("Notification dispatch failed for anomaly_id=%d", request.anomaly_id)
            from ai.puqai.fallback import send_os_notification

            send_os_notification(
                f"Yefai Anomaly: score={score} type={request.wear_type} id={request.anomaly_id}"
            )

        self._last_sent[request.anomaly_id] = datetime.utcnow().timestamp()
        return logs

    def _should_throttle(self, anomaly_id: int) -> bool:
        last = self._last_sent.get(anomaly_id)
        if last is None:
            return False
        return (datetime.utcnow().timestamp() - last) < 300

    async def send_report(self, report_type: str, parameters: dict) -> list[WebhookLog]:
        payload = {
            "event": "report",
            "timestamp": datetime.utcnow().isoformat(),
            "report_type": report_type,
            "parameters": parameters,
        }
        return [
            await self._client._post_webhook(self._settings.puqai_email_webhook, payload, "email")
        ]

    async def send_spare_parts_crisis(
        self,
        crisis: SparePartsCrisisPayload,
        po: PurchaseOrderPayload | None = None,
    ) -> list[WebhookLog]:
        logs = await self._client.send_crisis_alert(crisis)
        if po is not None:
            logs += await self._client.send_po_notification(po)
        return logs

    async def close(self) -> None:
        await self._client.close()

    # ==========================================
    # ABC FILE LOGIC (Secondary Dispatch/Supabase)
    # ==========================================

    async def send_anomaly_alert(
        self, org_id: str, anomaly_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Send anomaly alert through all enabled channels for the org."""
        return await self._dispatch(org_id, "anomaly_detected", anomaly_data)

    async def send_crisis_alert(
        self, org_id: str, crisis_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Send crisis/spare parts alert."""
        return await self._dispatch(org_id, "crisis_alert", crisis_data)

    async def send_test_notification(self, org_id: str, channel_id: str) -> dict[str, Any]:
        """Send test notification to verify channel config."""
        if not self.supabase:
            raise ValueError("Supabase client is not initialized.")

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
        result = await self.puq_client.send(
            channel["channel_type"], {"message": "Test Notification"}
        )

        # Log
        log_data = {
            "org_id": org_id,
            "channel_type": channel["channel_type"],
            "event_type": "test",
            "payload": {"message": "Test Notification"},
            "status": result["status"],
            "sent_at": "now()" if result["status"] == "sent" else None,
        }
        log_res = self.supabase.table("notification_logs").insert(log_data).execute()

        if not log_res.data:
            raise ValueError("Failed to create log entry")

        return log_res.data[0]

    async def _dispatch(
        self, org_id: str, event_type: str, payload: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Core dispatch logic: fetches channels, sends via PUQ AI, and logs."""
        if not self.supabase:
            logger.warning("Supabase client not available for _dispatch.")
            return []

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
                "sent_at": "now()" if status == "sent" else None,
            }
            log_res = self.supabase.table("notification_logs").insert(log_data).execute()
            if log_res.data:
                logs.append(log_res.data[0])

        return logs

    async def get_notification_logs(
        self, org_id: str, event_type: str | None = None, page: int = 1, limit: int = 50
    ) -> dict[str, Any]:
        """Paginated notification logs for an org."""
        if not self.supabase:
            return {"logs": []}

        offset = (page - 1) * limit
        query = self.supabase.table("notification_logs").select("*").eq("org_id", org_id)
        if event_type:
            query = query.eq("event_type", event_type)

        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return {"logs": result.data or []}
