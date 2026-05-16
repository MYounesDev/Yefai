"""Wear trend analysis to detect acceleration or deceleration."""

import logging
from datetime import datetime
from typing import Literal

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

TrendType = Literal["accelerating", "stable", "decelerating", "insufficient_data"]

# Threshold for trend detection (percentage change)
ACCELERATION_THRESHOLD = 0.15  # 15%


class WearTrendAnalyzer:
    """Analyzes wear trends to detect acceleration or deceleration."""

    def __init__(
        self,
        min_periods: int = 3,
        acceleration_threshold: float = ACCELERATION_THRESHOLD,
    ):
        """
        Initialize trend analyzer.

        Args:
            min_periods: Minimum number of periods required for analysis
            acceleration_threshold: Threshold for detecting acceleration (as fraction)
        """
        self.min_periods = min_periods
        self.acceleration_threshold = acceleration_threshold

    def analyze_trend(
        self,
        timestamps: list[datetime],
        wear_values: NDArray[np.float64],
    ) -> dict[str, str | float]:
        """
        Analyze wear trend from historical data.

        Args:
            timestamps: List of timestamps
            wear_values: Array of wear measurements (µm)

        Returns:
            Dictionary with trend type and rate change percentage
        """
        if len(timestamps) < self.min_periods:
            logger.warning(
                f"Insufficient data for trend analysis: need {self.min_periods}, "
                f"got {len(timestamps)}"
            )
            return {
                "trend": "insufficient_data",
                "rate_change_percent": 0.0,
                "data_points": len(timestamps),
            }

        # Sort by timestamp
        sorted_indices = np.argsort([ts.timestamp() for ts in timestamps])
        sorted_timestamps = [timestamps[i] for i in sorted_indices]
        sorted_wear = wear_values[sorted_indices]

        # Calculate wear rates for consecutive periods
        rates = self._calculate_period_rates(sorted_timestamps, sorted_wear)

        if len(rates) < 2:
            return {
                "trend": "insufficient_data",
                "rate_change_percent": 0.0,
                "data_points": len(timestamps),
            }

        # Compare last two periods
        recent_rate = rates[-1]
        previous_rate = rates[-2]

        # Calculate percentage change
        if previous_rate == 0:
            rate_change_percent = 0.0
        else:
            rate_change_percent = (recent_rate - previous_rate) / abs(previous_rate)

        # Determine trend
        if rate_change_percent > self.acceleration_threshold:
            trend: TrendType = "accelerating"
        elif rate_change_percent < -self.acceleration_threshold:
            trend = "decelerating"
        else:
            trend = "stable"

        logger.info(f"Trend analysis: {trend} (rate change: {rate_change_percent * 100:.1f}%)")

        return {
            "trend": trend,
            "rate_change_percent": float(rate_change_percent),
            "data_points": len(timestamps),
            "recent_rate": float(recent_rate),
            "previous_rate": float(previous_rate),
        }

    def _calculate_period_rates(
        self,
        timestamps: list[datetime],
        wear_values: NDArray[np.float64],
    ) -> list[float]:
        """Calculate wear rates for consecutive periods."""
        rates = []

        for i in range(1, len(timestamps)):
            time_diff_hours = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600.0
            wear_diff = wear_values[i] - wear_values[i - 1]

            if time_diff_hours > 0:
                rate = wear_diff / time_diff_hours
                rates.append(rate)

        return rates

    def is_accelerating(
        self,
        timestamps: list[datetime],
        wear_values: NDArray[np.float64],
    ) -> bool:
        """
        Check if wear is accelerating.

        Args:
            timestamps: List of timestamps
            wear_values: Array of wear measurements

        Returns:
            True if wear is accelerating above threshold
        """
        result = self.analyze_trend(timestamps, wear_values)
        return result["trend"] == "accelerating"


def analyze_wear_trend(
    timestamps: list[datetime],
    wear_values: list[float],
    min_periods: int = 3,
) -> dict[str, str | float]:
    """
    Simple function to analyze wear trend.

    Args:
        timestamps: List of timestamps
        wear_values: List of wear measurements (µm)
        min_periods: Minimum periods required

    Returns:
        Dictionary with trend type and rate change percentage
    """
    analyzer = WearTrendAnalyzer(min_periods=min_periods)
    return analyzer.analyze_trend(timestamps, np.array(wear_values))
