-- Yefai Phase B8 — Dashboard and Anomalies Schema Additions

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'anomalies' AND column_name = 'status') THEN
        ALTER TABLE anomalies ADD COLUMN status TEXT DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'resolved'));
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'anomalies' AND column_name = 'severity') THEN
        ALTER TABLE anomalies ADD COLUMN severity TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'anomalies' AND column_name = 'notes') THEN
        ALTER TABLE anomalies ADD COLUMN notes TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'anomalies' AND column_name = 'reviewed_by') THEN
        ALTER TABLE anomalies ADD COLUMN reviewed_by UUID REFERENCES profiles(id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'anomalies' AND column_name = 'reviewed_at') THEN
        ALTER TABLE anomalies ADD COLUMN reviewed_at TIMESTAMPTZ;
    END IF;
END $$;
