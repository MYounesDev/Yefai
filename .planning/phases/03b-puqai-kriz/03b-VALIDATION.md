---
phase: 3B
slug: puqai-kriz
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 3B — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio + respx/httpx mock |
| **Config file** | none yet — Wave 0 installs/creates |
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
| 3B-01-01 | PLAN.md | 1 | FR-5.3 | — | N/A | unit | `pytest tests/phase03b/test_puqai_client.py -q` | ❌ W0: `server/ai/puqai/client.py` | ⬜ pending |
| 3B-01-02 | PLAN.md | 1 | FR-5.4/FR-5.5/FR-5.6/FR-8.6 | — | N/A | unit | `pytest tests/phase03b/test_payload_templates.py -q` | ❌ W0: `server/ai/puqai/templates` | ⬜ pending |
| 3B-01-03 | PLAN.md | 1 | FR-5.8 | — | N/A | unit | `pytest tests/phase03b/test_webhook_retry.py -q` | ❌ W0: `server/ai/puqai/retry.py` | ⬜ pending |
| 3B-02-01 | PLAN.md | 2 | FR-5.3 | — | N/A | unit | `pytest tests/phase03b/test_notification_service.py -q` | ❌ W0: `server/services/notification_service.py` | ⬜ pending |
| 3B-02-02 | PLAN.md | 2 | FR-5.8 | — | N/A | unit | `pytest tests/phase03b/test_puqai_fallback.py -q` | ❌ W0: `server/ai/puqai/fallback.py` | ⬜ pending |
| 3B-03-01 | PLAN.md | 3 | FR-8.1/FR-8.3 | — | N/A | unit | `pytest tests/phase03b/test_crisis_service.py -q` | ❌ W0: `server/services/crisis_service.py` | ⬜ pending |
| 3B-03-02 | PLAN.md | 3 | FR-8.7 | — | N/A | unit | `pytest tests/phase03b/test_purchase_order_service.py -q` | ❌ W0: `server/services/purchase_order_service.py` | ⬜ pending |
| 3B-03-03 | PLAN.md | 3 | FR-8.8 | — | N/A | unit | `pytest tests/phase03b/test_supplier_service.py -q` | ❌ W0: `server/services/supplier_service.py` | ⬜ pending |
| 3B-04-01 | PLAN.md | 4 | FR-5.3/FR-5.8 | — | N/A | api | `pytest tests/phase03b/test_notifications_router.py -q` | ❌ W0: `server/routers/notifications.py` | ⬜ pending |
| 3B-04-02 | PLAN.md | 4 | FR-8.3/FR-8.7/FR-8.8 | — | N/A | api | `pytest tests/phase03b/test_spare_parts_router.py -q` | ❌ W0: `server/routers/spare_parts.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase03b/` — phase-specific test package/stubs
- [ ] `tests/conftest.py` — shared FastAPI/Supabase/mock fixtures as needed
- [ ] `pytest.ini` or `pyproject.toml` — markers for live/slow tests when relevant

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate completion | FR-5.3, FR-5.4, FR-5.5 | External account/service setup cannot be automated safely | Verify: G3 — PUQ AI hesabı, workflow webhook URL’leri ve test mesajları insan tarafından doğrulanmalı. |
| Live external/local service smoke | Service-dependent UAT | Requires real local Docker/webhook/account state | Run live marker test only after credentials/local service are ready |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags in commands.
- [ ] Feedback latency target accepted: < 90s.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
