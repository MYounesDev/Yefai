-- Yefai Phase 1 — Initial Database Schema
-- Supabase lightweight metadata + pgvector store
-- Görüntü BLOB'u YOK — file_path local disk yolunu tutar
-- Sensör CSV'leri local'de — sensors tablosu Supabase'de yok

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Core tables
-- ============================================================

CREATE TABLE IF NOT EXISTS sets (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    image_count INT NOT NULL DEFAULT 0,
    metadata    JSONB DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS images (
    id              SERIAL PRIMARY KEY,
    set_id          INT REFERENCES sets(id) ON DELETE CASCADE,
    file_path       TEXT NOT NULL,
    flank_wear      FLOAT,
    adhesive_wear   FLOAT,
    combination_wear FLOAT,
    wear_type       TEXT,
    wear            FLOAT,
    timestamp       TIMESTAMPTZ,
    image_embedding vector(1024),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS anomalies (
    id          SERIAL PRIMARY KEY,
    image_id    INT REFERENCES images(id) ON DELETE CASCADE,
    score       FLOAT NOT NULL,
    wear_type   TEXT,
    detected_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Mock spare parts tables (Phase 1 Wave 3)
-- ============================================================

CREATE TABLE IF NOT EXISTS spare_parts_catalog (
    id              SERIAL PRIMARY KEY,
    part_id         TEXT UNIQUE NOT NULL,
    part_name       TEXT NOT NULL,
    criticality     TEXT NOT NULL CHECK (criticality IN ('A', 'B', 'C')),
    demand_pattern  TEXT NOT NULL,
    unit_cost       FLOAT NOT NULL DEFAULT 0,
    lead_time_p50   INT NOT NULL DEFAULT 7,
    lead_time_p90   INT NOT NULL DEFAULT 14,
    min_stock       INT NOT NULL DEFAULT 0,
    max_stock       INT NOT NULL DEFAULT 100,
    metadata        JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS suppliers (
    id                  SERIAL PRIMARY KEY,
    supplier_id         TEXT UNIQUE NOT NULL,
    supplier_name       TEXT NOT NULL,
    reliability_score   FLOAT NOT NULL DEFAULT 0.8,
    lead_time_p50       INT NOT NULL DEFAULT 7,
    lead_time_p90       INT NOT NULL DEFAULT 14,
    is_primary          BOOLEAN DEFAULT false,
    metadata            JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS inventory_snapshots (
    id              SERIAL PRIMARY KEY,
    part_id         TEXT REFERENCES spare_parts_catalog(part_id) ON DELETE CASCADE,
    on_hand         INT NOT NULL DEFAULT 0,
    on_order        INT NOT NULL DEFAULT 0,
    min_level       INT NOT NULL DEFAULT 0,
    max_level       INT NOT NULL DEFAULT 100,
    snapshot_date   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS part_tickets (
    id              SERIAL PRIMARY KEY,
    part_id         TEXT REFERENCES spare_parts_catalog(part_id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'waiting_part',
    quantity        INT NOT NULL DEFAULT 1,
    needed_by       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id              SERIAL PRIMARY KEY,
    part_id         TEXT REFERENCES spare_parts_catalog(part_id) ON DELETE CASCADE,
    supplier_id     TEXT REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    quantity        INT NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'ready_for_review',
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_images_set_id ON images(set_id);
CREATE INDEX IF NOT EXISTS idx_images_wear_type ON images(wear_type);
CREATE INDEX IF NOT EXISTS idx_images_timestamp ON images(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_image_id ON anomalies(image_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_score ON anomalies(score);

-- HNSW index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_images_embedding_hnsw
    ON images USING hnsw (image_embedding vector_cosine_ops);

-- Mock table indexes
CREATE INDEX IF NOT EXISTS idx_inventory_part_id ON inventory_snapshots(part_id);
CREATE INDEX IF NOT EXISTS idx_tickets_part_id ON part_tickets(part_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON part_tickets(status);
CREATE INDEX IF NOT EXISTS idx_po_part_id ON purchase_orders(part_id);
CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status);
