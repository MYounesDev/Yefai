import logging
from typing import Any

import httpx

from ai.puqai.config import get_puqai_settings
from ai.puqai.schemas import (
    NotificationRequest,
    PurchaseOrderPayload,
    SparePartsCrisisPayload,
    WebhookLog,
    WebhookPayload,
)

logger = logging.getLogger(__name__)


class PuqAIWebhookClient:
    def __init__(self) -> None:
        self._settings = get_puqai_settings()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._settings.puqai_request_timeout)
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _post_webhook(
        self,
        url: str,
        payload: dict[str, Any],
        event_type: str,
    ) -> WebhookLog:
        client = await self._get_client()
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return WebhookLog(
                event_type=event_type,
                payload=payload,
                webhook_url=url,
                status="sent",
                attempt=1,
            )
        except httpx.HTTPStatusError as e:
            logger.warning("Webhook %s failed (HTTP %s): %s", event_type, e.response.status_code, e)
            return WebhookLog(
                event_type=event_type,
                payload=payload,
                webhook_url=url,
                status="failed",
                attempt=1,
                error=f"HTTP {e.response.status_code}",
            )
        except Exception as e:
            logger.warning("Webhook %s failed: %s", event_type, e)
            return WebhookLog(
                event_type=event_type,
                payload=payload,
                webhook_url=url,
                status="failed",
                attempt=1,
                error=str(e),
            )

    async def send_anomaly_alert(self, request: NotificationRequest) -> list[WebhookLog]:
        payload = WebhookPayload(
            event="anomaly_detected",
            machine=request.machine,
            anomaly={
                "image_id": request.anomaly_id,
                "score": request.score,
                "wear_type": request.wear_type,
                "wear_value_um": request.wear_value_um,
                "set_id": request.set_id,
            },
            image_url=request.image_url,
            severity=self._severity_from_score(request.score),
            message=request.message,
        )
        return await self._dispatch("anomaly", payload.model_dump())

    async def send_detail_report(self, request: NotificationRequest) -> list[WebhookLog]:
        payload = WebhookPayload(
            event="detail_report",
            machine=request.machine,
            anomaly={
                "image_id": request.anomaly_id,
                "score": request.score,
                "wear_type": request.wear_type,
                "wear_value_um": request.wear_value_um,
                "set_id": request.set_id,
            },
            image_url=request.image_url,
            severity=self._severity_from_score(request.score),
            message=request.message,
        )
        return await self._dispatch("email", payload.model_dump())

    async def send_crisis_alert(self, crisis: SparePartsCrisisPayload) -> list[WebhookLog]:
        return await self._dispatch("spare_parts", crisis.model_dump())

    async def send_po_notification(self, po: PurchaseOrderPayload) -> list[WebhookLog]:
        return await self._dispatch("po", po.model_dump())

    async def _dispatch(
        self,
        channel: str,
        payload: dict[str, Any],
    ) -> list[WebhookLog]:
        url = self._settings.webhook_map.get(channel, "")
        if not url:
            logger.info("No webhook URL configured for channel=%s — skipping", channel)
            return [
                WebhookLog(
                    event_type=channel,
                    payload=payload,
                    webhook_url="",
                    status="skipped",
                )
            ]
        log = await self._post_webhook(url, payload, channel)
        return [log]

    @staticmethod
    def _severity_from_score(score: float) -> str:
        if score > 0.9:
            return "critical"
        if score > 0.7:
            return "warning"
        if score > 0.5:
            return "info"
        return "low"
