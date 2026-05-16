# Phase B2 — Organization Management & Admin Panel

> Org CRUD, member management (invite/update/remove), admin panel endpoints, support tickets.

## Routers

### `routers/organizations.py`

```python
router = APIRouter(prefix="/api/organizations", tags=["organizations"])

GET /api/organizations
  Auth: Bearer token
  → Return list of orgs the current user is a member of
  → Each org: id, name, slug, logo_url, plan, role, member_count

POST /api/organizations/switch
  Auth: Bearer token
  Body: { org_id }
  → Validate user is member of org
  → Return org details + user's role in that org

GET /api/organizations/{org_id}
  Auth: Bearer token + org member
  → Org details (name, plan, settings, created_at, member_count)

PATCH /api/organizations/{org_id}
  Auth: Bearer token + Manager role
  Body: { name?, logo_url?, settings? }
  → Update org fields
```

### `routers/members.py`

```python
router = APIRouter(prefix="/api/organizations/{org_id}/members", tags=["members"])

GET /api/organizations/{org_id}/members
  Auth: Manager role in org
  → List all members: user_id, full_name, email, role, status, joined_at, last_active

POST /api/organizations/{org_id}/members/invite
  Auth: Manager role
  Body: { email, role }
  → Create org_members row with status='invited', invited_email=email
  → (Future: send invitation email via Supabase/PUQ AI)
  → Return invitation record

PATCH /api/organizations/{org_id}/members/{user_id}
  Auth: Manager role
  Body: { role }
  → Update member's role
  → Manager cannot demote themselves if they're the only manager

DELETE /api/organizations/{org_id}/members/{user_id}
  Auth: Manager role
  → Remove member (soft delete: set status='disabled' or hard delete)
  → Cannot remove the last manager
```

### `routers/admin.py`

```python
router = APIRouter(prefix="/api/admin", tags=["admin"])
# All endpoints require: Depends(require_platform_admin())

GET /api/admin/stats
  → total_orgs, total_users, active_orgs, tickets_open, total_anomalies_detected

GET /api/admin/organizations
  Query: page, limit, search, plan
  → Paginated list of all organizations with member_count, status

POST /api/admin/organizations
  Body: { name, slug, plan, manager_email }
  → Create org + invite initial manager
  → Return created org

GET /api/admin/organizations/{org_id}
  → Org details + member list + usage stats (anomalies count, predictions count)
  → Admin sees metadata ONLY, not factory data

GET /api/admin/users
  Query: page, limit, search, role
  → All platform users with their org memberships

GET /api/admin/support-tickets
  Query: status (open, in_progress, resolved, closed)
  → List support tickets

POST /api/admin/support-tickets/{ticket_id}/resolve
  Body: { resolution }
  → Mark ticket resolved
```

### Support Tickets Table (`005_auth_tables.sql`)

```sql
CREATE TABLE IF NOT EXISTS support_tickets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id),
    user_id         UUID NOT NULL,
    subject         TEXT NOT NULL,
    description     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    resolution      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    resolved_at     TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_org_id ON support_tickets(org_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
```

### `services/org_service.py`

- `create_organization(name, slug, plan)` → insert into organizations
- `get_user_organizations(user_id)` → join org_members + organizations
- `get_org_details(org_id)` → org + member count
- `update_organization(org_id, data)` → update org fields
- `add_member(org_id, user_id, role)` → insert org_members
- `invite_member(org_id, email, role)` → create invited member row
- `update_member_role(org_id, user_id, new_role)` → update role
- `remove_member(org_id, user_id)` → delete/disable member
- `get_org_members(org_id)` → list members with profiles
- `is_sole_manager(org_id, user_id)` → check if last manager (prevent removal)

## Deliverables

- [ ] `routers/organizations.py` — org list, switch, details, update
- [ ] `routers/members.py` — invite, list, update role, remove
- [ ] `routers/admin.py` — platform admin CRUD, stats, tickets
- [ ] `services/org_service.py` — org + member business logic
- [ ] `db/migrations/005_auth_tables.sql` — support_tickets table
- [ ] `main.py` updated with new routers
- [ ] Org switching works (validates membership, returns role)
- [ ] Member invite/role-change/removal works
- [ ] Admin endpoints require platform admin check
