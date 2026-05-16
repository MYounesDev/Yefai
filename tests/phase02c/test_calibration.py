"""Tests for calibration module."""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

from ai.prediction.calibration import (
    WearCalibrator,
    calibrate_score_to_wear,
)


def test_linear_calibration_default_scale():
    """Test linear calibration with default scale (200µm)."""
    calibrator = WearCalibrator(linear_scale=200.0)

    scores = np.array([0.0, 0.5, 1.0])
    expected_wear = np.array([0.0, 100.0, 200.0])

    predicted_wear = calibrator.predict(scores)

    np.testing.assert_array_almost_equal(predicted_wear, expected_wear)


def test_linear_calibration_custom_scale():
    """Test linear calibration with custom scale."""
    calibrator = WearCalibrator(linear_scale=300.0)

    scores = np.array([0.0, 0.5, 1.0])
    expected_wear = np.array([0.0, 150.0, 300.0])

    predicted_wear = calibrator.predict(scores)

    np.testing.assert_array_almost_equal(predicted_wear, expected_wear)


def test_calibration_non_negative():
    """Test that calibration never produces negative wear."""
    calibrator = WearCalibrator(linear_scale=200.0)

    # Even with negative scores (edge case), wear should be non-negative
    scores = np.array([-0.1, 0.0, 0.5])
    predicted_wear = calibrator.predict(scores)

    assert np.all(predicted_wear >= 0.0)


def test_calibration_fit_adjusts_scale():
    """Test that fit() adjusts linear scale based on actual data."""
    calibrator = WearCalibrator(linear_scale=200.0, use_polynomial=False)

    # Actual data: scores and corresponding wear
    scores = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    actual_wear = np.array([50.0, 100.0, 150.0, 200.0, 250.0])

    calibrator.fit(scores, actual_wear)

    # Scale should be adjusted to 250 (max_wear / max_score)
    assert calibrator.linear_scale == 250.0


def test_polynomial_calibration():
    """Test polynomial calibration."""
    calibrator = WearCalibrator(use_polynomial=True, poly_degree=2)

    # Fit with quadratic relationship
    scores = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    actual_wear = np.array([0.0, 15.625, 62.5, 140.625, 250.0])  # quadratic

    calibrator.fit(scores, actual_wear)

    # Predict should use polynomial
    test_scores = np.array([0.5])
    predicted = calibrator.predict(test_scores)

    # Should be close to 62.5
    assert abs(predicted[0] - 62.5) < 5.0


def test_calibration_evaluate_mae():
    """Test MAE evaluation."""
    calibrator = WearCalibrator(linear_scale=200.0)

    scores = np.array([0.0, 0.5, 1.0])
    actual_wear = np.array([10.0, 110.0, 210.0])  # 10µm offset

    metrics = calibrator.evaluate(scores, actual_wear)

    # MAE should be 10µm
    assert abs(metrics["mae"] - 10.0) < 0.1


def test_calibration_evaluate_rmse():
    """Test RMSE evaluation."""
    calibrator = WearCalibrator(linear_scale=200.0)

    scores = np.array([0.0, 0.5, 1.0])
    actual_wear = np.array([0.0, 100.0, 200.0])  # Perfect fit

    metrics = calibrator.evaluate(scores, actual_wear)

    # RMSE should be near 0
    assert metrics["rmse"] < 0.1


def test_calibration_mae_under_30um():
    """Test that calibration achieves MAE < 30µm (UAT requirement)."""
    calibrator = WearCalibrator(linear_scale=200.0)

    # Realistic data with some noise
    scores = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    actual_wear = np.array([18.0, 62.0, 98.0, 142.0, 185.0])

    # Fit the calibrator
    calibrator.fit(scores, actual_wear)

    # Evaluate
    metrics = calibrator.evaluate(scores, actual_wear)

    # UAT: MAE < 30µm
    assert metrics["mae"] < 30.0


def test_simple_calibrate_function():
    """Test simple calibrate_score_to_wear function."""
    wear = calibrate_score_to_wear(0.5, linear_scale=200.0)
    assert wear == 100.0

    wear = calibrate_score_to_wear(1.0, linear_scale=200.0)
    assert wear == 200.0

    wear = calibrate_score_to_wear(0.0, linear_scale=200.0)
    assert wear == 0.0


def test_calibration_with_empty_arrays():
    """Test calibration with empty arrays."""
    calibrator = WearCalibrator()

    with pytest.raises(ValueError):
        calibrator.fit(np.array([]), np.array([1.0]))


def test_calibration_with_mismatched_lengths():
    """Test calibration with mismatched array lengths."""
    calibrator = WearCalibrator()

    with pytest.raises(ValueError):
        calibrator.fit(np.array([0.5]), np.array([100.0, 200.0]))
