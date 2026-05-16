import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from ai.puqai.schemas import WebhookLog

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_base: float = 1.0
    backoff_multiplier: float = 4.0

    def delay_for(self, attempt: int) -> float:
        return self.backoff_base * (self.backoff_multiplier ** (attempt - 1))


async def retry_webhook(
    callback,
    channel: str,
    payload: dict[str, Any],
    url: str,
    config: RetryConfig | None = None,
    log_callback=None,
) -> WebhookLog:
    cfg = config or RetryConfig()
    last_error: str | None = None

    for attempt in range(1, cfg.max_attempts + 1):
        try:
            result = await callback(url, payload, channel)
            if isinstance(result, WebhookLog):
                result.attempt = attempt
            if log_callback and result.status == "sent":
                await log_callback(result)
            return result
        except Exception as e:
            last_error = str(e)
            logger.info(
                "Webhook %s attempt %d/%d failed: %s",
                channel,
                attempt,
                cfg.max_attempts,
                e,
            )
            if attempt < cfg.max_attempts:
                delay = cfg.delay_for(attempt)
                await asyncio.sleep(delay)

    failed_log = WebhookLog(
        event_type=channel,
        payload=payload,
        webhook_url=url,
        status="failed",
        attempt=cfg.max_attempts,
        error=last_error,
    )
    if log_callback:
        await log_callback(failed_log)
    return failed_log


@dataclass
class RetryQueue:
    pending: list[WebhookLog] = field(default_factory=list)

    def enqueue(self, log: WebhookLog) -> None:
        if log.status == "failed":
            self.pending.append(log)

    async def process(self, callback) -> list[WebhookLog]:
        results: list[WebhookLog] = []
        for entry in list(self.pending):
            try:
                result = await callback(entry.webhook_url, entry.payload, entry.event_type)
                if result.status == "sent":
                    self.pending.remove(entry)
                results.append(result)
            except Exception as e:
                logger.warning("Retry queue reprocess failed: %s", e)
        return results
