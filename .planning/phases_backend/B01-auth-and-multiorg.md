# Phase B1 — Authentication, Multi-Org & RBAC

> Set up Supabase Auth integration, JWT verification, multi-organization tables, role-based access control, and org-scoping middleware. This is the backbone of the B2B SaaS architecture.

## Context

The server already has a working Supabase client (`db/client.py`) using the **service key**. For auth, we need a second client path that verifies **user JWTs** issued by Supabase Auth. All new auth/org infrastructure is ADDED — no existing code is changed.

---

## Task

### 1. New Dependencies

Add to `pyproject.toml`:
```
pyjwt>=2.8.0          # JWT decode/verify
cryptography>=41.0.0   # For RS256 verification
```

### 2. Config Updates (`db/config.py`)

Add new fields to the existing `Settings` class (do NOT remove existing fields):

```python
# Auth
supabase_jwt_secret: str = ""          # Supabase JWT secret for verification
supabase_anon_key: str = ""            # Anon key for client-side auth operations

# Admin
admin_emails: str = ""                 # Comma-separated admin emails (e.g., "admin@yefai.io")
```

### 3. Database Migration: `004_multi_org.sql`

```sql
-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    logo_url        TEXT,
    plan            TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    settings        JSONB DEFAULT '{}'::jsonb,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Organization members (links Supabase Auth users to orgs with roles)
CREATE TABLE IF NOT EXISTS org_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,  -- References auth.users(id) from Supabase Auth
    role            TEXT NOT NULL DEFAULT 'viewer'
                    CHECK (role IN ('admin', 'manager', 'operator', 'technician', 'procurement', 'viewer')),
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'invited', 'disabled')),
    invited_email   TEXT,           -- For pending invitations
    joined_at       TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(org_id, user_id)
);

-- User profiles (extends Supabase Auth users with app-specific data)
CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY,  -- Same as auth.users(id)
    full_name       TEXT,
    avatar_url      TEXT,
    phone           TEXT,
    preferences     JSONB DEFAULT '{}'::jsonb,
    is_platform_admin BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_org_members_org_id ON org_members(org_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON org_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_role ON org_members(role);
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_platform_admin);

-- Add org_id to existing domain tables (nullable for backward compatibility)
ALTER TABLE sets ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE images ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS machine_id TEXT;  -- Currently missing, prediction_service needs it
ALTER TABLE spare_parts_catalog ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE inventory_snapshots ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE part_tickets ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);

-- Indexes for org_id on existing tables
CREATE INDEX IF NOT EXISTS idx_sets_org_id ON sets(org_id);
CREATE INDEX IF NOT EXISTS idx_images_org_id ON images(org_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_org_id ON anomalies(org_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_machine_id ON anomalies(machine_id);
CREATE INDEX IF NOT EXISTS idx_spare_parts_org_id ON spare_parts_catalog(org_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_org_id ON suppliers(org_id);
CREATE INDEX IF NOT EXISTS idx_inventory_org_id ON inventory_snapshots(org_id);
CREATE INDEX IF NOT EXISTS idx_tickets_org_id ON part_tickets(org_id);
CREATE INDEX IF NOT EXISTS idx_po_org_id ON purchase_orders(org_id);
```

### 4. Auth Module (`server/auth/`)

#### `auth/models.py`

```python
from enum import Enum
from pydantic import BaseModel

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    TECHNICIAN = "technician"
    PROCUREMENT = "procurement"
    VIEWER = "viewer"

class TokenPayload(BaseModel):
    sub: str           # user_id (UUID)
    email: str
    exp: int

class CurrentUser(BaseModel):
    id: str
    email: str
    is_platform_admin: bool = False

class OrgContext(BaseModel):
    org_id: str
    role: Role
    user: CurrentUser
```

#### `auth/permissions.py`

```python
from enum import Enum
from auth.models import Role

class Permission(str, Enum):
    VIEW_DASHBOARD = "view:dashboard"
    VIEW_ANOMALIES = "view:anomalies"
    MARK_ANOMALY_REVIEWED = "action:mark_anomaly_reviewed"
    VIEW_PREDICTIONS = "view:predictions"
    RECALCULATE_PREDICTION = "action:recalculate_prediction"
    VIEW_SPARE_PARTS = "view:spare_parts"
    APPROVE_PO = "action:approve_po"
    MANAGE_SUPPLIERS = "action:manage_suppliers"
    VIEW_CHAT = "view:chat"
    VIEW_NOTIFICATIONS = "view:notifications"
    TRIGGER_NOTIFICATION = "action:trigger_notification"
    MANAGE_MEMBERS = "manage:members"
    MANAGE_ORG_SETTINGS = "manage:org_settings"
    ADMIN_MANAGE_ORGS = "admin:manage_orgs"
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_VIEW_TICKETS = "admin:view_tickets"

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {Permission.ADMIN_MANAGE_ORGS, Permission.ADMIN_MANAGE_USERS, Permission.ADMIN_VIEW_TICKETS},
    Role.MANAGER: {ALL org permissions},
    Role.OPERATOR: {Permission.VIEW_DASHBOARD, Permission.VIEW_ANOMALIES, Permission.VIEW_PREDICTIONS, Permission.VIEW_CHAT, Permission.VIEW_NOTIFICATIONS},
    Role.TECHNICIAN: {operator + Permission.MARK_ANOMALY_REVIEWED, Permission.RECALCULATE_PREDICTION, Permission.VIEW_SPARE_PARTS},
    Role.PROCUREMENT: {Permission.VIEW_SPARE_PARTS, Permission.APPROVE_PO, Permission.MANAGE_SUPPLIERS, Permission.VIEW_NOTIFICATIONS},
    Role.VIEWER: {all view permissions, no actions},
}

def has_permission(role: Role, permission: Permission) -> bool: ...
def check_permission(role: Role, permission: Permission) -> None:  # raises HTTPException 403
```

