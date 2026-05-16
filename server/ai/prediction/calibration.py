"""Calibration module for converting anomaly scores to wear measurements."""

import logging

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


class WearCalibrator:
    """Calibrates anomaly scores (0-1) to wear measurements (µm)."""

    def __init__(
        self,
        linear_scale: float = 200.0,
        use_polynomial: bool = False,
        poly_degree: int = 2,
    ):
        """
        Initialize wear calibrator.

        Args:
            linear_scale: Scale factor for linear interpolation (default: 200µm at score=1.0)
            use_polynomial: Whether to use polynomial fit instead of linear
            poly_degree: Degree of polynomial fit if use_polynomial=True
        """
        self.linear_scale = linear_scale
        self.use_polynomial = use_polynomial
        self.poly_degree = poly_degree
        self.poly_coeffs: NDArray[np.float64] | None = None

    def fit(
        self, scores: NDArray[np.float64], actual_wear: NDArray[np.float64]
    ) -> "WearCalibrator":
        """
        Fit calibration model using actual wear data.

        Args:
            scores: Array of anomaly scores (0-1)
            actual_wear: Array of actual wear measurements (µm)

        Returns:
            Self for method chaining
        """
        if len(scores) != len(actual_wear):
            raise ValueError("Scores and actual_wear must have same length")

        if self.use_polynomial:
            # Polynomial fit: wear = c0 + c1*score + c2*score^2 + ...
            self.poly_coeffs = np.polyfit(scores, actual_wear, self.poly_degree)
            logger.info(
                f"Fitted polynomial calibration (degree={self.poly_degree}): "
                f"coeffs={self.poly_coeffs}"
            )
        else:
            # Linear fit: adjust scale based on actual data
            if len(scores) > 0 and np.max(scores) > 0:
                self.linear_scale = np.max(actual_wear) / np.max(scores)
                logger.info(f"Fitted linear calibration: scale={self.linear_scale:.2f}")

        return self

    def predict(self, scores: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Convert anomaly scores to wear measurements.

        Args:
            scores: Array of anomaly scores (0-1)

        Returns:
            Array of estimated wear measurements (µm)
        """
        if self.use_polynomial and self.poly_coeffs is not None:
            # Use polynomial model
            wear_um = np.polyval(self.poly_coeffs, scores)
        else:
            # Use linear interpolation: wear_um = score * linear_scale
            wear_um = scores * self.linear_scale

        # Ensure non-negative wear
        wear_um = np.maximum(wear_um, 0.0)

        return wear_um

    def evaluate(
        self, scores: NDArray[np.float64], actual_wear: NDArray[np.float64]
    ) -> dict[str, float]:
        """
        Evaluate calibration accuracy.

        Args:
            scores: Array of anomaly scores
            actual_wear: Array of actual wear measurements

        Returns:
            Dictionary with MAE and RMSE metrics
        """
        predicted_wear = self.predict(scores)

        mae = float(np.mean(np.abs(predicted_wear - actual_wear)))
        rmse = float(np.sqrt(np.mean((predicted_wear - actual_wear) ** 2)))

        logger.info(f"Calibration evaluation: MAE={mae:.2f}µm, RMSE={rmse:.2f}µm")

        return {"mae": mae, "rmse": rmse}


def calibrate_score_to_wear(score: float, linear_scale: float = 200.0) -> float:
    """
    Simple linear calibration: score → wear (µm).

    Args:
        score: Anomaly score (0-1)
        linear_scale: Scale factor (default: 200µm at score=1.0)

    Returns:
        Estimated wear in µm
    """
    wear_um = max(0.0, score * linear_scale)
    return wear_um
