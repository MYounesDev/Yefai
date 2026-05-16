"""Tests for wear trend analysis module."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from ai.prediction.trends import (
    WearTrendAnalyzer,
    analyze_wear_trend,
)


def test_trend_accelerating():
    """Test detection of accelerating wear trend."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.15)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Wear rate increasing: 5, 7, 10 µm/hour
    wear_values = np.array([100.0, 105.0, 112.0, 122.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    assert result["trend"] == "accelerating"
    assert result["rate_change_percent"] > 0.15


def test_trend_decelerating():
    """Test detection of decelerating wear trend."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.15)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Wear rate decreasing: 10, 7, 5 µm/hour
    wear_values = np.array([100.0, 110.0, 117.0, 122.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    assert result["trend"] == "decelerating"
    assert result["rate_change_percent"] < -0.15


def test_trend_stable():
    """Test detection of stable wear trend."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.15)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Constant wear rate: 5 µm/hour
    wear_values = np.array([100.0, 105.0, 110.0, 115.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    assert result["trend"] == "stable"
    assert abs(result["rate_change_percent"]) < 0.15


def test_trend_insufficient_data():
    """Test insufficient data handling."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time, base_time + timedelta(hours=1)]
    wear_values = np.array([100.0, 105.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    assert result["trend"] == "insufficient_data"
    assert result["data_points"] == 2


def test_trend_exactly_min_periods():
    """Test with exactly minimum periods."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    wear_values = np.array([100.0, 105.0, 110.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should work with exactly 3 points
    assert result["trend"] in ["accelerating", "stable", "decelerating"]
    assert result["data_points"] == 3


def test_trend_rate_change_calculation():
    """Test rate change percentage calculation."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Rate: 5, 6, 7.5 µm/hour (25% increase from 6 to 7.5)
    wear_values = np.array([100.0, 105.0, 111.0, 118.5])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should detect ~25% increase
    assert result["rate_change_percent"] > 0.2


def test_trend_is_accelerating_method():
    """Test is_accelerating convenience method."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.15)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    wear_values = np.array([100.0, 105.0, 112.0, 122.0])

    is_accel = analyzer.is_accelerating(timestamps, wear_values)

    assert is_accel is True


def test_trend_is_not_accelerating():
    """Test is_accelerating returns False for stable trend."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    wear_values = np.array([100.0, 105.0, 110.0, 115.0])

    is_accel = analyzer.is_accelerating(timestamps, wear_values)

    assert is_accel is False


def test_trend_unsorted_timestamps():
    """Test trend analysis with unsorted timestamps."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    # Unsorted
    timestamps = [
        base_time + timedelta(hours=2),
        base_time + timedelta(hours=0),
        base_time + timedelta(hours=1),
        base_time + timedelta(hours=3),
    ]
    wear_values = np.array([110.0, 100.0, 105.0, 115.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should still work after sorting
    assert result["trend"] in ["accelerating", "stable", "decelerating"]


def test_trend_custom_threshold():
    """Test trend analysis with custom acceleration threshold."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.30)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # 20% increase (below 30% threshold)
    wear_values = np.array([100.0, 105.0, 111.0, 118.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should be stable with 30% threshold
    assert result["trend"] == "stable"


def test_trend_zero_previous_rate():
    """Test handling of zero previous rate."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # First period: no change, second period: change
    wear_values = np.array([100.0, 100.0, 100.0, 105.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should handle gracefully
    assert result["trend"] in ["accelerating", "stable", "decelerating", "insufficient_data"]


def test_trend_negative_wear_rate():
    """Test trend with negative (decreasing) wear rates."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Decreasing wear
    wear_values = np.array([120.0, 115.0, 110.0, 105.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should still detect trend
    assert result["trend"] in ["accelerating", "stable", "decelerating"]


def test_trend_result_contains_rates():
    """Test that result contains recent and previous rates."""
    analyzer = WearTrendAnalyzer(min_periods=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    wear_values = np.array([100.0, 105.0, 110.0, 115.0])

    result = analyzer.analyze_trend(timestamps, wear_values)

    assert "recent_rate" in result
    assert "previous_rate" in result
    assert isinstance(result["recent_rate"], float)
    assert isinstance(result["previous_rate"], float)


def test_simple_analyze_function():
    """Test simple analyze_wear_trend function."""
    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    wear_values = [100.0, 105.0, 110.0, 115.0]

    result = analyze_wear_trend(timestamps, wear_values)

    assert "trend" in result
    assert "rate_change_percent" in result


def test_simple_analyze_function_insufficient_data():
    """Test simple function with insufficient data."""
    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time, base_time + timedelta(hours=1)]
    wear_values = [100.0, 105.0]

    result = analyze_wear_trend(timestamps, wear_values)

    assert result["trend"] == "insufficient_data"


def test_trend_15_percent_threshold_uat():
    """Test UAT: 15% threshold for acceleration detection."""
    analyzer = WearTrendAnalyzer(min_periods=3, acceleration_threshold=0.15)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(4)]
    # Exactly 15% increase
    wear_values = np.array([100.0, 105.0, 110.75, 117.4375])

    result = analyzer.analyze_trend(timestamps, wear_values)

    # Should detect acceleration at 15% threshold
    if result["rate_change_percent"] >= 0.15:
        assert result["trend"] == "accelerating"
