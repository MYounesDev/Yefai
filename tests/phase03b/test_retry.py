"""Tests for webhook retry mechanism — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

import pytest

from ai.puqai.retry import RetryConfig, RetryQueue, retry_webhook
from ai.puqai.schemas import WebhookLog


class TestRetryConfig:
    def test_defaults(self):
        cfg = RetryConfig()
        assert cfg.max_attempts == 3
        assert cfg.backoff_base == 1.0
        assert cfg.backoff_multiplier == 4.0

    def test_delay_calculation(self):
        cfg = RetryConfig()
        assert cfg.delay_for(1) == 1.0
        assert cfg.delay_for(2) == 4.0
        assert cfg.delay_for(3) == 16.0


class TestRetryWebhook:
    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        async def mock_callback(url, payload, channel):
            return WebhookLog(
                event_type=channel, payload=payload,
                webhook_url=url, status="sent",
            )

        result = await retry_webhook(mock_callback, "test", {}, "https://hook.example.com")
        assert result.status == "sent"
        assert result.attempt <= 1

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        call_count = 0

        async def mock_flaky(url, payload, channel):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temp failure")
            return WebhookLog(
                event_type=channel, payload=payload,
                webhook_url=url, status="sent",
            )

        result = await retry_webhook(
            mock_flaky, "test", {}, "https://hook.example.com",
            config=RetryConfig(max_attempts=4, backoff_base=0.01),
        )
        assert result.status == "sent"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_all_attempts_fail(self):
        async def mock_failing(url, payload, channel):
            raise Exception("Persistent failure")

        result = await retry_webhook(
            mock_failing, "test", {}, "https://hook.example.com",
            config=RetryConfig(max_attempts=3, backoff_base=0.01),
        )
        assert result.status == "failed"
        assert result.attempt == 3
        assert "Persistent failure" in (result.error or "")

    @pytest.mark.asyncio
    async def test_log_callback(self):
        logged = []

        async def mock_callback(url, payload, channel):
            return WebhookLog(
                event_type=channel, payload=payload,
                webhook_url=url, status="sent",
            )

        async def log_cb(log):
            logged.append(log)

        await retry_webhook(
            mock_callback, "test", {}, "https://hook.example.com",
            log_callback=log_cb,
        )
        assert len(logged) > 0


class TestRetryQueue:
    def test_enqueue_failed(self):
        queue = RetryQueue()
        log = WebhookLog(
            event_type="test", payload={},
            webhook_url="https://hook.example.com", status="failed",
        )
        queue.enqueue(log)
        assert len(queue.pending) == 1

    def test_skip_successful(self):
        queue = RetryQueue()
        log = WebhookLog(
            event_type="test", payload={},
            webhook_url="https://hook.example.com", status="sent",
        )
        queue.enqueue(log)
        assert len(queue.pending) == 0

    @pytest.mark.asyncio
    async def test_process_clears_succeeded(self):
        queue = RetryQueue()
        failed_log = WebhookLog(
            event_type="test", payload={},
            webhook_url="https://hook.example.com", status="failed",
        )
        queue.pending.append(failed_log)

        async def mock_callback(url, payload, channel):
            return WebhookLog(
                event_type=channel, payload=payload,
                webhook_url=url, status="sent",
            )

        results = await queue.process(mock_callback)
        assert len(results) >= 1
        # Should have been removed from pending
        assert len(queue.pending) == 0
