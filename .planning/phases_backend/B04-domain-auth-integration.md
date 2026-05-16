# Phase B4 — Domain Auth Integration

> Add auth dependencies and org-scoping to ALL existing routers. After this phase, every endpoint requires authentication and returns org-scoped data.

## Key Rule

Do NOT rewrite existing router logic. Only ADD auth dependencies to existing endpoint functions and add org_id filtering to service queries where needed.

## Changes

### 1. `routers/predictions.py` — Add Auth

```python
# BEFORE:
@router.get("/{machine_id}", response_model=PredictionResponse)
async def get_prediction(
    machine_id: str,
    service: PredictionService = Depends(get_prediction_service),
) -> Any:

# AFTER:
@router.get("/{machine_id}", response_model=PredictionResponse)
async def get_prediction(
    machine_id: str,
    org: OrgContext = Depends(get_org_context),          # ADD
    _: None = Depends(require_permission(Permission.VIEW_PREDICTIONS)),  # ADD
    service: PredictionService = Depends(get_prediction_service),
) -> Any:
    # Pass org_id to service for scoped query
```

Apply same pattern to:
- `get_factory_overview` — add auth + org context
- `recalculate_prediction` — add auth + require RECALCULATE_PREDICTION permission

### 2. `routers/anomalib.py` — Add Auth

- `train_anomalib` → require Manager role (training is a privileged operation)
- `get_training_status` → require authenticated user
- `predict_anomaly` → require VIEW_ANOMALIES permission
- `get_model_info` → require authenticated user

### 3. `routers/embeddings.py` — Add Auth

- `search_embeddings` → require authenticated user + org context
- Add org_id to search queries (filter results by org)

### 4. `routers/novavision.py` — Add Auth

- All deploy/delete endpoints → require Manager role
- Inference/health/models endpoints → require authenticated user

### 5. `services/prediction_service.py` — Add Org Scoping

Update queries to filter by org_id:
```python
# BEFORE:
response = self.supabase.table("anomalies").select("*").eq("machine_id", machine_id).execute()

# AFTER:
response = (
    self.supabase.table("anomalies")
    .select("*")
    .eq("machine_id", machine_id)
    .eq("org_id", org_id)  # ADD org scoping
    .execute()
)
```

Pass `org_id` parameter through PredictionService methods.
The `get_factory_overview` should only show machines belonging to the active org.

### 6. `services/embedding_service.py` — Add Org Scoping

Add org_id filter to pgvector search queries.

### 7. Backward Compatibility

For the transition period:
- If `org_id` is None in existing data, queries should still work (use `is(org_id, null)` or skip filter)
- New data should always have org_id set
- Existing endpoints that don't have auth yet should continue working during development (graceful degradation)

### 8. Optional Auth Wrapper

Create a helper for gradual migration:

```python
def optional_auth():
    """Returns CurrentUser if token present, None otherwise.
    Use during migration when some endpoints are being auth-hardened gradually."""
```

## Deliverables

- [ ] `predictions.py` — all 3 endpoints have auth + org scoping
- [ ] `anomalib.py` — all 4 endpoints have auth (training restricted to Manager)
- [ ] `embeddings.py` — search endpoint has auth + org scoping
- [ ] `novavision.py` — all 7 endpoints have auth (deploy/delete restricted to Manager)
- [ ] `prediction_service.py` — queries filter by org_id
- [ ] `embedding_service.py` — search filters by org_id
- [ ] All endpoints return 401 for unauthenticated requests
- [ ] All endpoints return 403 for insufficient role/permission
- [ ] Existing functionality unchanged when valid auth provided
