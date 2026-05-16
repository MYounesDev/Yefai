"""Prediction service for wear prediction and projection.

## Phase 3B Integration Interface

This service provides the prediction interface that Phase 3B's crisis_service.py will consume.

### Usage Example for crisis_service.py:

```python
from services.prediction_service import PredictionService

# In crisis_service.py:
async def calculate_crisis_score(machine_id: str, spare_part_id: str):
    # Get prediction data
    prediction = await prediction_service.get_prediction(machine_id)

    # Extract key metrics
    hours_to_critical = prediction["hours_to_critical"]
    confidence = prediction["confidence"]
    trend = prediction["trend"]

    # Get spare part lead time from catalog
    spare_part = get_spare_part(spare_part_id)
    lead_time_hours = spare_part["lead_time_days"] * 24

    # Calculate crisis score component
    if hours_to_critical < lead_time_hours:
        crisis_score += 30  # Lead time won't meet critical threshold

    if trend == "accelerating":
        crisis_score += 15  # Wear is accelerating

    if confidence == "low":
        crisis_score += 10  # Low confidence adds uncertainty risk

    return crisis_score
```

### Response Format:

The `get_prediction()` method returns:
- `machine_id`: str - Machine identifier
- `current_wear_um`: float - Current wear in micrometers
- `critical_threshold_um`: float - Critical threshold (default: 200µm)
- `wear_rate_um_per_hour`: float - Calculated wear rate
- `hours_to_critical`: float - Hours until critical threshold
- `confidence`: str - "high" | "medium" | "low" | "insufficient_data" | "critical"
- `trend`: str - "accelerating" | "stable" | "decelerating" | "insufficient_data"
- `scenarios`: dict - Baseline, pessimistic, optimistic projections
- `projection_points`: list - Timeline points for graphing
- `last_check_at`: str - ISO timestamp of last check
- `status`: str - "green" | "yellow" | "red" | "unknown"

### Status Levels:
- **green**: > 72 hours to critical
- **yellow**: 24-72 hours to critical
- **red**: < 24 hours to critical or already critical
"""

import logging
from datetime import datetime
from typing import Literal

from supabase import Client

from ai.prediction.calibration import WearCalibrator
from ai.prediction.projection import CriticalThresholdProjector
from ai.prediction.scenarios import ScenarioProjector
from ai.prediction.trends import WearTrendAnalyzer
from ai.prediction.wear_rate import WearRateCalculator

logger = logging.getLogger(__name__)

StatusLevel = Literal["green", "yellow", "red", "unknown"]


