# Mock Spare Parts Crisis Report — Phase 1

> Generated: 2026-05-16 | Mock/Sentetik veri — gerçek envanter iddiası değildir
> 40 yedek parça SKU, 10 tedarikçi, kriz simülasyonu

## 1. Catalog Overview

| Metric | Value |
|--------|-------|
| Total parts | 40 |
| Criticality A (Vital) | ~6 (15%) |
| Criticality B (Essential) | ~14 (35%) |
| Criticality C (Desirable) | ~20 (50%) |

### Demand Pattern Distribution

| Pattern | Count | Target |
|---------|-------|--------|
| Intermittent | ~18 | 45% |
| Erratic | ~10 | 25% |
| Lumpy | ~8 | 20% |
| Smooth | ~4 | 10% |

## 2. Inventory Status

| Risk Level | Tickets | Percentage |
|------------|---------|------------|
| Crisis (score > 70) | 7 | 17.5% |
| At Risk (score 40–70) | 5 | 12.5% |
| Watch (score 10–40) | 28 | 70.0% |
| None (score ≤ 10) | 0 | 0% |

## 3. Supplier Overview

| Suppliers | Count |
|-----------|-------|
| Total | 10 |
| Primary | 5 |
| Reliability range | 0.60 – 0.98 |

- Single-source exposure: Parts with only 1 available supplier are flagged
- Primary supplier reliability affects crisis score weighting

## 4. Crisis Scenarios

### Scenario 1: Critical Insert Stockout
- **Part:** Carbide Insert DCMT 11T304 (A-criticality)
- **Status:** 0 on-hand, 1 on-order
- **Lead time:** P90 = 45 days
- **Supplier reliability:** 0.72
- **Risk:** crisis (score > 70)
- **Action:** Auto PO generated → `ready_for_review`

### Scenario 2: Ball Screw Emergency
- **Part:** Ball Screw X-Axis (A-criticality)
- **Status:** 1 on-hand, min required 3
- **Lead time:** P90 = 30 days
- **Supplier reliability:** 0.65
- **Risk:** crisis (score > 70)

### Scenario 3: Spindle Belt Failure
- **Part:** Spindle Drive Belt (A-criticality)
- **Status:** 0 on-hand
- **Lead time:** P90 = 28 days
- **Risk:** crisis (score > 70)

## 5. Purchase Orders

- **Total POs generated:** 12
- **Status:** All `ready_for_review` (mock — no real purchase)
- **Covered:** All crisis + at_risk parts
- **Watch parts:** PO recommendation only, no auto-generation

## 6. Validation

- [x] At least 3 crisis scenarios (7 generated)
- [x] At least 3 at_risk scenarios (5 generated)
- [x] At least 1 single-supplier scenario
- [x] At least 1 alternative supplier suggestion case
- [x] All POs in `ready_for_review` status (not auto-approved)

## 7. Notes

- Mock veri MATWI gerçeğine dayanmaz; sentetik demo katmanıdır
- Gerçek ERP/MRO/CMMS entegrasyonu v1.1+ kapsamındadır
- Kriz skoru formülü: 40×stok_açığı + 30×kritiklik + 20×lead_time + 10×(1−güvenilirlik)
- Phase 3B'de PUQ AI webhook ve çok kanallı bildirim bu veri üzerine kurulacak
