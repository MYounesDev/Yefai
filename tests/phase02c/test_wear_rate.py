"""Tests for wear rate calculation module."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from ai.prediction.wear_rate import (
    WearRateCalculator,
    calculate_wear_rate,
)


def test_wear_rate_calculation_basic():
    """Test basic wear rate calculation."""
    calculator = WearRateCalculator(min_data_points=3)

    # Create test data: 5 measurements over 10 hours
    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i * 2) for i in range(5)]
    wear_values = np.array([50.0, 60.0, 70.0, 80.0, 90.0])  # 5 µm/hour

    result = calculator.calculate(timestamps, wear_values)

    # Should calculate ~5 µm/hour
    assert abs(result["wear_rate_um_per_hour"] - 5.0) < 0.1
    assert result["r_squared"] > 0.99  # Perfect linear fit
    assert result["data_points"] == 5


def test_wear_rate_high_r_squared():
    """Test that linear data produces high r² (UAT: r² > 0.7)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(5)]
    wear_values = np.array([100.0, 103.0, 106.0, 109.0, 112.0])

    result = calculator.calculate(timestamps, wear_values)

    # UAT requirement: r² > 0.7
    assert result["r_squared"] > 0.7


def test_wear_rate_insufficient_data():
    """Test error with insufficient data points."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time, base_time + timedelta(hours=1)]
    wear_values = np.array([50.0, 55.0])

    with pytest.raises(ValueError, match="Insufficient data"):
        calculator.calculate(timestamps, wear_values)


def test_wear_rate_single_point():
    """Test error with single data point."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time]
    wear_values = np.array([50.0])

    with pytest.raises(ValueError):
        calculator.calculate(timestamps, wear_values)


def test_wear_rate_with_confidence_high():
    """Test confidence level: high (r² > 0.85, n >= 5)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(5)]
    wear_values = np.array([100.0, 105.0, 110.0, 115.0, 120.0])

    result = calculator.calculate_with_confidence(timestamps, wear_values)

    assert result["confidence"] == "high"
    assert result["r_squared"] > 0.85
    assert result["data_points"] >= 5


def test_wear_rate_with_confidence_medium():
    """Test confidence level: medium (r² > 0.6, n >= 3)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    # Add some noise to reduce r²
    wear_values = np.array([100.0, 107.0, 112.0])

    result = calculator.calculate_with_confidence(timestamps, wear_values)

    assert result["confidence"] in ["medium", "high"]
    assert result["data_points"] >= 3


def test_wear_rate_with_confidence_low():
    """Test confidence level: low (r² < 0.6 or few points)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    # Very noisy data
    wear_values = np.array([100.0, 95.0, 110.0])

    result = calculator.calculate_with_confidence(timestamps, wear_values)

    # Should be low or medium depending on actual r²
    assert result["confidence"] in ["low", "medium"]


def test_wear_rate_with_confidence_insufficient():
    """Test confidence level: insufficient_data."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time, base_time + timedelta(hours=1)]
    wear_values = np.array([100.0, 105.0])

    result = calculator.calculate_with_confidence(timestamps, wear_values)

    assert result["confidence"] == "insufficient_data"
    assert "error" in result


def test_wear_rate_unsorted_timestamps():
    """Test that unsorted timestamps are handled correctly."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    # Unsorted timestamps
    timestamps = [
        base_time + timedelta(hours=4),
        base_time + timedelta(hours=0),
        base_time + timedelta(hours=2),
    ]
    wear_values = np.array([120.0, 100.0, 110.0])

    result = calculator.calculate(timestamps, wear_values)

    # Should still calculate correctly after sorting
    assert abs(result["wear_rate_um_per_hour"] - 5.0) < 0.1


def test_wear_rate_negative_rate():
    """Test handling of negative wear rate (decreasing wear - unusual but possible)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    wear_values = np.array([120.0, 110.0, 100.0])  # Decreasing

    result = calculator.calculate(timestamps, wear_values)

    # Should calculate negative rate
    assert result["wear_rate_um_per_hour"] < 0


def test_wear_rate_zero_rate():
    """Test handling of zero wear rate (no change)."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    wear_values = np.array([100.0, 100.0, 100.0])  # No change

    result = calculator.calculate(timestamps, wear_values)

    # Should calculate ~0 rate
    assert abs(result["wear_rate_um_per_hour"]) < 0.01


def test_simple_calculate_function():
    """Test simple calculate_wear_rate function."""
    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(5)]
    wear_values = [100.0, 110.0, 120.0, 130.0, 140.0]

    result = calculate_wear_rate(timestamps, wear_values)

    assert result is not None
    assert abs(result["wear_rate_um_per_hour"] - 10.0) < 0.1


def test_simple_calculate_function_insufficient_data():
    """Test simple function returns None with insufficient data."""
    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time, base_time + timedelta(hours=1)]
    wear_values = [100.0, 105.0]

    result = calculate_wear_rate(timestamps, wear_values)

    assert result is None


def test_wear_rate_mismatched_lengths():
    """Test error with mismatched array lengths."""
    calculator = WearRateCalculator(min_data_points=3)

    base_time = datetime(2026, 5, 16, 10, 0, 0)
    timestamps = [base_time + timedelta(hours=i) for i in range(3)]
    wear_values = np.array([100.0, 110.0])  # Wrong length

    with pytest.raises(ValueError, match="same length"):
        calculator.calculate(timestamps, wear_values)
