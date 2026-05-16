"""Tests for scenario projection module."""

import sys
from datetime import datetime
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from ai.prediction.scenarios import (
    ScenarioProjector,
    project_scenarios,
)


def test_scenarios_basic():
    """Test basic scenario generation."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Check all three scenarios exist
    assert "baseline" in result
    assert "pessimistic" in result
    assert "optimistic" in result
    assert "projection_points" in result


def test_scenarios_ordering():
    """Test UAT: optimistic > baseline > pessimistic hours."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    baseline_hours = result["baseline"]["hours"]
    pessimistic_hours = result["pessimistic"]["hours"]
    optimistic_hours = result["optimistic"]["hours"]

    # UAT requirement: optimistic > baseline > pessimistic
    assert optimistic_hours > baseline_hours
    assert baseline_hours > pessimistic_hours


def test_scenarios_baseline_calculation():
    """Test baseline scenario calculation (1.0x multiplier)."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Baseline: (200 - 100) / 5 = 20 hours
    assert abs(result["baseline"]["hours"] - 20.0) < 0.1
    assert result["baseline"]["wear_rate_multiplier"] == 1.0


def test_scenarios_pessimistic_calculation():
    """Test pessimistic scenario calculation (1.25x multiplier)."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Pessimistic: (200 - 100) / (5 * 1.25) = 16 hours
    assert abs(result["pessimistic"]["hours"] - 16.0) < 0.1
    assert result["pessimistic"]["wear_rate_multiplier"] == 1.25


def test_scenarios_optimistic_calculation():
    """Test optimistic scenario calculation (0.75x multiplier)."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Optimistic: (200 - 100) / (5 * 0.75) = 26.67 hours
    assert abs(result["optimistic"]["hours"] - 26.67) < 0.1
    assert result["optimistic"]["wear_rate_multiplier"] == 0.75


def test_scenarios_critical_timestamps():
    """Test that critical_at timestamps are correctly calculated."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Parse timestamps
    baseline_time = datetime.fromisoformat(result["baseline"]["critical_at"])
    pessimistic_time = datetime.fromisoformat(result["pessimistic"]["critical_at"])
    optimistic_time = datetime.fromisoformat(result["optimistic"]["critical_at"])

    # Pessimistic should be earliest, optimistic latest
    assert pessimistic_time < baseline_time < optimistic_time


def test_scenarios_projection_points():
    """Test that projection points are generated."""
    projector = ScenarioProjector(
        critical_threshold_um=200.0,
        projection_interval_hours=1.0,
    )

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    points = result["projection_points"]

    # Should have multiple points
    assert len(points) > 1

    # First point should be current state
    assert points[0]["wear_um"] == 100.0

    # Last point should be at or near critical
    assert points[-1]["wear_um"] <= 200.0


def test_scenarios_projection_points_increasing():
    """Test that projection points show increasing wear."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    points = result["projection_points"]

    # Wear should increase over time
    for i in range(1, len(points)):
        assert points[i]["wear_um"] >= points[i - 1]["wear_um"]


def test_scenarios_already_critical():
    """Test scenarios when already at critical."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=210.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # All scenarios should be 0 hours
    assert result["baseline"]["hours"] == 0.0
    assert result["pessimistic"]["hours"] == 0.0
    assert result["optimistic"]["hours"] == 0.0


def test_scenarios_very_slow_wear():
    """Test scenarios with very slow wear rate."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=0.0001,
        current_time=current_time,
    )

    # All scenarios should cap at 999 hours
    assert result["baseline"]["hours"] == 999.0
    assert result["pessimistic"]["hours"] == 999.0
    assert result["optimistic"]["hours"] == 999.0


def test_scenarios_custom_threshold():
    """Test scenarios with custom critical threshold."""
    projector = ScenarioProjector(critical_threshold_um=300.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=10.0,
        current_time=current_time,
    )

    # Baseline: (300 - 100) / 10 = 20 hours
    assert abs(result["baseline"]["hours"] - 20.0) < 0.1


def test_scenarios_custom_interval():
    """Test scenarios with custom projection interval."""
    projector = ScenarioProjector(
        critical_threshold_um=200.0,
        projection_interval_hours=5.0,
    )

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    points = result["projection_points"]

    # With 5-hour intervals and 20 hours total, should have ~5 points
    assert len(points) <= 6  # Including start point


def test_simple_project_scenarios_function():
    """Test simple project_scenarios function."""
    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
        critical_threshold_um=200.0,
    )

    assert "baseline" in result
    assert "pessimistic" in result
    assert "optimistic" in result


def test_scenarios_result_format():
    """Test that scenario results match expected format."""
    projector = ScenarioProjector(critical_threshold_um=200.0)

    current_time = datetime(2026, 5, 16, 10, 0, 0)
    result = projector.project_scenarios(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        current_time=current_time,
    )

    # Check baseline format
    assert "hours" in result["baseline"]
    assert "critical_at" in result["baseline"]
    assert "wear_rate_multiplier" in result["baseline"]

    # Check projection points format
    for point in result["projection_points"]:
        assert "timestamp" in point
        assert "wear_um" in point
