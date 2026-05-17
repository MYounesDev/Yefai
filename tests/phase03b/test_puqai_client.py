"""Tests for PUQ AI webhook client — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

from unittest.mock import AsyncMock, patch

import pytest

from ai.puqai.client import PuqAIWebhookClient
from ai.puqai.schemas import NotificationRequest, PurchaseOrderPayload, SparePartsCrisisPayload


@pytest.fixture
def client():
    return PuqAIWebhookClient()


class TestPuqAIWebhookClient:
    @pytest.mark.asyncio
    async def test_severity_from_score(self):
        assert PuqAIWebhookClient._severity_from_score(0.95) == "critical"
        assert PuqAIWebhookClient._severity_from_score(0.80) == "warning"
        assert PuqAIWebhookClient._severity_from_score(0.60) == "info"
        assert PuqAIWebhookClient._severity_from_score(0.30) == "low"

    @pytest.mark.asyncio
    async def test_anomaly_alert(self):
        with patch.object(PuqAIWebhookClient, "_dispatch", new=AsyncMock()) as mock:
            mock.return_value = []
            c = PuqAIWebhookClient()
            req = NotificationRequest(anomaly_id=42, score=0.87)
            result = await c.send_anomaly_alert(req)
            mock.assert_called_once()
            assert result == []

    @pytest.mark.asyncio
    async def test_crisis_alert(self):
        with patch.object(PuqAIWebhookClient, "_dispatch", new=AsyncMock()) as mock:
            mock.return_value = []
            c = PuqAIWebhookClient()
            crisis = SparePartsCrisisPayload(part_id=1, part_name="Test Part")
            result = await c.send_crisis_alert(crisis)
            mock.assert_called_once()
            assert result == []

    @pytest.mark.asyncio
    async def test_po_notification(self):
        with patch.object(PuqAIWebhookClient, "_dispatch", new=AsyncMock()) as mock:
            mock.return_value = []
            c = PuqAIWebhookClient()
            po = PurchaseOrderPayload(po_id=1001, part_name="Test Part")
            result = await c.send_po_notification(po)
            mock.assert_called_once()
            assert result == []

    @pytest.mark.asyncio
    async def test_dispatch_skipped_when_no_url(self):
        c = PuqAIWebhookClient()
        with patch.object(c, "_settings") as mock_settings:
            mock_settings.webhook_map = {"anomaly": ""}
            logs = await c._dispatch("anomaly", {"event": "test"})
            assert len(logs) == 1
            assert logs[0].status == "skipped"

    @pytest.mark.asyncio
    async def test_close(self):
        c = PuqAIWebhookClient()
        mock_http = AsyncMock()
        c._client = mock_http
        await c.close()
        assert c._client is None
        mock_http.aclose.assert_awaited_once()
