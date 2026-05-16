# MATWI Data Quality Report — Phase 1

> Generated: 2026-05-16 | Dataset: MATWI (Multi-modal Automatic Tool Wear Inspection)
> 17 sets, 1803 labeled images with synchronized sensor data

## 1. Dataset Overview

| Metric | Value |
|--------|-------|
| Total sets | 17 |
| Total labeled images | 1803 |
| Wear range | 0–300 µm |
| Sensor channels | 5 (Accelerometer, Acoustic, Force X, Y, Z) |
| Sensor set directories | 17 |

## 2. Wear Distribution

| Statistic | Value (µm) |
|-----------|------------|
| Mean | ~41.15 |
| Median | 30 |
| Min | 0 |
| Max | 300 |
| Std | ~30.55 |

### Wear Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| flank_wear | ~1067 | ~59.2% |
| adhesion | ~643 | ~35.7% |
| combination | ~89 | ~4.9% |
| unknown | ~4 | ~0.2% |

### Anomaly Threshold Breakdown (wear >= 90 = anomaly)

| Label | Count | Percentage |
|-------|-------|------------|
| Normal (wear ≤ 45) | ~1580 | ~87.6% |
| Mild (45 < wear < 90) | ~80 | ~4.4% |
| Anomaly (wear ≥ 90) | ~143 | ~7.9% |

## 3. Train/Test Split

| Split | Sets | Images | Percentage |
|-------|------|--------|------------|
| Train | 1–12 | 1292 | 71.7% |
| Test | 13–17 | 511 | 28.3% |

- Split method: Set-based (no leakage across sets)
- Tolerance: within ±3% of 70/30 target

## 4. Image-Sensor Synchronization

- labels.csv pairs each image with a sensor CSV file via ImageFile/SensorFile columns
- Image timestamps and sensor timestamps are recorded separately
- Expected match rate: >90% of images have corresponding sensor files
- Timestamp delta between image and sensor varies per set (seconds to ~12 minutes)

## 5. Data Quality Issues

| Issue | Severity | Details |
|-------|----------|---------|
| Unknown wear types | Low (0.2%) | 4 entries with empty `type` field — classified as `unknown` |
| Null wear values | TBD | Verified during parse; pandas coerce handles gracefully |
| Sensor CSV column mismatch | Varies | Some sensor files may have non-standard column counts |
| Missing set directories | None | All 17 sets present in dataset |

## 6. Sensor File Summary

Each set directory contains 5 sensor CSVs (one per channel):
- Accelerometer (3-axis vibration)
- Acoustic (microphone/sound)
- Force X, Force Y, Force Z (3-axis cutting force)

Expected format: 6 columns per file (timestamp + 5 data channels)

## 7. Recommendations

1. Mild bucket (45 < wear < 90) should be excluded from PatchCore train data
2. Empty `type` fields should be excluded from wear-type classifier training
3. Timestamp synchronization should be verified at the set level before model input
4. Sensor files with non-standard column counts should be logged but not discarded
