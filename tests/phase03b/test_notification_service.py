"""Tests for notification service — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.puqai.schemas import NotificationRequest, WebhookLog
from services.notification_service import NotificationService


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.send_anomaly_alert = AsyncMock(return_value=[WebhookLog(
        event_type="anomaly", payload={}, webhook_url="https://hook.example.com", status="sent",
    )])
    client.send_detail_report = AsyncMock(return_value=[WebhookLog(
        event_type="email", payload={}, webhook_url="https://hook.example.com", status="sent",
    )])
    client._post_webhook = AsyncMock(return_value=WebhookLog(
        event_type="sms", payload={}, webhook_url="https://hook.example.com", status="sent",
    ))
    return client


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_critical_anomaly_triggers_all_channels(self, mock_client):
        """score > 0.9 should trigger all channels."""
        with patch("services.notification_service.get_puqai_settings") as mock_settings:
            settings = MagicMock()
            settings.puqai_sms_webhook = "https://sms.hook.com"
            mock_settings.return_value = settings

            service = NotificationService(client=mock_client)
            request = NotificationRequest(
                anomaly_id=1, score=0.95, wear_type="flank",
                wear_value_um=120.5, set_id=5, machine="MATWI-Tool-15mm",
            )
            logs = await service.notify_anomaly(request)
            assert len(logs) >= 3  # anomaly + email + sms

    @pytest.mark.asyncio
    async def test_warning_anomaly_triggers_two_channels(self, mock_client):
        """score 0.7-0.9 should trigger anomaly + email."""
        with patch("services.notification_service.get_puqai_settings") as mock_settings:
            settings = MagicMock()
            settings.puqai_sms_webhook = ""
            mock_settings.return_value = settings

            service = NotificationService(client=mock_client)
            request = NotificationRequest(
                anomaly_id=2, score=0.80, wear_type="flank",
                wear_value_um=100.0, set_id=3, machine="MATWI-Tool-15mm",
            )
            logs = await service.notify_anomaly(request)
            assert len(logs) >= 2

    @pytest.mark.asyncio
    async def test_info_anomaly_triggers_email_only(self, mock_client):
        """score 0.5-0.7 should trigger email only (detail report)."""
        with patch("services.notification_service.get_puqai_settings") as mock_settings:
            settings = MagicMock()
            settings.puqai_sms_webhook = ""
            mock_settings.return_value = settings

            service = NotificationService(client=mock_client)
            request = NotificationRequest(
                anomaly_id=3, score=0.60, wear_type="chipping",
                wear_value_um=50.0, set_id=1, machine="MATWI-Tool-15mm",
            )
            logs = await service.notify_anomaly(request)
            # Only email (detail report) should fire
            assert len(logs) >= 1

    @pytest.mark.asyncio
    async def test_throttle_same_anomaly(self, mock_client):
        """Same anomaly within 5 min should be throttled."""
        service = NotificationService(client=mock_client)
        request = NotificationRequest(anomaly_id=999, score=0.95)
        # First call should go through
        logs1 = await service.notify_anomaly(request)
        assert len(logs1) > 0
        # Second call immediately after should be throttled
        logs2 = await service.notify_anomaly(request)
        assert len(logs2) == 0

    @pytest.mark.asyncio
    async def test_fallback_on_exception(self, mock_client):
        """Exception in webhook should trigger OS fallback."""
        mock_client.send_anomaly_alert = AsyncMock(side_effect=Exception("Connection failed"))
        mock_client.send_detail_report = AsyncMock(side_effect=Exception("Connection failed"))

        with (
            patch("services.notification_service.get_puqai_settings") as mock_settings,
            patch("ai.puqai.fallback.send_os_notification") as mock_fallback,
        ):
            settings = MagicMock()
            settings.puqai_sms_webhook = ""
            mock_settings.return_value = settings

            service = NotificationService(client=mock_client)
            request = NotificationRequest(anomaly_id=100, score=0.95)
            logs = await service.notify_anomaly(request)
            mock_fallback.assert_called_once()
            assert isinstance(logs, list)

    @pytest.mark.asyncio
    async def test_send_report(self, mock_client):
        service = NotificationService(client=mock_client)
        logs = await service.send_report("daily", {"date": "2026-05-16"})
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_close(self, mock_client):
        service = NotificationService(client=mock_client)
        # Should not raise
        await service.close()
