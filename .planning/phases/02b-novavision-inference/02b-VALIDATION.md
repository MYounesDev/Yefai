---
phase: 2B
slug: novavision-inference
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 2B — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio; live Docker/NovaVision testleri marker ile ayrılır |
| **Config file** | none yet — Wave 0 installs/creates |
| **Quick run command** | `pytest tests/phase02b -q -m "not live"` |
| **Full suite command** | `pytest tests/phase02b -q` |
| **Estimated runtime** | < 90s mock; live değişken |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase02b -q -m "not live"`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase02b -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 90s mock; live değişken.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2B-01-01 | PLAN.md | 1 | FR-2.2 | — | N/A | unit | `pytest tests/phase02b/test_novavision_cli.py -q` | ❌ W0: `server/ai/novavision/cli.py` | ⬜ pending |
| 2B-01-02 | PLAN.md | 1 | FR-2.2 | — | N/A | unit | `pytest tests/phase02b/test_novavision_config.py -q` | ❌ W0: `server/ai/novavision/config.py` | ⬜ pending |
| 2B-02-01 | PLAN.md | 2 | FR-2.2 | — | N/A | integration | `pytest tests/phase02b/test_deploy_service.py -q` | ❌ W0: `server/ai/novavision/deploy.py` | ⬜ pending |
| 2B-02-02 | PLAN.md | 2 | FR-2.2 | — | N/A | unit | `pytest tests/phase02b/test_model_registry.py -q` | ❌ W0: `server/ai/novavision/models.py` | ⬜ pending |
| 2B-03-01 | PLAN.md | 3 | FR-2.2 | — | N/A | unit | `pytest tests/phase02b/test_preprocessing.py -q` | ❌ W0: `server/ai/novavision/preprocessing.py` | ⬜ pending |
| 2B-03-02 | PLAN.md | 3 | FR-2.2/FR-2.3 | — | N/A | api | `pytest tests/phase02b/test_inference_client.py -q` | ❌ W0: `server/ai/novavision/inference.py` | ⬜ pending |
| 2B-03-03 | PLAN.md | 3 | FR-2.2 | — | N/A | integration | `pytest tests/phase02b/test_lifecycle.py -q` | ❌ W0: `server/ai/novavision/lifecycle.py` | ⬜ pending |
| 2B-04-01 | PLAN.md | 4 | FR-2.2 | — | N/A | api | `pytest tests/phase02b/test_novavision_router.py -q` | ❌ W0: `server/routers/novavision.py` | ⬜ pending |
| 2B-04-02 | PLAN.md | 4 | FR-2.2 | — | N/A | manual/live | `pytest tests/test_novavision_live.py -q -m live` | ❌ W0: `tests/test_novavision_live.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase02b/` — phase-specific test package/stubs
- [ ] `tests/conftest.py` — shared FastAPI/Supabase/mock fixtures as needed
- [ ] `pytest.ini` or `pyproject.toml` — markers for live/slow tests when relevant

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate completion | FR-2.2, FR-2.3, FR-5.2 | External account/service setup cannot be automated safely | Verify: G2 — Docker Desktop, novavision CLI, NovaVision token ve local install insan tarafından tamamlanmalı. |
| Live external/local service smoke | Service-dependent UAT | Requires real local Docker/webhook/account state | Run live marker test only after credentials/local service are ready |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags in commands.
- [ ] Feedback latency target accepted: < 90s mock; live değişken.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
