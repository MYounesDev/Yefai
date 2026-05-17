-- Yefai Phase B2 — Support tickets + files table
-- Support tickets for org → admin communication
-- Files table for Supabase Storage metadata

-- ============================================================
-- Support Tickets
-- ============================================================

CREATE TABLE IF NOT EXISTS support_tickets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id);

-- ============================================================
-- Files (Supabase Storage metadata)
-- NOT for MATWI images — those stay on local disk in images.file_path
-- ============================================================

CREATE TABLE IF NOT EXISTS files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by     UUID NOT NULL,
    bucket          TEXT NOT NULL,
    storage_path    TEXT NOT NULL,
    file_url        TEXT NOT NULL,
    file_name       TEXT NOT NULL,
    file_size       BIGINT,
    mime_type       TEXT,
    category        TEXT DEFAULT 'general'
                    CHECK (category IN ('avatar', 'report', 'document', 'export', 'general')),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_files_org_id ON files(org_id);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_files_category ON files(category);

-- ============================================================
-- Comments
-- ============================================================

COMMENT ON TABLE support_tickets IS 'Org support requests to platform admin';
COMMENT ON TABLE files IS 'Supabase Storage file metadata — NOT for MATWI images';
COMMENT ON COLUMN files.storage_path IS 'Path within Supabase Storage bucket';
COMMENT ON COLUMN files.file_url IS 'Full public or signed URL';
