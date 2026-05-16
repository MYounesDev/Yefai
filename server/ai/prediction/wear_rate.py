"""Wear rate calculation using linear regression."""

import logging
from datetime import datetime

import numpy as np
from numpy.typing import NDArray
from scipy import stats

logger = logging.getLogger(__name__)


class WearRateCalculator:
    """Calculates wear rate using linear regression on historical data."""

    def __init__(self, min_data_points: int = 3):
        """
        Initialize wear rate calculator.

        Args:
            min_data_points: Minimum number of data points required for calculation
        """
        self.min_data_points = min_data_points

    def calculate(
        self,
        timestamps: list[datetime],
        wear_values: NDArray[np.float64],
    ) -> dict[str, float]:
        """
        Calculate wear rate using linear regression.

        Args:
            timestamps: List of timestamps for each measurement
            wear_values: Array of wear measurements (µm)

        Returns:
            Dictionary with wear_rate_um_per_hour, r_squared, and data_points

        Raises:
            ValueError: If insufficient data points
        """
        if len(timestamps) != len(wear_values):
            raise ValueError("Timestamps and wear_values must have same length")

        if len(timestamps) < self.min_data_points:
            raise ValueError(
                f"Insufficient data: need at least {self.min_data_points} points, "
                f"got {len(timestamps)}"
            )

        # Convert timestamps to hours since first measurement
        sorted_indices = np.argsort([ts.timestamp() for ts in timestamps])
        sorted_timestamps = [timestamps[i] for i in sorted_indices]
        sorted_wear = wear_values[sorted_indices]

        first_time = sorted_timestamps[0]
        hours_elapsed = np.array(
            [(ts - first_time).total_seconds() / 3600.0 for ts in sorted_timestamps]
        )

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(hours_elapsed, sorted_wear)

        r_squared = r_value**2
        wear_rate_um_per_hour = float(slope)

        logger.info(
            f"Calculated wear rate: {wear_rate_um_per_hour:.4f} µm/hour, "
            f"r²={r_squared:.4f}, n={len(timestamps)}"
        )

        return {
            "wear_rate_um_per_hour": wear_rate_um_per_hour,
            "r_squared": r_squared,
            "data_points": len(timestamps),
            "intercept": float(intercept),
            "p_value": float(p_value),
            "std_err": float(std_err),
        }

    def calculate_with_confidence(
        self,
        timestamps: list[datetime],
        wear_values: NDArray[np.float64],
    ) -> dict[str, float | str]:
        """
        Calculate wear rate with confidence level.

        Args:
            timestamps: List of timestamps for each measurement
            wear_values: Array of wear measurements (µm)

        Returns:
            Dictionary with wear rate, r_squared, confidence level, and data_points
        """
        try:
            result = self.calculate(timestamps, wear_values)

            # Determine confidence level
            r_squared = result["r_squared"]
            data_points = result["data_points"]

            if r_squared > 0.85 and data_points >= 5:
                confidence = "high"
            elif r_squared > 0.6 and data_points >= 3:
                confidence = "medium"
            else:
                confidence = "low"

            result["confidence"] = confidence
            return result

        except ValueError as e:
            logger.warning(f"Cannot calculate wear rate: {e}")
            return {
                "wear_rate_um_per_hour": 0.0,
                "r_squared": 0.0,
                "confidence": "insufficient_data",
                "data_points": len(timestamps),
                "error": str(e),
            }


def calculate_wear_rate(
    timestamps: list[datetime],
    wear_values: list[float],
    min_data_points: int = 3,
) -> dict[str, float] | None:
    """
    Simple function to calculate wear rate.

    Args:
        timestamps: List of timestamps
        wear_values: List of wear measurements (µm)
        min_data_points: Minimum required data points

    Returns:
        Dictionary with wear rate and r_squared, or None if insufficient data
    """
    calculator = WearRateCalculator(min_data_points=min_data_points)
    try:
        return calculator.calculate(timestamps, np.array(wear_values))
    except ValueError:
        return None
