---
phase: 2.5
slug: gelecek-tahmini
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 2.5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + scipy/numpy unit tests |
| **Config file** | none yet — Wave 0 installs/creates |
| **Quick run command** | `pytest tests/phase02c -q` |
| **Full suite command** | `pytest tests/phase02c tests/integration -q` |
| **Estimated runtime** | < 60s |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase02c -q`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase02c tests/integration -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 60s.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2C-01-01 | PLAN.md | 1 | FR-8.1 | — | N/A | unit | `pytest tests/phase02c/test_calibration.py -q` | ❌ W0: `server/ai/prediction/calibration.py` | ⬜ pending |
| 2C-01-02 | PLAN.md | 1 | FR-8.1 | — | N/A | unit | `pytest tests/phase02c/test_wear_rate.py -q` | ❌ W0: `server/ai/prediction/wear_rate.py` | ⬜ pending |
| 2C-01-03 | PLAN.md | 1 | FR-8.3 | — | N/A | unit | `pytest tests/phase02c/test_projection.py -q` | ❌ W0: `server/ai/prediction/projection.py` | ⬜ pending |
| 2C-02-01 | PLAN.md | 2 | FR-8.3 | — | N/A | unit | `pytest tests/phase02c/test_scenarios.py -q` | ❌ W0: `server/ai/prediction/scenarios.py` | ⬜ pending |
| 2C-02-02 | PLAN.md | 2 | FR-8.3 | — | N/A | unit | `pytest tests/phase02c/test_trends.py -q` | ❌ W0: `server/ai/prediction/trends.py` | ⬜ pending |
| 2C-03-01 | PLAN.md | 3 | FR-8.3 | — | N/A | migration | `pytest tests/phase02c/test_prediction_migration.py -q` | ❌ W0: `server/db/migrations/003_prediction_fields.sql` | ⬜ pending |
| 2C-03-02 | PLAN.md | 3 | FR-8.3 | — | N/A | api | `pytest tests/phase02c/test_predictions_api.py -q` | ❌ W0: `server/routers/predictions.py` | ⬜ pending |
| 2C-03-03 | PLAN.md | 3 | FR-8.3 | — | N/A | contract | `pytest tests/phase02c/test_crisis_interface_contract.py -q` | ❌ W0: `server/services/prediction_service.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase02c/` — phase-specific test package/stubs
- [ ] `tests/conftest.py` — shared FastAPI/Supabase/mock fixtures as needed
- [ ] `pytest.ini` or `pyproject.toml` — markers for live/slow tests when relevant

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate review | phase prerequisites | Confirms human-owned preconditions before execution | Read PLAN.md prerequisites and mark gate status before starting Wave 1 |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags in commands.
- [ ] Feedback latency target accepted: < 60s.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
