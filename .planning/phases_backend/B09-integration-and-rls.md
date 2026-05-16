# Phase B9 — Integration, RLS & Hardening

> Final phase: Row Level Security policies, app lifespan management, error handling, integration tests, and production readiness.

## Task

### 1. Row Level Security (RLS) Policies (`db/migrations/006_rls_policies.sql`)

Enable RLS on all tables with org_id to ensure data isolation at the database level:

```sql
-- Enable RLS on org-scoped tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE spare_parts_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE part_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (our backend uses service key)
-- These policies are for Supabase client-side access (future)
-- and as defense-in-depth

-- Profile: users can see their own profile
CREATE POLICY profiles_own ON profiles FOR ALL
    USING (id = auth.uid());

-- Org members: users can see members of orgs they belong to
CREATE POLICY org_members_own_orgs ON org_members FOR SELECT
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Domain tables: org members can access their org's data
CREATE POLICY sets_org_access ON sets FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Repeat for: images, anomalies, spare_parts_catalog, suppliers,
-- inventory_snapshots, part_tickets, purchase_orders, chat_sessions,
-- notification_channels, notification_logs, files

-- Chat: users can only see their own sessions
CREATE POLICY chat_sessions_own ON chat_sessions FOR ALL
    USING (user_id = auth.uid() AND org_id IN (
        SELECT org_id FROM org_members WHERE user_id = auth.uid()
    ));

-- Support tickets: users can see their org's tickets
CREATE POLICY support_tickets_org ON support_tickets FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));
```

**Note:** Since our backend uses the **service key** (which bypasses RLS), these policies are defense-in-depth and prepare for future client-side Supabase access.

### 2. App Lifespan (`main.py`)

Add proper startup/shutdown lifecycle:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Yefai API starting up...")
    # Test database connection
    test_connection()
    # Pre-load embedding model (optional, for faster first request)
    # Verify Supabase Auth config

    yield

    # Shutdown
    logger.info("Yefai API shutting down...")
    # Clean up resources

app = FastAPI(
    title="Yefai API",
    description="Predictive Maintenance Platform — Backend",
    version="0.2.0",
    lifespan=lifespan,
)
```

### 3. Error Handling

Create standardized error responses:

```python
# server/errors.py

class YefaiError(HTTPException):
    """Base exception for Yefai API."""

class NotFoundError(YefaiError):      # 404
class ForbiddenError(YefaiError):     # 403
class UnauthorizedError(YefaiError):  # 401
class ConflictError(YefaiError):      # 409 (e.g., duplicate member)
class ValidationError(YefaiError):    # 422

# Global exception handler in main.py
@app.exception_handler(YefaiError)
async def yefai_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "path": str(request.url)
        }
    )
```

### 4. Request Logging Middleware

```python
# middleware/logging.py

class RequestLoggingMiddleware:
    """Log all requests with timing, user_id, org_id."""

    async def dispatch(self, request, call_next):
        start_time = time.time()
        # Extract user/org from headers (if present)
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.3f}s "
            f"org={request.headers.get('X-Organization-Id', '-')}"
        )
        return response
```

### 5. Rate Limiting (Optional)

Add basic rate limiting for auth endpoints to prevent brute force:

```python
# Simple in-memory rate limiter for login/register
# Production: use Redis-based limiter

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
# Apply to: POST /auth/login (5/minute), POST /auth/register (3/minute)
```

### 6. Integration Tests

Create test files in `tests/`:

```
tests/
├── conftest.py           # Fixtures: test client, mock supabase, test user
├── test_auth.py          # Register, login, token verification, role checks
├── test_organizations.py # Org CRUD, member management
├── test_predictions.py   # Prediction endpoints with auth
├── test_spare_parts.py   # Crisis, POs, suppliers
├── test_chat.py          # Chat sessions, messages
├── test_notifications.py # Notification dispatch
├── test_dashboard.py     # Aggregation endpoints
├── test_permissions.py   # RBAC checks (each role can/can't access)
└── test_files.py         # File upload/download
```

Key test scenarios:
- Unauthenticated request → 401
- Wrong role → 403
- Org member accessing different org → 403
- Valid request → correct data returned
- Admin can manage orgs but not see org data
- Manager can manage members
- Viewer sees read-only, no action endpoints

### 7. OpenAPI Documentation

Ensure all endpoints have proper:
- Summary and description
- Request/response models (Pydantic)
- Auth requirements documented in description
- Example responses

The Swagger UI at `/docs` should be a complete API reference.

### 8. Migration Runner Update

Update `db/client.py` `run_migration_sql()` to track applied migrations:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,
    applied_at  TIMESTAMPTZ DEFAULT now()
);
```

The runner checks if migration is already applied before executing.

### 9. CORS Update

Update CORS for production:
```python
allow_origins=[
    "http://localhost:3000",     # Local dev
    "tauri://localhost",          # Tauri desktop app
    "https://yefai.io",          # Production
    "https://app.yefai.io",      # Production app
]
```

### 10. Final Checklist

- [ ] All tables have RLS enabled
- [ ] Lifespan manages startup/shutdown
- [ ] Standardized error responses
- [ ] Request logging middleware
- [ ] Rate limiting on auth endpoints
- [ ] Integration tests for all routers
- [ ] RBAC tests (6 roles × each endpoint)
- [ ] OpenAPI documentation complete
- [ ] Migration runner tracks versions
- [ ] CORS configured for production
- [ ] No `print()` statements (all `logger.*`)
- [ ] All secrets loaded from env vars (no hardcoded values)
- [ ] `pyproject.toml` dependencies up to date

## Deliverables

- [ ] `db/migrations/006_rls_policies.sql` — RLS policies for all tables
- [ ] `main.py` — lifespan, error handlers, middleware, CORS update
- [ ] `errors.py` — standardized error classes
- [ ] `middleware/logging.py` — request logging
- [ ] Integration tests for all major flows
- [ ] RBAC permission tests
- [ ] OpenAPI docs complete
- [ ] Migration runner with version tracking
- [ ] Production readiness checklist passed
