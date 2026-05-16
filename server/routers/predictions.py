"""Predictions router for wear prediction API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from supabase import Client

from db.client import get_supabase_client
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


# Response models
class ScenarioResult(BaseModel):
    """Single scenario result."""

    hours: float
    critical_at: str
    wear_rate_multiplier: float


class ProjectionPoint(BaseModel):
    """Single projection point."""

    timestamp: str
    wear_um: float


class Scenarios(BaseModel):
    """All three scenarios."""

    baseline: ScenarioResult
    pessimistic: ScenarioResult
    optimistic: ScenarioResult


class PredictionResponse(BaseModel):
    """Prediction response for a single machine."""

    machine_id: str
    current_wear_um: float
    critical_threshold_um: float
    wear_rate_um_per_hour: float
    hours_to_critical: float
    confidence: str
    trend: str
    scenarios: Scenarios
    projection_points: list[ProjectionPoint]
    last_check_at: str
    status: str


class MachineOverview(BaseModel):
    """Overview of a single machine."""

    machine_id: str
    status: str
    hours_to_critical: float = Field(default=0.0)
    current_wear_um: float = Field(default=0.0)
    confidence: str = Field(default="unknown")
    trend: str = Field(default="unknown")
    error: str | None = Field(default=None)


class FactoryOverviewResponse(BaseModel):
    """Factory overview response."""

    machines: list[MachineOverview]


# Dependency
def get_prediction_service(
    supabase: Client = Depends(get_supabase_client),
) -> PredictionService:
    """Get prediction service instance."""
    return PredictionService(supabase)


@router.get("/{machine_id}", response_model=PredictionResponse)
async def get_prediction(
    machine_id: str,
    service: PredictionService = Depends(get_prediction_service),
) -> Any:
    """
    Get wear prediction for a specific machine.

    Args:
        machine_id: Machine/set identifier
        service: Prediction service instance

    Returns:
        Prediction data with scenarios and projections
    """
    try:
        result = await service.get_prediction(machine_id)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prediction for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/factory/overview", response_model=FactoryOverviewResponse)
async def get_factory_overview(
    service: PredictionService = Depends(get_prediction_service),
) -> Any:
    """
    Get overview of all machines in factory.

    Returns:
        List of machines with their status and key metrics
    """
    try:
        result = await service.get_factory_overview()
        return result

    except Exception as e:
        logger.error(f"Error getting factory overview: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/recalculate/{machine_id}", response_model=PredictionResponse)
async def recalculate_prediction(
    machine_id: str,
    service: PredictionService = Depends(get_prediction_service),
) -> Any:
    """
    Manually trigger recalculation of prediction for a machine.

    Args:
        machine_id: Machine identifier
        service: Prediction service instance

    Returns:
        Updated prediction data
    """
    try:
        result = await service.recalculate_prediction(machine_id)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating prediction for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
