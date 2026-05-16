---
phase: 1
slug: veri-altyapisi
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-16
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Generated from PLAN.md + RESEARCH.md synthesis; statuses remain pending until implementation/tests exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Wave 0 installs; repo’da henüz test altyapısı yok) |
| **Config file** | none yet — Wave 0 installs/creates |
| **Quick run command** | `pytest tests/phase01 -q` |
| **Full suite command** | `pytest tests/phase01 tests/integration -q` |
| **Estimated runtime** | < 60s hedef |

---

## Sampling Rate

- **After every task commit:** Run that task’s Automated Command.
- **After every plan wave:** Run `pytest tests/phase01 -q`.
- **Before `/gsd:verify-work`:** Run `pytest tests/phase01 tests/integration -q` and resolve all red/flaky failures.
- **Max feedback latency:** < 60s hedef.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | PLAN.md | 1 | FR-1.1 | — | N/A | unit+integration | `pytest tests/phase01/test_unzip_data.py -q` | ❌ W0: `server/etl/unzip_data.py` | ⬜ pending |
| 1-01-02 | PLAN.md | 1 | FR-1.1 | — | N/A | unit | `pytest tests/phase01/test_parse_labels.py -q` | ❌ W0: `server/etl/parse_labels.py` | ⬜ pending |
| 1-01-03 | PLAN.md | 1 | FR-1.3 | — | N/A | unit | `pytest tests/phase01/test_parse_sensors.py -q` | ❌ W0: `server/etl/parse_sensors.py` | ⬜ pending |
| 1-02-01 | PLAN.md | 2 | FR-1.2 | — | N/A | unit | `pytest tests/phase01/test_split_data.py -q` | ❌ W0: `server/etl/split_data.py` | ⬜ pending |
| 1-02-02 | PLAN.md | 2 | FR-7.1/FR-7.2 | — | N/A | migration | `pytest tests/phase01/test_schema_sql.py -q` | ❌ W0: `server/db/migrations/001_initial_schema.sql` | ⬜ pending |
| 1-02-03 | PLAN.md | 2 | FR-7.1 | — | N/A | integration | `pytest tests/phase01/test_supabase_client.py -q` | ❌ W0: `server/db/client.py` | ⬜ pending |
| 1-03-01 | PLAN.md | 3 | FR-1.1/FR-7.1 | — | N/A | integration | `pytest tests/phase01/test_seed_database.py -q` | ❌ W0: `server/etl/seed_database.py` | ⬜ pending |
| 1-03-02 | PLAN.md | 3 | FR-1.5/FR-7.7 | — | N/A | unit | `pytest tests/phase01/test_mock_spare_parts.py -q` | ❌ W0: `server/etl/generate_mock_spare_parts.py` | ⬜ pending |
| 1-04-01 | PLAN.md | 4 | FR-1.4 | — | N/A | report | `pytest tests/phase01/test_data_quality_report.py -q` | ❌ W0: `reports/data_quality_report.md` | ⬜ pending |
| 1-04-02 | PLAN.md | 4 | FR-1.5 | — | N/A | report | `pytest tests/phase01/test_mock_spare_parts_report.py -q` | ❌ W0: `reports/mock_spare_parts_report.md` | ⬜ pending |
| 1-04-03 | PLAN.md | 4 | FR-7.1 | — | N/A | integration | `pytest tests/phase01/test_fastapi_scaffold.py -q` | ❌ W0: `server/main.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase01/` — phase-specific test package/stubs
- [ ] `tests/conftest.py` — shared FastAPI/Supabase/mock fixtures as needed
- [ ] `pytest.ini` or `pyproject.toml` — markers for live/slow tests when relevant

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Manual gate completion | FR-1.1, FR-1.2, FR-1.3 | External account/service setup cannot be automated safely | ✅ DONE: G1 — Yefai Supabase project configured; `.env` ready; REST HTTP 200; DB connect OK; `vector` 0.8.0 verified. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all MISSING references.
- [ ] No watch-mode flags in commands.
- [ ] Feedback latency target accepted: < 60s hedef.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 + first green sample.

**Approval:** pending
