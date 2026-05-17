---
phase: 3B
slug: puqai-kriz
status: implemented_mock_green
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-16
last_updated: 2026-05-17T03:37:44Z
---

# Phase 3B — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Updated after Phase 3B backend mock-mode implementation and test execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio + respx/httpx mock |
| **Config file** | `server/pyproject.toml` / project pytest configuration |
| **Quick run command** | `pytest tests/phase03b -q` |
| **Full suite command** | `pytest tests/phase03b tests/integration -q` |
| **Estimated runtime** | < 90s |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase03b -q`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase03b tests/integration -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 90s.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3B-01-01 | PLAN.md | 1 | FR-5.3 | — | N/A | unit | `pytest tests/phase03b/test_puqai_client.py -q` | ✅ `server/ai/puqai/client.py` | ✅ green via phase03b/pre-commit |
| 3B-01-02 | PLAN.md | 1 | FR-5.4/FR-5.5/FR-5.6/FR-8.6 | — | N/A | unit | `pytest tests/phase03b/test_payload_templates.py -q` | ✅ `server/ai/puqai/templates` | ✅ green via phase03b/pre-commit |
| 3B-01-03 | PLAN.md | 1 | FR-5.8 | — | N/A | unit | `pytest tests/phase03b/test_webhook_retry.py -q` | ✅ `server/ai/puqai/retry.py` | ✅ green via phase03b/pre-commit |
| 3B-02-01 | PLAN.md | 2 | FR-5.3 | — | N/A | unit | `pytest tests/phase03b/test_notification_service.py -q` | ✅ `server/services/notification_service.py` | ✅ green via phase03b/pre-commit |
| 3B-02-02 | PLAN.md | 2 | FR-5.8 | — | N/A | unit | `pytest tests/phase03b/test_puqai_fallback.py -q` | ✅ `server/ai/puqai/fallback.py` | ✅ green via phase03b/pre-commit |
| 3B-03-01 | PLAN.md | 3 | FR-8.1/FR-8.3 | — | N/A | unit | `pytest tests/phase03b/test_crisis_service.py -q` | ✅ `server/services/crisis_service.py` | ✅ green via phase03b/pre-commit |
| 3B-03-02 | PLAN.md | 3 | FR-8.7 | — | N/A | unit | `pytest tests/phase03b/test_purchase_order_service.py -q` | ✅ `server/services/purchase_order_service.py` | ✅ green via phase03b/pre-commit |
| 3B-03-03 | PLAN.md | 3 | FR-8.8 | — | N/A | unit | `pytest tests/phase03b/test_supplier_service.py -q` | ✅ `server/services/supplier_service.py` | ✅ green via phase03b/pre-commit |
| 3B-04-01 | PLAN.md | 4 | FR-5.3/FR-5.8 | — | N/A | api | `pytest tests/phase03b/test_notifications_router.py -q` | ✅ `server/routers/notifications.py` | ✅ green via phase03b/pre-commit |
| 3B-04-02 | PLAN.md | 4 | FR-8.3/FR-8.7/FR-8.8 | — | N/A | api | `pytest tests/phase03b/test_spare_parts_router.py -q` | ✅ `server/routers/spare_parts.py` | ✅ green via phase03b/pre-commit |
| 3B-04-03 | yedek-parca-krizi-mock-plan.md | 4 | FR-8.3/FR-8.7/FR-8.8 | — | N/A | api | `pytest ../tests/phase03b/test_routers.py::TestCrisisWorkflow ../tests/phase03b/test_crisis_service.py -q` | ✅ `server/services/spare_parts_workflow_service.py` | ✅ green targeted |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/phase03b/` — phase-specific test package/stubs
- [x] `tests/conftest.py` / local path setup — shared FastAPI/Supabase/mock fixtures as needed
- [x] `server/pyproject.toml` / existing test tooling — markers/config as needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate completion | FR-5.3, FR-5.4, FR-5.5 | External account/service setup cannot be automated safely | Verify: G3 — PUQ AI hesabı, workflow webhook URL’leri ve test mesajları insan tarafından doğrulanmalı. |
| Live external/local service smoke | Service-dependent UAT | Requires real local Docker/webhook/account state | Run live marker test only after credentials/local service are ready |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all MISSING references.
- [x] No watch-mode flags in commands.
- [x] Feedback latency target accepted: < 90s for targeted phase tests; full pre-commit may exceed 90s.
- [x] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** backend mock-mode approved; live PUQ AI channel delivery remains blocked by G3 manual gate.
