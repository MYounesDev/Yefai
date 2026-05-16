---
phase: 3A
slug: rag-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 3A — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio; LLM live testleri mock dışı marker |
| **Config file** | none yet — Wave 0 installs/creates |
| **Quick run command** | `pytest tests/phase03a -q -m "not live"` |
| **Full suite command** | `pytest tests/phase03a -q` |
| **Estimated runtime** | < 90s mock |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase03a -q -m "not live"`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase03a -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 90s mock.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3A-01-01 | PLAN.md | 1 | FR-4.4 | — | N/A | unit | `pytest tests/phase03a/test_llm_client.py -q` | ❌ W0: `server/ai/llm/client.py` | ⬜ pending |
| 3A-01-02 | PLAN.md | 1 | FR-4.1/FR-4.4 | — | N/A | integration | `pytest tests/phase03a/test_rag_pipeline.py -q` | ❌ W0: `server/ai/rag/pipeline.py` | ⬜ pending |
| 3A-01-03 | PLAN.md | 1 | FR-4.1 | — | N/A | unit | `pytest tests/phase03a/test_prompts.py -q` | ❌ W0: `server/ai/rag/prompts.py` | ⬜ pending |
| 3A-02-01 | PLAN.md | 2 | FR-7.5/NFR-6 | — | N/A | unit | `pytest tests/phase03a/test_hybrid_search.py -q` | ❌ W0: `server/ai/rag/hybrid_search.py` | ⬜ pending |
| 3A-02-02 | PLAN.md | 2 | FR-4.5 | — | N/A | unit | `pytest tests/phase03a/test_sessions.py -q` | ❌ W0: `server/ai/rag/sessions.py` | ⬜ pending |
| 3A-03-01 | PLAN.md | 3 | FR-4.1/FR-4.5 | — | N/A | api | `pytest tests/phase03a/test_chat_router.py -q` | ❌ W0: `server/routers/chat.py` | ⬜ pending |
| 3A-03-02 | PLAN.md | 3 | FR-7.5 | — | N/A | api | `pytest tests/phase03a/test_search_router.py -q` | ❌ W0: `server/routers/search.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase03a/` — phase-specific test package/stubs
- [ ] `tests/conftest.py` — shared FastAPI/Supabase/mock fixtures as needed
- [ ] `pytest.ini` or `pyproject.toml` — markers for live/slow tests when relevant

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate completion | FR-4.1, FR-4.4, FR-4.5 | External account/service setup cannot be automated safely | Verify: G4 — LLM API key ve provider .env’de olmalı; Phase 2A embedding’leri hazır olmalı. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags in commands.
- [ ] Feedback latency target accepted: < 90s mock.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