class PredictionService:
    """Service for wear prediction and critical threshold projection."""

    def __init__(
        self,
        supabase_client: Client,
        critical_threshold_um: float = 200.0,
    ):
        """
        Initialize prediction service.

        Args:
            supabase_client: Supabase client instance
            critical_threshold_um: Critical wear threshold in micrometers
        """
        self.supabase = supabase_client
        self.critical_threshold_um = critical_threshold_um

        # Initialize components
        self.calibrator = WearCalibrator(linear_scale=200.0)
        self.wear_rate_calculator = WearRateCalculator(min_data_points=3)
        self.projector = CriticalThresholdProjector(critical_threshold_um)
        self.scenario_projector = ScenarioProjector(critical_threshold_um)
        self.trend_analyzer = WearTrendAnalyzer(min_periods=3)

    async def get_prediction(self, machine_id: str) -> dict:
        """
        Get wear prediction for a specific machine.

        Args:
            machine_id: Machine/set identifier

        Returns:
            Dictionary with prediction data including scenarios and projections
        """
        # Fetch anomaly data for this machine
        response = (
            self.supabase.table("anomalies")
            .select("*")
            .eq("machine_id", machine_id)
            .order("created_at", desc=False)
            .execute()
        )

        if not response.data:
            logger.warning(f"No anomaly data found for machine {machine_id}")
            return {
                "machine_id": machine_id,
                "error": "No data available",
                "status": "unknown",
            }

        anomalies: list[dict] = response.data  # type: ignore[assignment]

        # Get latest anomaly
        latest: dict = anomalies[-1]  # type: ignore[assignment]
        current_wear_um = float(latest.get("estimated_wear_um", 0.0))

        # Calculate wear rate from historical data
        timestamps = [
            datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")) for a in anomalies
        ]
        wear_values = [a.get("estimated_wear_um", 0.0) for a in anomalies]

        try:
            wear_rate_result = self.wear_rate_calculator.calculate_with_confidence(
                timestamps, wear_values
            )
            wear_rate_um_per_hour = wear_rate_result["wear_rate_um_per_hour"]
            r_squared = wear_rate_result["r_squared"]
            confidence = wear_rate_result["confidence"]
        except Exception as e:
            logger.error(f"Error calculating wear rate: {e}")
            wear_rate_um_per_hour = 0.0
            r_squared = 0.0
            confidence = "insufficient_data"

        # Project hours to critical
        projection_result = self.projector.project_hours_to_critical(
            current_wear_um,
            wear_rate_um_per_hour,
            r_squared,
            len(anomalies),
        )
        hours_to_critical = projection_result["hours_to_critical"]

        # Analyze trend
        trend_result = self.trend_analyzer.analyze_trend(timestamps, wear_values)
        trend = trend_result["trend"]

        # Generate scenarios
        current_time = timestamps[-1]
        scenarios = self.scenario_projector.project_scenarios(
            current_wear_um,
            wear_rate_um_per_hour,
            current_time,
        )

        # Determine status
        status = self._determine_status(hours_to_critical, current_wear_um)

        return {
            "machine_id": machine_id,
            "current_wear_um": current_wear_um,
            "critical_threshold_um": self.critical_threshold_um,
            "wear_rate_um_per_hour": wear_rate_um_per_hour,
            "hours_to_critical": hours_to_critical,
            "confidence": confidence,
            "trend": trend,
            "scenarios": scenarios,
            "projection_points": scenarios["projection_points"],
            "last_check_at": latest["created_at"],
            "status": status,
        }

    async def get_factory_overview(self) -> dict:
        """
        Get overview of all machines in factory.

        Returns:
            Dictionary with list of machines and their status
        """
        # Get all unique machine IDs
        response = self.supabase.table("anomalies").select("machine_id").execute()

        if not response.data:
            return {"machines": []}

        # Get unique machine IDs
        machine_ids = list({a["machine_id"] for a in response.data})

        # Get prediction for each machine
        machines = []
        for machine_id in machine_ids:
            try:
                prediction = await self.get_prediction(machine_id)
                machines.append(
                    {
                        "machine_id": machine_id,
                        "status": prediction.get("status", "unknown"),
                        "hours_to_critical": prediction.get("hours_to_critical", 0.0),
                        "current_wear_um": prediction.get("current_wear_um", 0.0),
                        "confidence": prediction.get("confidence", "unknown"),
                        "trend": prediction.get("trend", "unknown"),
                    }
                )
            except Exception as e:
                logger.error(f"Error getting prediction for {machine_id}: {e}")
                machines.append(
                    {
                        "machine_id": machine_id,
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {"machines": machines}

    async def recalculate_prediction(self, machine_id: str) -> dict:
        """
        Manually trigger recalculation of prediction.

        Args:
            machine_id: Machine identifier

        Returns:
            Updated prediction data
        """
        logger.info(f"Recalculating prediction for machine {machine_id}")
        return await self.get_prediction(machine_id)

    def _determine_status(self, hours_to_critical: float, current_wear_um: float) -> StatusLevel:
        """Determine status level based on hours to critical."""
        if current_wear_um >= self.critical_threshold_um or hours_to_critical <= 24:
            return "red"
        elif hours_to_critical <= 72:
            return "yellow"
        else:
            return "green"
