"""Tests for crisis score calculation — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

import pytest

from services.crisis_service import CrisisResult, calculate_crisis_score


class TestCrisisScoreCalculation:
    def test_score_range(self):
        """Crisis score should always be between 0 and 100."""
        for score in [0.1, 0.5, 0.7, 0.95]:
            result = calculate_crisis_score(image_id=1, anomaly_score=score)
            assert 0 <= result.crisis_score <= 100

    def test_higher_anomaly_higher_score(self):
        """Higher anomaly score should produce higher or equal crisis score."""
        score_low = calculate_crisis_score(image_id=1, anomaly_score=0.3)
        score_high = calculate_crisis_score(image_id=1, anomaly_score=0.9)
        assert score_high.crisis_score >= score_low.crisis_score

    def test_risk_level_mapping(self):
        """Verify risk level thresholds."""
        # Low anomaly should yield none or watch
        result = calculate_crisis_score(image_id=999, anomaly_score=0.05)
        assert result.risk_level in ("none", "watch")

    def test_breakdown_structure(self):
        result = calculate_crisis_score(image_id=5, anomaly_score=0.8)
        if result.breakdown:
            expected_keys = {
                "stock_gap_pct", "on_hand", "min_level",
                "lead_time_p90_days", "criticality",
                "supplier_reliability", "anomaly_score",
                "contributions",
            }
            assert expected_keys.issubset(result.breakdown.keys())
            contrib = result.breakdown["contributions"]
            assert "stock_gap" in contrib
            assert "lead_time" in contrib
            assert "criticality" in contrib
            assert "supplier_risk" in contrib
            assert "anomaly" in contrib

    def test_needs_auto_order(self):
        """at_risk and crisis should trigger auto-order need."""
        # Mock a high-anomaly scenario to force crisis
        result = CrisisResult(
            image_id=1, part_id=101, part_name="Test Part",
            crisis_score=75.0, risk_level="crisis",
            breakdown={},
        )
        assert result.needs_auto_order is True

        result.risk_level = "at_risk"
        assert result.needs_auto_order is True

        result.risk_level = "watch"
        assert result.needs_auto_order is False

        result.risk_level = "none"
        assert result.needs_auto_order is False

    def test_multiple_images(self):
        """Multiple image IDs should produce diverse results."""
        scores = set()
        for image_id in range(1, 20):
            result = calculate_crisis_score(image_id=image_id, anomaly_score=0.7)
            scores.add(result.crisis_score)
        # At least some should vary (parts are mapped by modulo)
        assert len(scores) > 1
