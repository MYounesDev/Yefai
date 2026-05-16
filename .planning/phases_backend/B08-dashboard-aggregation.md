# Phase B8 — Dashboard Aggregation

> Create a dedicated dashboard router that aggregates stats from all domain services into a single optimized response for the frontend dashboard.

## Context

The frontend dashboard (Phase 3 frontend) needs a single API call to get:
- Total anomalies, active anomalies, average wear, crisis count
- Machine status grid (8 machines overview)
- Recent anomalies feed
- System health status

Currently, the frontend would need to call multiple endpoints. This phase creates optimized aggregation endpoints.

## Task

### 1. Dashboard Service (`services/dashboard_service.py`)

```python
class DashboardService:
    def __init__(
        self, supabase: Client,
        prediction_service: PredictionService,
        crisis_service: CrisisService
    ):
        self.supabase = supabase
        self.prediction_service = prediction_service
        self.crisis_service = crisis_service

    async def get_overview(self, org_id: str) -> dict:
        """
        Aggregated dashboard data in a single query-optimized call.

        Returns:
        {
            "stats": {
                "total_anomalies": int,
                "active_anomalies": int,
                "avg_wear_um": float,
                "crisis_count": int,
                "uptime_percent": float
            },
            "machines": [  # from factory overview, org-scoped
                {
                    "machine_id": str,
                    "status": "green|yellow|red",
                    "current_wear_um": float,
                    "hours_to_critical": float,
                    "trend": str
                }
            ],
            "recent_anomalies": [  # last 5
                {
                    "id": int,
                    "machine_id": str,
                    "score": float,
                    "wear_type": str,
                    "severity": str,
                    "detected_at": str
                }
            ],
            "crisis_summary": {
                "total_parts": int,
                "at_risk": int,
                "critical": int,
                "pending_pos": int
            }
        }
        """

    async def get_health_status(self) -> dict:
        """
        System health check across all services.

        Returns:
        {
            "database": { "status": "healthy|degraded|down", "latency_ms": int },
            "anomalib": { "status": str, "model_loaded": bool },
            "novavision": { "status": str, "mode": "mock|live" },
            "embeddings": { "status": str, "model_loaded": bool },
            "puqai": { "status": str },
            "last_check": str (ISO timestamp)
        }
        """
```

### 2. Dashboard Router (`routers/dashboard.py`)

```python
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

GET /api/dashboard/overview
  Auth: VIEW_DASHBOARD permission
  → Aggregated dashboard data (org-scoped)
  → Single call replaces multiple frontend API calls

GET /api/dashboard/health
  Auth: authenticated user (any role)
  → System health status across all services
```

### 3. Anomaly List Endpoint

The anomalib router currently has predict/train but not a list endpoint for browsing anomalies. Add:

```python
# In routers/anomalib.py or a new routers/anomalies.py

GET /api/anomalies
  Auth: VIEW_ANOMALIES permission
  Query: severity?, wear_type?, machine_id?, page, limit, sort_by, sort_order, date_from?, date_to?
  → Paginated anomaly list (org-scoped)

GET /api/anomalies/{id}
  Auth: VIEW_ANOMALIES permission
  → Full anomaly detail with linked image, prediction data

PATCH /api/anomalies/{id}/status
  Auth: MARK_ANOMALY_REVIEWED permission (Manager/Technician)
  Body: { status: "reviewed" | "resolved", notes?: string }
  → Update anomaly status
```

Add columns if needed:
```sql
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'new'
    CHECK (status IN ('new', 'reviewed', 'resolved'));
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS severity TEXT;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS reviewed_by UUID;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;
```

### 4. Health Endpoint Migration (✅ Approved)

Move the existing `/health` from `main.py` to `routers/health.py`:
- Basic `/health` endpoint stays **public** (no auth) for uptime monitoring tools
- Detailed `/api/dashboard/health` is auth-protected and shows per-service status
- Remove the health endpoint code from `main.py` after migration
- Add `routers/health.py` to `main.py` via `include_router()`

## Deliverables

- [ ] `services/dashboard_service.py` — stats aggregation, health check
- [ ] `routers/dashboard.py` — overview + health endpoints
- [ ] Anomaly list/detail/status-update endpoints
- [ ] Migration for anomaly status/severity/notes columns
- [ ] Dashboard overview optimized for single-call from frontend
- [ ] Health check covers all services
- [ ] All endpoints auth-protected and org-scoped
- [ ] `main.py` updated with new routers