#### `auth/dependencies.py`

FastAPI dependencies for injection:

```python
from fastapi import Depends, Header, HTTPException
from supabase import Client
import jwt

async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> CurrentUser:
    """
    Verify Supabase JWT from Authorization header.
    Extract user_id, email. Check profiles table for is_platform_admin.
    Raises 401 if invalid/expired.
    """

async def get_org_context(
    current_user: CurrentUser = Depends(get_current_user),
    x_organization_id: str = Header(..., alias="X-Organization-Id"),
) -> OrgContext:
    """
    Validate user is a member of the specified org.
    Return OrgContext with org_id, role, and user.
    Raises 403 if not a member.
    """

def require_role(*roles: Role):
    """
    Dependency factory: returns a dependency that checks the user's org role.
    Usage: Depends(require_role(Role.MANAGER, Role.PROCUREMENT))
    """

def require_permission(permission: Permission):
    """
    Dependency factory: checks if user's role has the given permission.
    Usage: Depends(require_permission(Permission.APPROVE_PO))
    """

def require_platform_admin():
    """
    Dependency: checks if user.is_platform_admin is True.
    Raises 403 otherwise.
    """
```

### 5. Org Context Middleware (`middleware/org_context.py`)

Optional middleware that extracts `X-Organization-Id` and makes it available:
- Reads header from request
- Validates format (UUID)
- Stores in request state for downstream access
- Does NOT enforce auth (that's done by dependencies)

### 6. Auth Router (`routers/auth.py`)

```python
router = APIRouter(prefix="/api/auth", tags=["auth"])

POST /api/auth/register
  Body: { name, email, password }
  → Create user via Supabase Auth, create profile row
  → Return { user, token }

POST /api/auth/login
  Body: { email, password }
  → Authenticate via Supabase Auth
  → Fetch user's org memberships
  → Return { user, token, organizations: [{ org_id, org_name, role }] }

POST /api/auth/logout
  → Invalidate session (Supabase handles this)

GET /api/auth/me
  Auth: Bearer token
  → Return current user + org memberships

POST /api/auth/forgot-password
  Body: { email }
  → Trigger Supabase password reset email

POST /api/auth/reset-password
  Body: { token, new_password }
  → Reset via Supabase Auth

POST /api/auth/accept-invite
  Body: { invite_token }
  → Activate org_members row, create profile if needed
  → Return { user, org, role }

POST /api/auth/refresh
  Body: { refresh_token }
  → Refresh Supabase session
```

### 7. Auth Service (`services/auth_service.py`)

Wraps Supabase Auth operations:
- `sign_up(email, password, name)` → Supabase `auth.sign_up()` + create profile
- `sign_in(email, password)` → Supabase `auth.sign_in_with_password()`
- `get_user_by_id(user_id)` → profiles table lookup
- `get_user_orgs(user_id)` → join org_members + organizations
- `verify_token(jwt_token)` → decode + verify JWT
- `is_platform_admin(user_id)` → check profiles.is_platform_admin
- Uses the **service key client** for admin operations (user lookup, etc.)

### 8. Update `main.py`

Add new router (without removing existing ones):
```python
from routers.auth import router as auth_router
app.include_router(auth_router)
```

Add CORS origin for frontend dev server if needed.

## Deliverables

- [ ] `db/migrations/004_multi_org.sql` — orgs, members, profiles tables + org_id columns on existing tables
- [ ] `auth/models.py` — Role enum, CurrentUser, OrgContext, TokenPayload
- [ ] `auth/permissions.py` — Permission enum, ROLE_PERMISSIONS mapping, check functions
- [ ] `auth/dependencies.py` — `get_current_user`, `get_org_context`, `require_role`, `require_permission`, `require_platform_admin`
- [ ] `middleware/org_context.py` — X-Organization-Id extraction
- [ ] `routers/auth.py` — register, login, logout, me, forgot-password, reset, accept-invite, refresh
- [ ] `services/auth_service.py` — Supabase Auth wrapper
- [ ] `main.py` updated with auth router
- [ ] `db/config.py` updated with new env vars
- [ ] Migration applied successfully
- [ ] Login/register flow works end-to-end
