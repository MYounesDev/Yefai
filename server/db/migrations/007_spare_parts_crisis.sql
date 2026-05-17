-- Yefai Phase B6 — Spare Parts Crisis Schema Additions

-- ============================================================
-- Supplier Parts Junction Table
-- ============================================================

CREATE TABLE IF NOT EXISTS supplier_parts (
    id              SERIAL PRIMARY KEY,
    supplier_id     TEXT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    part_id         TEXT REFERENCES spare_parts_catalog(part_id) ON DELETE CASCADE,
    unit_cost       FLOAT,
    lead_time_days  INT,
    is_preferred    BOOLEAN DEFAULT false,
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE(supplier_id, part_id, org_id)
);

CREATE INDEX IF NOT EXISTS idx_supplier_parts_part_id ON supplier_parts(part_id);
CREATE INDEX IF NOT EXISTS idx_supplier_parts_supplier_id ON supplier_parts(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_parts_org_id ON supplier_parts(org_id);

-- ============================================================
-- Updates to existing tables
-- ============================================================

-- Add risk_level to part_tickets
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'part_tickets' AND column_name = 'risk_level') THEN
        ALTER TABLE part_tickets ADD COLUMN risk_level TEXT DEFAULT 'safe' CHECK (risk_level IN ('safe', 'watch', 'at_risk', 'critical'));
    END IF;
END $$;
