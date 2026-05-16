"""Scenario-based wear projection with baseline, pessimistic, and optimistic scenarios."""

import logging
from datetime import datetime, timedelta
from typing import TypedDict

logger = logging.getLogger(__name__)


class ScenarioResult(TypedDict):
    """Result for a single scenario."""

    hours: float
    critical_at: str  # ISO timestamp
    wear_rate_multiplier: float


class ProjectionPoint(TypedDict):
    """Single point in projection timeline."""

    timestamp: str  # ISO timestamp
    wear_um: float


class ScenarioProjection(TypedDict):
    """Complete scenario projection result."""

    baseline: ScenarioResult
    pessimistic: ScenarioResult
    optimistic: ScenarioResult
    projection_points: list[ProjectionPoint]


class ScenarioProjector:
    """Projects wear scenarios with different rate multipliers."""

    # Scenario multipliers
    BASELINE_MULTIPLIER = 1.0
    PESSIMISTIC_MULTIPLIER = 1.25  # 25% faster wear
    OPTIMISTIC_MULTIPLIER = 0.75  # 25% slower wear

    def __init__(
        self,
        critical_threshold_um: float = 200.0,
        projection_interval_hours: float = 1.0,
    ):
        """
        Initialize scenario projector.

        Args:
            critical_threshold_um: Critical wear threshold
            projection_interval_hours: Time interval for projection points
        """
        self.critical_threshold_um = critical_threshold_um
        self.projection_interval_hours = projection_interval_hours

    def project_scenarios(
        self,
        current_wear_um: float,
        wear_rate_um_per_hour: float,
        current_time: datetime,
    ) -> ScenarioProjection:
        """
        Generate 3-scenario projection.

        Args:
            current_wear_um: Current wear measurement (µm)
            wear_rate_um_per_hour: Current wear rate (µm/hour)
            current_time: Current timestamp

        Returns:
            Dictionary with baseline, pessimistic, and optimistic scenarios
        """
        baseline = self._calculate_scenario(
            current_wear_um,
            wear_rate_um_per_hour,
            self.BASELINE_MULTIPLIER,
            current_time,
        )

        pessimistic = self._calculate_scenario(
            current_wear_um,
            wear_rate_um_per_hour,
            self.PESSIMISTIC_MULTIPLIER,
            current_time,
        )

        optimistic = self._calculate_scenario(
            current_wear_um,
            wear_rate_um_per_hour,
            self.OPTIMISTIC_MULTIPLIER,
            current_time,
        )

        # Generate projection points for baseline scenario
        projection_points = self._generate_projection_points(
            current_wear_um,
            wear_rate_um_per_hour * self.BASELINE_MULTIPLIER,
            current_time,
            baseline["hours"],
        )

        logger.info(
            f"Generated scenarios: baseline={baseline['hours']:.1f}h, "
            f"pessimistic={pessimistic['hours']:.1f}h, "
            f"optimistic={optimistic['hours']:.1f}h"
        )

        return {
            "baseline": baseline,
            "pessimistic": pessimistic,
            "optimistic": optimistic,
            "projection_points": projection_points,
        }

    def _calculate_scenario(
        self,
        current_wear_um: float,
        wear_rate_um_per_hour: float,
        multiplier: float,
        current_time: datetime,
    ) -> ScenarioResult:
        """Calculate single scenario."""
        adjusted_rate = wear_rate_um_per_hour * multiplier

        # Calculate hours to critical
        if current_wear_um >= self.critical_threshold_um:
            hours = 0.0
        elif adjusted_rate <= 0.001:
            hours = 999.0
        else:
            remaining_wear = self.critical_threshold_um - current_wear_um
            hours = remaining_wear / adjusted_rate
            hours = min(hours, 999.0)

        # Calculate critical timestamp
        critical_at = current_time + timedelta(hours=hours)

        return {
            "hours": hours,
            "critical_at": critical_at.isoformat(),
            "wear_rate_multiplier": multiplier,
        }

    def _generate_projection_points(
        self,
        current_wear_um: float,
        wear_rate_um_per_hour: float,
        start_time: datetime,
        total_hours: float,
    ) -> list[ProjectionPoint]:
        """Generate projection timeline points."""
        points: list[ProjectionPoint] = []

        # Add current point
        points.append(
            {
                "timestamp": start_time.isoformat(),
                "wear_um": current_wear_um,
            }
        )

        # Generate intermediate points
        hours_elapsed = 0.0
        while hours_elapsed < total_hours:
            hours_elapsed += self.projection_interval_hours
            if hours_elapsed > total_hours:
                hours_elapsed = total_hours

            timestamp = start_time + timedelta(hours=hours_elapsed)
            wear_um = current_wear_um + (wear_rate_um_per_hour * hours_elapsed)
            wear_um = min(wear_um, self.critical_threshold_um)

            points.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "wear_um": wear_um,
                }
            )

        return points


def project_scenarios(
    current_wear_um: float,
    wear_rate_um_per_hour: float,
    current_time: datetime,
    critical_threshold_um: float = 200.0,
) -> ScenarioProjection:
    """
    Simple function to generate scenario projections.

    Args:
        current_wear_um: Current wear (µm)
        wear_rate_um_per_hour: Wear rate (µm/hour)
        current_time: Current timestamp
        critical_threshold_um: Critical threshold (µm)

    Returns:
        Dictionary with all three scenarios and projection points
    """
    projector = ScenarioProjector(critical_threshold_um)
    return projector.project_scenarios(current_wear_um, wear_rate_um_per_hour, current_time)
