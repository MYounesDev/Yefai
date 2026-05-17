"""Tests for PUQ AI schema models — Phase 3B."""



from ai.puqai.schemas import (
    AnomalyDetail,
    AutoOrderRequest,
    CrisisScoreResponse,
    NotificationRequest,
    PurchaseOrderPayload,
    SparePartsCrisisPayload,
    WebhookLog,
    WebhookPayload,
)


class TestAnomalyDetail:
    def test_defaults(self):
        d = AnomalyDetail(image_id=1, score=0.85)
        assert d.image_id == 1
        assert d.score == 0.85
        assert d.wear_type == ""
        assert d.wear_value_um == 0.0
        assert d.set_id == 0


class TestWebhookPayload:
    def test_default_timestamp(self):
        p = WebhookPayload(event="test")
        assert p.event == "test"
        assert p.timestamp
        assert p.severity == "info"

    def test_with_anomaly(self):
        p = WebhookPayload(
            event="anomaly_detected",
            machine="MATWI-Tool-15mm",
            anomaly=AnomalyDetail(image_id=42, score=0.87, wear_type="flank", wear_value_um=120.5, set_id=5),
            image_url="https://example.com/img.jpg",
            severity="critical",
        )
        assert p.anomaly.score == 0.87
        assert p.anomaly.wear_value_um == 120.5


class TestSparePartsCrisisPayload:
    def test_defaults(self):
        p = SparePartsCrisisPayload(part_id=1, part_name="Tool Insert")
        assert p.event == "spare_parts_crisis"
        assert p.part_name == "Tool Insert"
        assert p.on_hand == 0
        assert p.crisis_score == 0.0
        assert p.risk_level == "none"

    def test_full_payload(self):
        p = SparePartsCrisisPayload(
            part_id=101,
            part_name="Bearing XYZ",
            on_hand=2,
            needed_by="2026-06-01",
            lead_time_days_p90=21,
            crisis_score=82.5,
            risk_level="crisis",
            alternative_suppliers=[{"supplier_id": "S02", "name": "AltTed A.S."}],
        )
        assert p.lead_time_days_p90 == 21
        assert len(p.alternative_suppliers) == 1


class TestPurchaseOrderPayload:
    def test_defaults(self):
        p = PurchaseOrderPayload()
        assert p.event == "purchase_order_created"
        assert p.status == "ready_for_review"


class TestWebhookLog:
    def test_basic(self):
        log = WebhookLog(
            event_type="anomaly",
            payload={"event": "test"},
            webhook_url="https://hook.example.com",
            status="sent",
        )
        assert log.status == "sent"
        assert log.attempt == 1
        assert log.error is None

    def test_with_error(self):
        log = WebhookLog(
            event_type="anomaly",
            payload={},
            webhook_url="https://hook.example.com",
            status="failed",
            attempt=3,
            error="HTTP 500",
        )
        assert log.attempt == 3
        assert log.error == "HTTP 500"


class TestNotificationRequest:
    def test_defaults(self):
        req = NotificationRequest(anomaly_id=42, score=0.87)
        assert req.anomaly_id == 42
        assert req.score == 0.87
        assert req.wear_type == ""
        assert req.machine == ""


class TestCrisisScoreResponse:
    def test_response(self):
        resp = CrisisScoreResponse(
            image_id=1, crisis_score=65.0, risk_level="at_risk", breakdown={}
        )
        assert resp.risk_level == "at_risk"


class TestAutoOrderRequest:
    def test_defaults(self):
        req = AutoOrderRequest(part_id=101)
        assert req.part_id == 101
        assert req.quantity == 1
        assert req.trigger == "crisis"
