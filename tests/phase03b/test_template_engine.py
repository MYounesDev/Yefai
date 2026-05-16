"""Tests for Jinja2 template rendering — Phase 3B."""

from pathlib import Path

import pytest

TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent.parent / "server" / "ai" / "puqai" / "templates"
)


@pytest.fixture
def template_engine():
    """Import template_engine lazily to avoid import order issues."""
    import sys

    sys.path.insert(0, str(TEMPLATE_DIR.parent.parent.parent))
    from ai.puqai import template_engine as te

    return te


class TestTelegramAnomalyTemplate:
    def test_render(self, template_engine):
        result = template_engine.render_telegram_anomaly(
            machine="MATWI-Tool-15mm",
            anomaly_id=42,
            score=0.87,
            wear_type="flank",
            wear_value_um=120.5,
            image_url="https://example.com/img.jpg",
        )
        assert "ANOMALI" in result
        assert "MATWI-Tool-15mm" in result
        assert "Flank" in result or "flank" in result  # Jinja2 |capitalize
        assert "120.5" in result


class TestEmailReportTemplate:
    def test_render(self, template_engine):
        result = template_engine.render_email_report(
            machine="MATWI-Tool-15mm",
            anomaly_id=42,
            score=0.87,
            wear_type="flank",
            wear_value_um=120.5,
            set_id=5,
            image_url="https://example.com/img.jpg",
            timestamp="2026-05-16T10:30:00Z",
        )
        assert "Yefai Anomali Raporu" in result
        assert "0.87" in result
        assert "10:30" in result


class TestSmsCriticalTemplate:
    def test_render(self, template_engine):
        result = template_engine.render_sms_critical(
            machine="MATWI-Tool-15mm",
            wear_type="flank",
            wear_value_um=120.5,
            set_id=5,
        )
        assert "ANOMALI" in result
        assert "MATWI" in result
        assert "120" in result  # rounded to 0 decimal
        assert len(result) < 160  # SMS limit


class TestCrisisPayloadTemplate:
    def test_render(self, template_engine):
        result = template_engine.render_crisis_payload(
            part_name="Bearing XYZ",
            on_hand=2,
            crisis_score=82.5,
            risk_level="crisis",
            lead_time_days=21,
            alt_suppliers="Alternatif Tedarikci A.S.",
        )
        assert "Yedek Parca Krizi" in result
        assert "Bearing" in result
        assert "82.5" in result


class TestPoNotificationTemplate:
    def test_render(self, template_engine):
        result = template_engine.render_po_payload(
            part_name="Bearing XYZ",
            supplier_name="Ana Tedarikci A.S.",
            quantity=5,
            unit_price=450.0,
            total=2250.0,
            po_id=1001,
        )
        assert "Satin Alma Siparisi" in result
        assert "Bearing" in result
        assert "2250" in result


class TestTemplateNotFound:
    def test_nonexistent_template(self, template_engine):
        """Should return empty string for missing template."""
        from ai.puqai.template_engine import render_template

        result = render_template("nonexistent.j2")
        assert result == ""
