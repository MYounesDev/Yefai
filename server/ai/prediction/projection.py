"""Critical threshold projection for wear prediction."""

import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Default critical threshold in micrometers
DEFAULT_CRITICAL_THRESHOLD_UM = 200.0

# Maximum hours to report (for very slow wear rates)
MAX_HOURS_TO_CRITICAL = 999.0

# Minimum wear rate to avoid division by zero (µm/hour)
MIN_WEAR_RATE = 0.001

ConfidenceLevel = Literal["high", "medium", "low", "insufficient_data"]


class CriticalThresholdProjector:
    """Projects time to critical threshold based on current wear and wear rate."""

    def __init__(self, critical_threshold_um: float = DEFAULT_CRITICAL_THRESHOLD_UM):
        """
        Initialize projector.

        Args:
            critical_threshold_um: Critical wear threshold in micrometers
        """
        self.critical_threshold_um = critical_threshold_um

    def project_hours_to_critical(
        self,
        current_wear_um: float,
        wear_rate_um_per_hour: float,
        r_squared: float = 0.0,
        data_points: int = 0,
    ) -> dict[str, float | str]:
        """
        Calculate hours until critical threshold is reached.

        Args:
            current_wear_um: Current wear measurement (µm)
            wear_rate_um_per_hour: Wear rate (µm/hour)
            r_squared: R² value from regression (for confidence)
            data_points: Number of data points used (for confidence)

        Returns:
            Dictionary with hours_to_critical, confidence, and related metrics
        """
        # Check if already at or past critical threshold
        if current_wear_um >= self.critical_threshold_um:
            logger.warning(
                f"Already at critical: current={current_wear_um:.2f}µm, "
                f"threshold={self.critical_threshold_um:.2f}µm"
            )
            return {
                "hours_to_critical": 0.0,
                "confidence": "critical",
                "current_wear_um": current_wear_um,
                "critical_threshold_um": self.critical_threshold_um,
                "wear_rate_um_per_hour": wear_rate_um_per_hour,
            }

        # Check for very low or negative wear rate
        if wear_rate_um_per_hour < MIN_WEAR_RATE:
            logger.info(
                f"Very low wear rate ({wear_rate_um_per_hour:.6f} µm/hour), setting to max hours"
            )
            return {
                "hours_to_critical": MAX_HOURS_TO_CRITICAL,
                "confidence": self._determine_confidence(r_squared, data_points),
                "current_wear_um": current_wear_um,
                "critical_threshold_um": self.critical_threshold_um,
                "wear_rate_um_per_hour": wear_rate_um_per_hour,
            }

        # Calculate hours to critical
        remaining_wear = self.critical_threshold_um - current_wear_um
        hours_to_critical = remaining_wear / wear_rate_um_per_hour

        # Cap at maximum
        hours_to_critical = min(hours_to_critical, MAX_HOURS_TO_CRITICAL)

        confidence = self._determine_confidence(r_squared, data_points)

        logger.info(
            f"Projected hours to critical: {hours_to_critical:.2f}h (confidence={confidence})"
        )

        return {
            "hours_to_critical": hours_to_critical,
            "confidence": confidence,
            "current_wear_um": current_wear_um,
            "critical_threshold_um": self.critical_threshold_um,
            "wear_rate_um_per_hour": wear_rate_um_per_hour,
            "remaining_wear_um": remaining_wear,
        }

    def _determine_confidence(self, r_squared: float, data_points: int) -> ConfidenceLevel:
        """
        Determine confidence level based on regression quality.

        Args:
            r_squared: R² value from regression
            data_points: Number of data points

        Returns:
            Confidence level: 'high', 'medium', 'low', or 'insufficient_data'
        """
        if data_points < 3:
            return "insufficient_data"
        elif r_squared > 0.85 and data_points >= 5:
            return "high"
        elif r_squared > 0.6 and data_points >= 3:
            return "medium"
        else:
            return "low"


def project_hours_to_critical(
    current_wear_um: float,
    wear_rate_um_per_hour: float,
    critical_threshold_um: float = DEFAULT_CRITICAL_THRESHOLD_UM,
    r_squared: float = 0.0,
    data_points: int = 0,
) -> float:
    """
    Simple function to calculate hours to critical threshold.

    Args:
        current_wear_um: Current wear (µm)
        wear_rate_um_per_hour: Wear rate (µm/hour)
        critical_threshold_um: Critical threshold (µm)
        r_squared: R² value (optional)
        data_points: Number of data points (optional)

    Returns:
        Hours until critical threshold
    """
    projector = CriticalThresholdProjector(critical_threshold_um)
    result = projector.project_hours_to_critical(
        current_wear_um, wear_rate_um_per_hour, r_squared, data_points
    )
    return result["hours_to_critical"]
