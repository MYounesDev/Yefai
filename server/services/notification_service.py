import logging
from datetime import datetime

from ai.puqai.client import PuqAIWebhookClient
from ai.puqai.config import get_puqai_settings
from ai.puqai.schemas import NotificationRequest, WebhookLog

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, client: PuqAIWebhookClient | None = None) -> None:
        self._client = client or PuqAIWebhookClient()
        self._settings = get_puqai_settings()
        self._last_sent: dict[int, float] = {}

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

    async def close(self) -> None:
        await self._client.close()
