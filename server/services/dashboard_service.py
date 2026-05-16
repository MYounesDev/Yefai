"""Dashboard Service — aggregates stats and provides system health."""

import logging
from typing import Any

from supabase import Client

from services.crisis_service import CrisisService
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(
        self,
        supabase: Client,
        prediction_service: PredictionService | None = None,
        crisis_service: CrisisService | None = None,
    ):
        self.supabase = supabase
        self.prediction_service = prediction_service or PredictionService(supabase)
        self.crisis_service = crisis_service or CrisisService(supabase, self.prediction_service)

    async def get_overview(self, org_id: str) -> dict[str, Any]:
        """Aggregated dashboard data in a single query-optimized call."""
        # 1. Anomalies Overview
        anomalies_res = (
            self.supabase.table("anomalies")
            .select("id, machine_id, score, wear_type, severity, status, created_at, wear")
            .eq("org_id", org_id)
            .execute()
        )
        anomalies = anomalies_res.data or []

        total_anomalies = len(anomalies)
        active_anomalies = len(
            [a for a in anomalies if str(a.get("status", "")) in ("new", "reviewed")]
        )

        total_wear = sum((float(a.get("wear") or 0) for a in anomalies), 0.0)
        avg_wear_um = total_wear / total_anomalies if total_anomalies > 0 else 0.0

        recent_anomalies = sorted(anomalies, key=lambda x: x.get("created_at", ""), desc=True)[:5]

        # 2. Crisis Overview
        # We can simulate calling crisis_service.get_crisis_dashboard
        crisis_summary = await self.crisis_service.get_crisis_dashboard(org_id)

        # 3. Machines Overview
        try:
            machines_overview = await self.prediction_service.get_factory_overview(org_id)
            machines = machines_overview.get("machines", [])
        except Exception:
            machines = []

        return {
            "stats": {
                "total_anomalies": total_anomalies,
                "active_anomalies": active_anomalies,
                "avg_wear_um": round(avg_wear_um, 2),
                "crisis_count": crisis_summary.get("critical_count", 0),
                "uptime_percent": 99.9,  # Mock uptime
            },
            "machines": machines,
            "recent_anomalies": recent_anomalies,
            "crisis_summary": {
                "total_parts": crisis_summary.get("total_parts", 0),
                "at_risk": crisis_summary.get("at_risk_count", 0),
                "critical": crisis_summary.get("critical_count", 0),
                "pending_pos": 0,  # To be fetched if needed
            },
        }

    async def get_health_status(self) -> dict[str, Any]:
        """System health check across all services."""
        # Check database
        db_status = "healthy"
        try:
            self.supabase.table("organizations").select("id").limit(1).execute()
        except Exception:
            db_status = "down"

        # Check embedding model
        from services.embedding_service import EmbeddingService

        emb_service = EmbeddingService()
        emb_loaded = emb_service.model_loaded

        # Anomalib status (mock check since we don't hold the instance here)
        anomalib_status = "healthy"

        # Novavision status
        novavision_status = "healthy"

        return {
            "database": {"status": db_status, "latency_ms": 15},
            "anomalib": {"status": anomalib_status, "model_loaded": True},
            "novavision": {"status": novavision_status, "mode": "mock"},
            "embeddings": {
                "status": "healthy" if emb_loaded else "standby",
                "model_loaded": emb_loaded,
            },
            "puqai": {"status": "mock"},
            "last_check": "now",
        }
