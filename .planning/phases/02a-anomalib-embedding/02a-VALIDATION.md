---
phase: 2A
slug: anomalib-embedding
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 2A — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (Wave 0) |
| **Config file** | none yet — Wave 0 installs/creates |
| **Quick run command** | `pytest tests/phase02a -q` |
| **Full suite command** | `pytest tests/phase02a tests/integration -q` |
| **Estimated runtime** | < 120s mock/smoke; full model testleri opsiyonel slow marker |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase02a -q`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase02a tests/integration -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 120s mock/smoke; full model testleri opsiyonel slow marker.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2A-01-01 | PLAN.md | 1 | FR-2.1 | — | N/A | unit | `pytest tests/phase02a/test_anomalib_dataset.py -q` | ❌ W0: `server/ai/anomalib/dataset.py` | ⬜ pending |
| 2A-01-02 | PLAN.md | 1 | FR-2.3 | — | N/A | report | `pytest tests/phase02a/test_image_quality_report.py -q` | ❌ W0: `reports/image_data_quality.md` | ⬜ pending |
| 2A-02-01 | PLAN.md | 2 | FR-2.1 | — | N/A | smoke | `pytest tests/phase02a/test_patchcore_train.py -q` | ❌ W0: `server/ai/anomalib/train.py` | ⬜ pending |
| 2A-02-02 | PLAN.md | 2 | FR-2.1 | — | N/A | unit | `pytest tests/phase02a/test_model_export.py -q` | ❌ W0: `server/ai/anomalib/export.py` | ⬜ pending |
| 2A-02-03 | PLAN.md | 2 | FR-2.3 | — | N/A | integration | `pytest tests/phase02a/test_anomalib_inference.py -q` | ❌ W0: `server/ai/anomalib/inference.py` | ⬜ pending |
| 2A-02-04 | PLAN.md | 2 | FR-2.4 | — | N/A | unit | `pytest tests/phase02a/test_wear_classifier.py -q` | ❌ W0: `server/ai/anomalib/wear_classifier.py` | ⬜ pending |
| 2A-03-01 | PLAN.md | 3 | FR-2.6/FR-7.3 | — | N/A | smoke | `pytest tests/phase02a/test_jina_model.py -q` | ❌ W0: `server/ai/embeddings/model.py` | ⬜ pending |
| 2A-03-02 | PLAN.md | 3 | FR-7.3 | — | N/A | integration | `pytest tests/phase02a/test_batch_embed.py -q` | ❌ W0: `server/ai/embeddings/batch_embed.py` | ⬜ pending |
| 2A-03-03 | PLAN.md | 3 | FR-7.5 | — | N/A | unit | `pytest tests/phase02a/test_embedding_search.py -q` | ❌ W0: `server/ai/embeddings/search.py` | ⬜ pending |
| 2A-04-01 | PLAN.md | 4 | FR-2.1/FR-2.3 | — | N/A | api | `pytest tests/phase02a/test_anomalib_router.py -q` | ❌ W0: `server/routers/anomalib.py` | ⬜ pending |
| 2A-04-02 | PLAN.md | 4 | FR-7.5 | — | N/A | api | `pytest tests/phase02a/test_embeddings_router.py -q` | ❌ W0: `server/routers/embeddings.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase02a/` — phase-specific test package/stubs
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
- [ ] Feedback latency target accepted: < 120s mock/smoke; full model testleri opsiyonel slow marker.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
