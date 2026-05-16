---
phase: 2B
slug: novavision-inference
status: mock_green_live_pending
nyquist_compliant: true
wave_0_complete: true
last_updated: 2026-05-16
---

# Phase 2B — Validation Strategy

> Per-phase validation contract for NovaVision local inference. Current implementation is mock-mode green; live validation remains intentionally pending behind Manual Gate G2 and Phase 2A `.pt` artifact availability.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + FastAPI TestClient; live Docker/NovaVision testleri `live` marker ile ayrılır |
| **Config file** | `server/pyproject.toml` + root `pytest.ini` live marker registration |
| **Quick run command** | `cd server && uv run pytest ../tests/phase02b -q` |
| **Focused Phase 2B command** | `cd server && uv run pytest ../tests/phase02b ../tests/test_novavision_live.py -q` |
| **Full backend gate** | `cd server && uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run --extra dev pytest ../tests/ -q` |
| **Estimated runtime** | < 90s mock; live değişken |

---

## Current Verification Result

Son odaklı Phase 2B test çalıştırması:

```bash
cd server && uv run pytest ../tests/phase02b ../tests/test_novavision_live.py -q
```

Sonuç:

- `5 passed, 2 skipped`
- Skip edilen iki test `@pytest.mark.live` kapsamındadır; G2 live token/local install/container ve Phase 2A `.pt` model artifact gerektirir.

Önceki tam kalite gate raporu `reports/novavision_phase02b.md` içinde kayıtlıdır:

- Ruff check: passed
- Ruff format check: passed
- Mypy: passed
- Pytest: `51 passed, 2 skipped`

---

## Sampling Rate

- **After every task commit:** Run the focused Phase 2B command.
- **After every plan wave:** Run `cd server && uv run pytest ../tests/phase02b -q`.
- **Before phase sign-off:** Run the full backend gate and resolve all red/flaky failures.
- **Max feedback latency:** < 90s mock; live değişken.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2B-01-01 | PLAN.md | 1 | NovaVision CLI wrapper | mock/unit via API contract + wrapper import coverage | `cd server && uv run pytest ../tests/phase02b -q` | ✅ `server/ai/novavision/cli.py` | ✅ mock green |
| 2B-01-02 | PLAN.md | 1 | Config & health | api | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_health_mock_mode -q` | ✅ `server/ai/novavision/config.py` | ✅ mock green |
| 2B-02-01 | PLAN.md | 2 | Deploy service | api/mock integration | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_deploy_mock_mode -q` | ✅ `server/ai/novavision/deploy.py`, `server/services/novavision_service.py` | ✅ mock green |
| 2B-02-02 | PLAN.md | 2 | Model registry/status | api/mock integration | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_models_mock_mode -q` | ✅ `server/ai/novavision/models.py` | ✅ mock green |
| 2B-03-01 | PLAN.md | 3 | Preprocessing contract | exercised through inference request contract | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_inference_base64_mock_mode -q` | ✅ `server/ai/novavision/preprocessing.py` | ✅ mock green |
| 2B-03-02 | PLAN.md | 3 | Local REST inference client + mock fallback | api/mock integration | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_inference_base64_mock_mode -q` | ✅ `server/ai/novavision/inference.py`, `server/ai/novavision/schemas.py` | ✅ mock green |
| 2B-03-03 | PLAN.md | 3 | Container lifecycle helper | mock health/lifecycle contract | `cd server && uv run pytest ../tests/phase02b/test_novavision_mock.py::test_novavision_health_mock_mode -q` | ✅ `server/ai/novavision/lifecycle.py` | ✅ mock green; live pending |
| 2B-04-01 | PLAN.md | 4 | FastAPI router endpoints | api | `cd server && uv run pytest ../tests/phase02b -q` | ✅ `server/routers/novavision.py` | ✅ mock green |
| 2B-04-02 | PLAN.md | 4 | Real model live integration | manual/live | `cd server && NOVAVISION_MOCK=false NOVAVISION_TEST_MODEL_PATH=... NOVAVISION_TEST_IMAGE_PATH=... uv run pytest ../tests/test_novavision_live.py -q -m live` | ✅ `tests/test_novavision_live.py` | ⏸ pending G2 + Phase 2A `.pt` artifact |

*Status: ✅ green · ❌ red · ⚠️ flaky · ⏸ pending external/manual gate*

---

## Wave 0 Requirements

- [x] `tests/phase02b/` — phase-specific mock API tests
- [x] `pytest.ini` — `live` marker registered for root-level test execution
- [x] `server/pyproject.toml` — pytest/dev dependency configuration
- [~] `tests/conftest.py` — not required for current Phase 2B mock contract; add shared fixtures only if later phases need them

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Status |
|----------|-------------|------------|-------------------|--------|
| Manual gate completion | FR-2.2, FR-2.3, FR-5.2 | External account/service setup cannot be automated safely | Verify: G2 — Docker Desktop, novavision CLI, NovaVision token ve local install insan tarafından tamamlanmalı. | ⏸ token/local install pending |
| Live external/local service smoke | Service-dependent UAT | Requires real local Docker/account/model state | Set `NOVAVISION_MOCK=false`, provide `NOVAVISION_TEST_MODEL_PATH` and `NOVAVISION_TEST_IMAGE_PATH`, then run live marker tests. | ⏸ Phase 2A model + live container pending |

---

## Validation Sign-Off

- [x] Mock-mode tasks have automated verification.
- [x] Sampling continuity preserved for mock contract.
- [x] Wave 0 covers current test/config references.
- [x] No watch-mode flags in commands.
- [x] Feedback latency target accepted: < 90s mock; live değişken.
- [ ] Full live sign-off: pending G2 token/local install/container and Phase 2A `.pt` artifact.

**Approval:** mock-mode approved; live NovaVision approval pending manual gate.
