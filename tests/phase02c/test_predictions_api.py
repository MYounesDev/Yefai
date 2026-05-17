"""Tests for predictions API endpoints and wear prediction pipeline."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

import numpy as np
import pytest


class TestCalibration:
    def test_linear_calibration(self):
        from ai.prediction.calibration import calibrate_score_to_wear

        assert calibrate_score_to_wear(0.0) == 0.0
        assert calibrate_score_to_wear(0.5) == 100.0
        assert calibrate_score_to_wear(1.0) == 200.0
        assert calibrate_score_to_wear(0.75) == 150.0

    def test_linear_calibration_negative_clamped(self):
        from ai.prediction.calibration import calibrate_score_to_wear

        assert calibrate_score_to_wear(-0.1) == 0.0

    def test_calibrator_fit_linear(self):
        from ai.prediction.calibration import WearCalibrator

        scores = np.array([0.0, 0.5, 1.0])
        actual = np.array([0.0, 100.0, 200.0])
        cal = WearCalibrator().fit(scores, actual)
        assert cal.linear_scale == pytest.approx(200.0)

    def test_calibrator_evaluate(self):
        from ai.prediction.calibration import WearCalibrator

        scores = np.array([0.0, 0.5, 1.0])
        actual = np.array([5.0, 105.0, 205.0])
        cal = WearCalibrator().fit(scores, actual)
        metrics = cal.evaluate(scores, actual)
        assert metrics["mae"] < 10.0
        assert metrics["rmse"] < 10.0


class TestWearRate:
    def test_linear_increasing(self):
        from ai.prediction.wear_rate import WearRateCalculator

        calc = WearRateCalculator(min_data_points=3)
        now = datetime(2026, 1, 1, 0, 0)
        timestamps = [now + timedelta(hours=i * 10) for i in range(5)]
        wear = np.array([0.0, 30.0, 60.0, 90.0, 120.0])

        result = calc.calculate(timestamps, wear)
        assert result["wear_rate_um_per_hour"] == pytest.approx(3.0, rel=0.01)
        assert result["r_squared"] == pytest.approx(1.0, rel=0.01)
        assert result["data_points"] == 5

    def test_insufficient_data(self):
        from ai.prediction.wear_rate import WearRateCalculator

        calc = WearRateCalculator(min_data_points=3)
        now = datetime(2026, 1, 1)
        timestamps = [now, now + timedelta(hours=1)]
        wear = np.array([0.0, 10.0])

        with pytest.raises(ValueError, match="Insufficient data"):
            calc.calculate(timestamps, wear)

    def test_confidence_levels(self):
        from ai.prediction.wear_rate import WearRateCalculator

        calc = WearRateCalculator(min_data_points=3)
        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(5)]
        wear = np.array([0.0, 30.0, 60.0, 90.0, 120.0])

        result = calc.calculate_with_confidence(timestamps, wear)
        assert result["confidence"] == "high"

    def test_noisy_data_medium_confidence(self):
        from ai.prediction.wear_rate import WearRateCalculator

        calc = WearRateCalculator(min_data_points=3)
        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(4)]
        wear = np.array([0.0, 25.0, 65.0, 85.0])  # not perfectly linear

        result = calc.calculate_with_confidence(timestamps, wear)
        assert result["confidence"] in ("medium", "high")


class TestProjection:
    def test_positive_projection(self):
        from ai.prediction.projection import CriticalThresholdProjector

        p = CriticalThresholdProjector(critical_threshold_um=200.0)
        result = p.project_hours_to_critical(
            current_wear_um=100.0,
            wear_rate_um_per_hour=5.0,
        )
        assert result["hours_to_critical"] == 20.0

    def test_already_critical(self):
        from ai.prediction.projection import CriticalThresholdProjector

        p = CriticalThresholdProjector(critical_threshold_um=200.0)
        result = p.project_hours_to_critical(
            current_wear_um=210.0,
            wear_rate_um_per_hour=5.0,
        )
        assert result["hours_to_critical"] == 0.0
        assert result["confidence"] == "critical"

    def test_very_slow_wear(self):
        from ai.prediction.projection import CriticalThresholdProjector

        p = CriticalThresholdProjector(critical_threshold_um=200.0)
        result = p.project_hours_to_critical(
            current_wear_um=50.0,
            wear_rate_um_per_hour=0.0001,
        )
        assert result["hours_to_critical"] == 999.0


class TestScenarios:
    def test_scenario_ordering(self):
        from ai.prediction.scenarios import ScenarioProjector

        p = ScenarioProjector(critical_threshold_um=200.0)
        result = p.project_scenarios(
            current_wear_um=100.0,
            wear_rate_um_per_hour=5.0,
            current_time=datetime(2026, 5, 17, 0, 0),
        )
        baseline = result["baseline"]["hours"]
        pessimistic = result["pessimistic"]["hours"]
        optimistic = result["optimistic"]["hours"]

        assert optimistic > baseline
        assert baseline > pessimistic

    def test_projection_points_count(self):
        from ai.prediction.scenarios import ScenarioProjector

        p = ScenarioProjector(critical_threshold_um=200.0, projection_interval_hours=1.0)
        result = p.project_scenarios(
            current_wear_um=50.0,
            wear_rate_um_per_hour=5.0,
            current_time=datetime(2026, 5, 17, 0, 0),
        )
        points = result["projection_points"]
        assert len(points) > 0
        assert points[0]["wear_um"] == 50.0

    def test_scenarios_critical_at_timestamps(self):
        from ai.prediction.scenarios import ScenarioProjector

        p = ScenarioProjector(critical_threshold_um=200.0)
        now = datetime(2026, 5, 17, 0, 0)
        result = p.project_scenarios(
            current_wear_um=100.0,
            wear_rate_um_per_hour=10.0,
            current_time=now,
        )
        baseline_critical = datetime.fromisoformat(result["baseline"]["critical_at"])
        assert baseline_critical > now


class TestTrends:
    def test_accelerating_trend(self):
        from ai.prediction.trends import WearTrendAnalyzer

        analyzer = WearTrendAnalyzer(min_periods=3)
        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(5)]
        wear = np.array([0.0, 10.0, 25.0, 50.0, 100.0])

        result = analyzer.analyze_trend(timestamps, wear)
        assert result["trend"] == "accelerating"

    def test_stable_trend(self):
        from ai.prediction.trends import WearTrendAnalyzer

        analyzer = WearTrendAnalyzer(min_periods=3)
        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(5)]
        wear = np.array([0.0, 30.0, 60.0, 90.0, 120.0])

        result = analyzer.analyze_trend(timestamps, wear)
        assert result["trend"] == "stable"

    def test_decelerating_trend(self):
        from ai.prediction.trends import WearTrendAnalyzer

        analyzer = WearTrendAnalyzer(min_periods=3)
        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(5)]
        wear = np.array([0.0, 50.0, 90.0, 110.0, 120.0])

        result = analyzer.analyze_trend(timestamps, wear)
        assert result["trend"] == "decelerating"

    def test_insufficient_data_trend(self):
        from ai.prediction.trends import WearTrendAnalyzer

        analyzer = WearTrendAnalyzer(min_periods=3)
        now = datetime(2026, 1, 1)
        timestamps = [now, now + timedelta(hours=1)]
        wear = np.array([0.0, 10.0])

        result = analyzer.analyze_trend(timestamps, wear)
        assert result["trend"] == "insufficient_data"


class TestPredictionService:
    def test_status_level_determination(self):
        from services.prediction_service import PredictionService

        class MockSupabase:
            pass

        service = PredictionService(MockSupabase(), critical_threshold_um=200.0)

        assert service._determine_status(20.0, 100.0) == "red"
        assert service._determine_status(48.0, 100.0) == "yellow"
        assert service._determine_status(100.0, 100.0) == "green"
        assert service._determine_status(50.0, 210.0) == "red"

    def test_prediction_with_data(self):
        from datetime import timezone

        from services.prediction_service import PredictionService

        mock_anomalies = [
            {
                "estimated_wear_um": 30.0,
                "detected_at": "2026-01-01T00:00:00Z",
                "machine_id": "Set1",
                "created_at": "2026-01-01T00:00:00Z",
            },
            {
                "estimated_wear_um": 60.0,
                "detected_at": "2026-01-01T10:00:00Z",
                "machine_id": "Set1",
                "created_at": "2026-01-01T10:00:00Z",
            },
            {
                "estimated_wear_um": 90.0,
                "detected_at": "2026-01-01T20:00:00Z",
                "machine_id": "Set1",
                "created_at": "2026-01-01T20:00:00Z",
            },
            {
                "estimated_wear_um": 120.0,
                "detected_at": "2026-01-02T06:00:00Z",
                "machine_id": "Set1",
                "created_at": "2026-01-02T06:00:00Z",
            },
        ]

        class MockQuery:
            def __init__(self, data):
                self.data = data
                self._order_col = None
                self._order_dir = None
                self._eq_col = None
                self._eq_val = None

            def select(self, _):
                return self

            def eq(self, col, val):
                self.data = [d for d in self.data if d.get(col) == val]
                return self

            def order(self, col, desc=False):
                self.data = sorted(self.data, key=lambda d: d.get(col, ""), reverse=desc)
                return self

            def execute(self):
                return self

        class MockTable:
            def __init__(self, data):
                self._data = data

            def select(self, *_):
                return MockQuery(list(self._data))

        class MockSupabase:
            def table(self, name):
                return MockTable(mock_anomalies)

        service = PredictionService(MockSupabase(), critical_threshold_um=200.0)
        result = service.get_prediction_sync("Set1")

        assert result["machine_id"] == "Set1"
        assert result["current_wear_um"] == pytest.approx(120.0)
        assert result["wear_rate_um_per_hour"] == pytest.approx(3.0, rel=0.01)
        assert result["hours_to_critical"] > 0
        assert result["confidence"] in ("high", "medium")

    def test_get_prediction_sync(self):
        from services.prediction_service import PredictionService

        mock_anomalies = [
            {
                "estimated_wear_um": 100.0,
                "detected_at": "2026-01-01T00:00:00Z",
                "machine_id": "Set3",
                "created_at": "2026-01-01T00:00:00Z",
            },
            {
                "estimated_wear_um": 150.0,
                "detected_at": "2026-01-02T00:00:00Z",
                "machine_id": "Set3",
                "created_at": "2026-01-02T00:00:00Z",
            },
        ]

        class MockQuery:
            def __init__(self, data):
                self.data = data

            def select(self, _):
                return self

            def eq(self, col, val):
                self.data = [d for d in self.data if d.get(col) == val]
                return self

            def order(self, col, desc=False):
                self.data = sorted(self.data, key=lambda d: d.get(col, ""), reverse=desc)
                return self

            def execute(self):
                return self

        class MockTable:
            def __init__(self, data):
                self._data = data

            def select(self, *_):
                return MockQuery(list(self._data))

        class MockSupabase:
            def table(self, name):
                return MockTable(mock_anomalies)

        service = PredictionService(MockSupabase(), critical_threshold_um=200.0)
        result = service.get_prediction_sync("Set3")
        assert result["machine_id"] == "Set3"


class TestPredictionResponseModel:
    def test_model_instantiation(self):
        from routers.predictions import PredictionResponse, Scenarios

        response = PredictionResponse(
            machine_id="Set3",
            current_wear_um=145.0,
            critical_threshold_um=200.0,
            wear_rate_um_per_hour=2.8,
            hours_to_critical=19.6,
            confidence="medium",
            trend="stable",
            scenarios=Scenarios(
                baseline={
                    "hours": 20.0,
                    "critical_at": "2026-05-17T06:00:00Z",
                    "wear_rate_multiplier": 1.0,
                },
                pessimistic={
                    "hours": 16.0,
                    "critical_at": "2026-05-17T02:00:00Z",
                    "wear_rate_multiplier": 1.25,
                },
                optimistic={
                    "hours": 27.0,
                    "critical_at": "2026-05-17T13:00:00Z",
                    "wear_rate_multiplier": 0.75,
                },
            ),
            projection_points=[
                {"timestamp": "2026-05-16T10:00:00Z", "wear_um": 145.0},
            ],
            last_check_at="2026-05-16T10:00:00Z",
            status="yellow",
        )
        assert response.machine_id == "Set3"

    def test_factory_overview_response(self):
        from routers.predictions import FactoryOverviewResponse, MachineOverview

        response = FactoryOverviewResponse(
            machines=[
                MachineOverview(machine_id="Set1", status="green", hours_to_critical=100.0),
                MachineOverview(machine_id="Set3", status="yellow", hours_to_critical=48.0),
            ]
        )
        assert len(response.machines) == 2


class TestChatPredictionIntegration:
    def test_format_prediction_message(self):
        from routers.chat import _format_prediction_message

        prediction = {
            "hours_to_critical": 19.6,
            "confidence": "medium",
            "trend": "stable",
            "current_wear_um": 145.0,
            "scenarios": {
                "baseline": {"hours": 20.0},
                "pessimistic": {"hours": 16.0},
                "optimistic": {"hours": 27.0},
            },
        }

        msg = _format_prediction_message(prediction)
        assert "Asinma Tahmini" in msg
        assert "19.6" in msg
        assert "Normal=20.0h" in msg
        assert "Kotu=16.0h" in msg
        assert "Iyi=27.0h" in msg

    def test_format_prediction_message_no_scenarios(self):
        from routers.chat import _format_prediction_message

        prediction = {
            "hours_to_critical": 50.0,
            "confidence": "high",
            "trend": "decelerating",
            "current_wear_um": 80.0,
            "scenarios": {},
        }

        msg = _format_prediction_message(prediction)
        assert "50.0" in msg
        assert "Yavasliyor" in msg


class TestSeedScript:
    def test_build_anomaly_records(self):
        from scripts.seed_predictions import build_anomaly_records

        images = [
            {"id": 1, "set_id": 1, "wear": 30.0, "wear_type": "flank_wear",
             "timestamp": "2022-09-09T13:42:21Z", "image_name": "Set1/img1.jpg",
             "set_name": "Set1"},
            {"id": 2, "set_id": 1, "wear": 60.0, "wear_type": "flank_wear",
             "timestamp": "2022-09-09T14:02:11Z", "image_name": "Set1/img2.jpg",
             "set_name": "Set1"},
            {"id": 3, "set_id": 2, "wear": 50.0, "wear_type": "adhesion",
             "timestamp": None, "image_name": "Set2/img1.jpg",
             "set_name": "Set2"},
        ]

        records = build_anomaly_records(images)
        assert len(records) == 2  # third skipped (no timestamp)

        assert records[0]["machine_id"] == "Set1"
        assert records[0]["estimated_wear_um"] == 30.0
        assert records[0]["detected_at"] == "2022-09-09T13:42:21Z"
        assert records[1]["machine_id"] == "Set1"
        assert records[1]["estimated_wear_um"] == 60.0


class TestPipelineEndToEnd:
    """Full pipeline test: calibration → wear rate → projection → scenarios."""

    def test_full_pipeline_with_mock_data(self):
        from ai.prediction.calibration import WearCalibrator
        from ai.prediction.projection import CriticalThresholdProjector
        from ai.prediction.scenarios import ScenarioProjector
        from ai.prediction.trends import WearTrendAnalyzer
        from ai.prediction.wear_rate import WearRateCalculator

        now = datetime(2026, 1, 1)
        timestamps = [now + timedelta(hours=i * 10) for i in range(6)]
        scores = np.array([0.0, 0.15, 0.30, 0.45, 0.60, 0.75])

        cal = WearCalibrator(linear_scale=200.0)
        wear_values = cal.predict(scores)

        rate_calc = WearRateCalculator(min_data_points=3)
        rate_result = rate_calc.calculate_with_confidence(timestamps, wear_values)
        wear_rate = rate_result["wear_rate_um_per_hour"]

        proj = CriticalThresholdProjector(critical_threshold_um=200.0)
        proj_result = proj.project_hours_to_critical(
            current_wear_um=float(wear_values[-1]),
            wear_rate_um_per_hour=wear_rate,
            r_squared=rate_result["r_squared"],
            data_points=rate_result["data_points"],
        )

        trend_analyzer = WearTrendAnalyzer(min_periods=3)
        trend_result = trend_analyzer.analyze_trend(timestamps, wear_values)

        scenario_proj = ScenarioProjector(critical_threshold_um=200.0)
        scenarios = scenario_proj.project_scenarios(
            current_wear_um=float(wear_values[-1]),
            wear_rate_um_per_hour=wear_rate,
            current_time=timestamps[-1],
        )

        assert wear_rate > 0
        assert proj_result["hours_to_critical"] > 0
        assert scenarios["optimistic"]["hours"] > scenarios["pessimistic"]["hours"]
        assert trend_result["trend"] in ("stable", "accelerating", "decelerating", "insufficient_data")
