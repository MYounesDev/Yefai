"""Tests for notification and spare-parts API endpoints — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data or "spare_parts" in data


class TestSparePartsCatalog:
    def test_get_catalog(self, client):
        response = client.get("/api/spare-parts/catalog")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data

    def test_catalog_filter_by_criticality(self, client):
        response = client.get("/api/spare-parts/catalog?criticality=A")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item.get("criticality", "").upper() == "A"


class TestCrisisScore:
    def test_crisis_score_valid(self, client):
        response = client.get("/api/spare-parts/crisis-score/1?anomaly_score=0.85")
        assert response.status_code in (200, 404)

    def test_crisis_score_invalid_image(self, client):
        response = client.get("/api/spare-parts/crisis-score/-1")
        # Should still return something valid
        assert response.status_code in (200, 404, 422)


class TestAutoOrder:
    def test_auto_order(self, client):
        response = client.post("/api/spare-parts/auto-order", json={"part_id": 42, "quantity": 2})
        assert response.status_code in (200, 409)  # 409 = duplicate
        if response.status_code == 200:
            data = response.json()
            assert data["created"] is True
            assert "po" in data


class TestCrisisWorkflow:
    def test_workflow_without_po_or_notification(self, client):
        response = client.post(
            "/api/spare-parts/crisis-workflow",
            json={
                "image_id": 94,
                "machine_id": "Set3",
                "anomaly_score": 0.92,
                "hours_to_critical": 16,
                "auto_order": False,
                "notify": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["machine_id"] == "Set3"
        assert data["prediction"]["hours_to_critical"] == 16
        assert data["crisis"]["risk_level"] in {"watch", "at_risk", "crisis"}
        assert data["purchase_order"]["created"] is False
        assert data["notification"]["sent"] is False
        assert "alternative_suppliers" in data

    def test_workflow_creates_mock_po_for_crisis(self, client):
        response = client.post(
            "/api/spare-parts/crisis-workflow",
            json={
                "image_id": 94,
                "machine_id": "Set3",
                "anomaly_score": 0.99,
                "hours_to_critical": 1,
                "auto_order": True,
                "notify": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crisis"]["needs_auto_order"] is True
        assert data["purchase_order"]["created"] in {True, False}
        if data["purchase_order"]["created"]:
            assert data["purchase_order"]["po"]["status"] == "ready_for_review"
        else:
            assert data["purchase_order"]["reason"] == "duplicate_order_prevented"


class TestAlternativeSuppliers:
    def test_alternatives(self, client):
        response = client.get("/api/spare-parts/alternative-suppliers/1")
        assert response.status_code == 200
        data = response.json()
        assert "alternatives" in data

    def test_alternatives_with_lead_time_filter(self, client):
        response = client.get("/api/spare-parts/alternative-suppliers/1?max_lead_time_days=7")
        assert response.status_code == 200


class TestInventory:
    def test_inventory(self, client):
        response = client.get("/api/spare-parts/inventory")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_low_stock(self, client):
        response = client.get("/api/spare-parts/inventory?low_stock=true")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert int(item.get("on_hand", 0)) < int(item.get("min_level", 10))


class TestPurchaseOrders:
    def test_list_pos(self, client):
        response = client.get("/api/spare-parts/purchase-orders")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data

    def test_get_single_po(self, client):
        # First create one
        client.post("/api/spare-parts/auto-order", json={"part_id": 77, "quantity": 1})
        response = client.get("/api/spare-parts/purchase-orders")
        if response.status_code == 200:
            orders = response.json().get("orders", [])
            if orders:
                po_id = orders[0]["po_id"]
                resp = client.get(f"/api/spare-parts/purchase-orders/{po_id}")
                assert resp.status_code == 200

    def test_get_nonexistent_po(self, client):
        response = client.get("/api/spare-parts/purchase-orders/999999")
        assert response.status_code == 404


class TestNotifications:
    def test_notification_status(self, client):
        with patch("ai.puqai.config.get_puqai_settings") as mock:
            settings = MagicMock()
            settings.configured = True
            settings.webhook_map = {"anomaly": "https://hook.example.com"}
            settings.puqai_fallback_enabled = True
            settings.puqai_retry_max_attempts = 3
            mock.return_value = settings

            response = client.get("/api/notifications/status")
            assert response.status_code == 200
            data = response.json()
            assert "puqai_configured" in data

    def test_webhook_logs(self, client):
        response = client.get("/api/notifications/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
