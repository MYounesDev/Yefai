-- Yefai Phase B1 — Multi-Organization & Auth Schema
-- Adds organizations, org_members, profiles tables
-- Adds org_id column to all existing domain tables
-- Adds machine_id column to anomalies (was missing, prediction_service needs it)

-- ============================================================
-- Multi-org core tables
-- ============================================================

CREATE TABLE IF NOT EXISTS organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    logo_url        TEXT,
    plan            TEXT NOT NULL DEFAULT 'free'
                    CHECK (plan IN ('free', 'pro', 'enterprise')),
    settings        JSONB DEFAULT '{
        "notification_channels": {"telegram": false, "email": true, "sms": false},
        "critical_threshold_hours": 24,
        "crisis_score_threshold": 70,
        "refresh_interval_seconds": 30
    }'::jsonb,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS org_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,
    role            TEXT NOT NULL DEFAULT 'viewer'
                    CHECK (role IN ('admin', 'manager', 'operator', 'technician', 'procurement', 'viewer')),
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'invited', 'disabled')),
    invited_email   TEXT,
    joined_at       TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(org_id, user_id)
);

CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY,
    full_name       TEXT,
    avatar_url      TEXT,
    phone           TEXT,
    preferences     JSONB DEFAULT '{}'::jsonb,
    is_platform_admin BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Indexes for new tables
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_org_members_org_id ON org_members(org_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON org_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_role ON org_members(role);
CREATE INDEX IF NOT EXISTS idx_org_members_status ON org_members(status);
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_plan ON organizations(plan);
CREATE INDEX IF NOT EXISTS idx_organizations_is_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_platform_admin);

-- ============================================================
-- Add org_id to existing domain tables (nullable for backward compat)
-- ============================================================

ALTER TABLE sets ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE images ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE spare_parts_catalog ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE inventory_snapshots ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE part_tickets ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);

-- Add machine_id to anomalies (prediction_service already queries this column)
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS machine_id TEXT;

-- ============================================================
-- Indexes for org_id on existing tables
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_sets_org_id ON sets(org_id);
CREATE INDEX IF NOT EXISTS idx_images_org_id ON images(org_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_org_id ON anomalies(org_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_machine_id ON anomalies(machine_id);
CREATE INDEX IF NOT EXISTS idx_spare_parts_org_id ON spare_parts_catalog(org_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_org_id ON suppliers(org_id);
CREATE INDEX IF NOT EXISTS idx_inventory_org_id ON inventory_snapshots(org_id);
CREATE INDEX IF NOT EXISTS idx_tickets_org_id ON part_tickets(org_id);
CREATE INDEX IF NOT EXISTS idx_po_org_id ON purchase_orders(org_id);

-- ============================================================
-- Comments
-- ============================================================

COMMENT ON TABLE organizations IS 'B2B SaaS organizations (factories/companies)';
COMMENT ON TABLE org_members IS 'Maps users to organizations with roles';
COMMENT ON TABLE profiles IS 'Extends Supabase auth.users with app-specific data';
COMMENT ON COLUMN org_members.role IS 'admin=platform, manager/operator/technician/procurement/viewer=org-level';
COMMENT ON COLUMN org_members.status IS 'active=full access, invited=pending, disabled=revoked';
COMMENT ON COLUMN profiles.is_platform_admin IS 'True for Yefai platform administrators';
