-- Migration: Add prediction fields to anomalies table
-- Phase: 2.5 (Gelecek Tahmini - Wear Prediction Engine)
-- Description: Adds wear prediction and projection fields to anomalies table

-- Add prediction fields
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS estimated_wear_um FLOAT;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS wear_rate_um_per_hour FLOAT;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS hours_to_critical FLOAT;
ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS confidence TEXT CHECK (confidence IN ('low', 'medium', 'high', 'insufficient_data', 'critical'));

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_anomalies_hours_to_critical ON anomalies(hours_to_critical);
CREATE INDEX IF NOT EXISTS idx_anomalies_confidence ON anomalies(confidence);

-- Add comments
COMMENT ON COLUMN anomalies.estimated_wear_um IS 'Estimated wear in micrometers (calibrated from anomaly score)';
COMMENT ON COLUMN anomalies.wear_rate_um_per_hour IS 'Calculated wear rate in µm/hour from historical data';
COMMENT ON COLUMN anomalies.hours_to_critical IS 'Projected hours until critical threshold (200µm)';
COMMENT ON COLUMN anomalies.confidence IS 'Confidence level of prediction: low/medium/high/insufficient_data/critical';
