"""Tests for critical threshold projection module."""


import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from ai.prediction.projection import (
    CriticalThresholdProjector,
    project_hours_to_critical,
)


def test_projection_basic():
    """Test basic projection calculation."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    # (200 - 100) / 5 = 20 hours
    assert abs(result["hours_to_critical"] - 20.0) < 0.1
    assert result["confidence"] == "high"


def test_projection_already_critical():
    """Test projection when already at critical threshold."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=210.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    # Already critical
    assert result["hours_to_critical"] == 0.0
    assert result["confidence"] == "critical"


def test_projection_at_threshold():
    """Test projection when exactly at threshold."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=200.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    assert result["hours_to_critical"] == 0.0


def test_projection_very_low_rate():
    """Test projection with very low wear rate."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=0.0001,  # Very slow
        r_squared=0.9,
        data_points=5,
    )

    # Should cap at max hours (999)
    assert result["hours_to_critical"] == 999.0


def test_projection_negative_rate():
    """Test projection with negative wear rate."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=-1.0,  # Decreasing
        r_squared=0.9,
        data_points=5,
    )

    # Should cap at max hours
    assert result["hours_to_critical"] == 999.0


def test_projection_confidence_high():
    """Test high confidence determination (r² > 0.85, n >= 5)."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    assert result["confidence"] == "high"


def test_projection_confidence_medium():
    """Test medium confidence determination (r² > 0.6, n >= 3)."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.7,
        data_points=3,
    )

    assert result["confidence"] == "medium"


def test_projection_confidence_low():
    """Test low confidence determination (r² < 0.6)."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.5,
        data_points=5,
    )

    assert result["confidence"] == "low"


def test_projection_confidence_insufficient_data():
    """Test insufficient_data confidence (n < 3)."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=2,
    )

    assert result["confidence"] == "insufficient_data"


def test_projection_20_hours_uat():
    """Test UAT scenario: 20 hours to critical."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    # UAT: Should correctly calculate 20 hours
    assert abs(result["hours_to_critical"] - 20.0) < 0.1
    assert result["remaining_wear_um"] == 100.0


def test_projection_custom_threshold():
    """Test projection with custom critical threshold."""
    projector = CriticalThresholdProjector(critical_threshold_um=300.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=10.0,
        r_squared=0.9,
        data_points=5,
    )

    # (300 - 100) / 10 = 20 hours
    assert abs(result["hours_to_critical"] - 20.0) < 0.1
    assert result["critical_threshold_um"] == 300.0


def test_projection_near_critical():
    """Test projection when very close to critical."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=195.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    # (200 - 195) / 5 = 1 hour
    assert abs(result["hours_to_critical"] - 1.0) < 0.1


def test_projection_slow_wear():
    """Test projection with slow wear rate."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=0.1,
        r_squared=0.9,
        data_points=5,
    )

    # (200 - 100) / 0.1 = 1000 hours, capped at 999
    assert result["hours_to_critical"] == 999.0


def test_simple_project_function():
    """Test simple project_hours_to_critical function."""
    hours = project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        critical_threshold_um=200.0,
        r_squared=0.9,
        data_points=5,
    )

    assert abs(hours - 20.0) < 0.1


def test_projection_result_contains_all_fields():
    """Test that projection result contains all expected fields."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=100.0,
        wear_rate_um_per_hour=5.0,
        r_squared=0.9,
        data_points=5,
    )

    # Check all required fields
    assert "hours_to_critical" in result
    assert "confidence" in result
    assert "current_wear_um" in result
    assert "critical_threshold_um" in result
    assert "wear_rate_um_per_hour" in result
    assert "remaining_wear_um" in result


def test_projection_zero_current_wear():
    """Test projection starting from zero wear."""
    projector = CriticalThresholdProjector(critical_threshold_um=200.0)

    result = projector.project_hours_to_critical(
        current_wear_um=0.0,
        wear_rate_um_per_hour=10.0,
        r_squared=0.9,
        data_points=5,
    )

    # 200 / 10 = 20 hours
    assert abs(result["hours_to_critical"] - 20.0) < 0.1
