# Yefai Backend — Build Prompt Overview

> **Goal:** Extend the existing FastAPI backend into a production-grade **B2B SaaS** backend with multi-organization support, RBAC, Supabase Auth, file storage, and all domain services defined in the planning docs.
> **Rule:** Do NOT modify or remove any existing code, tables, or columns. Only ADD new modules, tables, columns, and endpoints on top of what exists.

---

## Current Server State (What Already Exists)

### Working Modules
| Module | Status | Files |
|--------|--------|-------|
| `main.py` | ✅ FastAPI app, CORS, health endpoint | Entry point |
| `db/client.py` | ✅ Supabase client singleton (service key) | `get_supabase_client()` |
| `db/config.py` | ✅ Pydantic settings from `.env` | `Settings`, `get_settings()` |
| `routers/anomalib.py` | ✅ Train, predict, status, model info | 4 endpoints |
| `routers/embeddings.py` | ✅ Embedding search (text + image) | 1 endpoint |
| `routers/novavision.py` | ✅ Deploy, models, inference, health | 7 endpoints |
| `routers/predictions.py` | ✅ Prediction, factory overview, recalculate | 3 endpoints |
| `services/anomalib_service.py` | ✅ PatchCore model management | Full |
| `services/embedding_service.py` | ✅ Jina CLIP v2 wrapper | Full |
| `services/novavision_service.py` | ✅ NovaVision container lifecycle | Full |
| `services/prediction_service.py` | ✅ Wear rate, projection, scenarios | Full |
| `ai/anomalib/` | ✅ Training, inference, dataset prep, export | 7 files |
| `ai/prediction/` | ✅ Calibration, projection, scenarios, trends, wear rate | 6 files |
| `ai/novavision/` | ✅ CLI wrapper, config, deploy, inference, schemas | 9 files |
| `ai/embeddings/` | ✅ Jina CLIP model, batch embed, search | 4 files |
| `etl/` | ✅ Data pipeline scripts | 7 files |
| `Snakefile` | ✅ Pipeline orchestration | Training pipeline |

### Stub/Placeholder Files (Need Implementation)
| File | Content | Phase |
|------|---------|-------|
| `routers/chat.py` | `# Chat router placeholder — Phase 3A` | Phase 3A |
| `routers/spare_parts.py` | `# Spare parts router placeholder — Phase 3B` | Phase 3B |
| `routers/notifications.py` | `# Notifications router placeholder — Phase 3B` | Phase 3B |

### Current Database Schema (Supabase — DO NOT MODIFY)

**Tables:**
- `sets` — MATWI set metadata (id, name, image_count, metadata)
- `images` — Image metadata + embedding (id, set_id, file_path, wear fields, image_embedding vector(1024))
- `anomalies` — Anomaly detections (id, image_id, score, wear_type, detected_at, + prediction fields from migration 003)
- `spare_parts_catalog` — Mock part catalog (part_id, part_name, criticality, demand_pattern, costs, lead times)
- `suppliers` — Mock supplier data (supplier_id, supplier_name, reliability_score, lead times)
- `inventory_snapshots` — Stock snapshots (part_id, on_hand, on_order, min/max_level)
- `part_tickets` — Maintenance tickets (part_id, status, quantity, needed_by)
- `purchase_orders` — Mock POs (part_id, supplier_id, quantity, status)

**Extensions:** `vector` (pgvector 0.8.0)

**Key Fact:** Images are stored on LOCAL DISK (`file_path` column), NOT in Supabase Storage. Embeddings (vector(1024)) ARE in Supabase. This architecture must NOT change.

### Current Config (.env)
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `SUPABASE_DB_HOST`, `SUPABASE_DB_NAME`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`
- `ENVIRONMENT` (development)
- `YEFAI_DATA_ROOT`

---

## What Needs to Be Added

### 1. Authentication & Authorization (Supabase Auth)
- Use **Supabase Auth** for user management (sign up, login, JWT tokens)
- FastAPI dependency that verifies Supabase JWT from `Authorization: Bearer <token>` header
- Role extraction from JWT / user metadata
- Org-scoped middleware (reads `X-Organization-Id` header, validates membership)

### 2. Multi-Organization Architecture
- `organizations` table, `org_members` table (user_id, org_id, role)
- All domain tables (`anomalies`, `sets`, `images`, `spare_parts_catalog`, etc.) get an `org_id` column
- Org-scoped queries: every data query filters by active org
- Org switching: validate user is member of target org

### 3. RBAC (Same roles as frontend)
| Role | Scope |
|------|-------|
| `admin` | Platform-level — manages orgs, cannot see org data |
| `manager` | Org-level — full access within org, manages members |
| `operator` | Org-level — views dashboard, anomalies, predictions, chatbot |
| `technician` | Org-level — operator + mark reviewed, view spare parts |
| `procurement` | Org-level — spare parts, POs, suppliers |
| `viewer` | Org-level — read-only |

### 4. Supabase Storage (NEW — separate from image_embedding images)
- **Bucket: `avatars`** — User profile pictures
- **Bucket: `org-files`** — Organization reports, documents, general uploads
- **`files` table** — stores file metadata + Supabase Storage URL
- **NOT for MATWI images** — those stay on local disk with `file_path` in `images` table

### 5. Missing Domain Services
- Chat/RAG router + service (Phase 3A)
- Spare parts crisis router + service (Phase 3B)
- Notifications/PUQ AI router + service (Phase 3B)
- Dashboard aggregation endpoints
- Admin/platform management endpoints

---

## Project Structure (What Gets Added)

```
server/
├── main.py                          # UPDATE: add new routers, lifespan
├── db/
│   ├── client.py                    # KEEP as-is
│   ├── config.py                    # UPDATE: add new env vars
│   └── migrations/
│       ├── 001_initial_schema.sql   # KEEP
│       ├── 003_prediction_fields.sql # KEEP
│       ├── 004_multi_org.sql        # NEW: organizations, org_members, org_id columns
│       ├── 005_auth_tables.sql      # NEW: profiles, support_tickets, files
│       └── 006_rls_policies.sql     # NEW: Row Level Security policies
├── auth/                            # NEW MODULE
│   ├── __init__.py
│   ├── dependencies.py              # get_current_user, require_role, require_org_access
│   ├── models.py                    # User, TokenPayload, OrgMembership pydantic models
│   └── permissions.py               # Role → Permission mapping, has_permission()
├── routers/
│   ├── __init__.py
│   ├── anomalib.py                  # KEEP
│   ├── embeddings.py                # KEEP
│   ├── novavision.py                # KEEP
│   ├── predictions.py               # UPDATE: add auth dependency
│   ├── auth.py                      # NEW: login, register, me, refresh
│   ├── organizations.py             # NEW: CRUD orgs, switch org, org details
│   ├── members.py                   # NEW: invite, list, update role, remove
│   ├── admin.py                     # NEW: platform admin endpoints
│   ├── chat.py                      # IMPLEMENT: RAG chatbot
│   ├── spare_parts.py               # IMPLEMENT: crisis, POs, suppliers
│   ├── notifications.py             # IMPLEMENT: PUQ AI webhooks
│   ├── dashboard.py                 # NEW: aggregation endpoints
│   ├── files.py                     # NEW: file upload/download (Supabase Storage)
│   └── health.py                    # NEW: detailed health check (extracted from main)
├── services/
│   ├── anomalib_service.py          # KEEP
│   ├── embedding_service.py         # KEEP
│   ├── novavision_service.py        # KEEP
│   ├── prediction_service.py        # KEEP (UPDATE: add org_id filtering)
│   ├── auth_service.py              # NEW: Supabase Auth wrapper
│   ├── org_service.py               # NEW: org CRUD, member management
│   ├── chat_service.py              # NEW: RAG pipeline
│   ├── crisis_service.py            # NEW: crisis score, auto-PO, alt suppliers
│   ├── notification_service.py      # NEW: PUQ AI webhook client
│   ├── dashboard_service.py         # NEW: stats aggregation
│   └── file_service.py              # NEW: Supabase Storage operations
├── ai/                              # KEEP ALL as-is
│   ├── anomalib/
│   ├── embeddings/
│   ├── novavision/
│   └── prediction/
├── etl/                             # KEEP ALL as-is
└── middleware/                      # NEW MODULE
    ├── __init__.py
    └── org_context.py               # Middleware to extract & validate org_id
```

---

## Approved Changes to Existing Code

> ✅ All recommendations approved by the user.

1. ✅ **Add `org_id` column to existing tables** (`sets`, `images`, `anomalies`, `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `part_tickets`, `purchase_orders`) — needed for multi-org scoping. This is an ADD COLUMN, not a schema change. → **Phase B01** (`004_multi_org.sql`)

2. ✅ **Add `machine_id` column to `anomalies` table** — the prediction service queries `anomalies` by `machine_id` but this column doesn't exist in the schema yet (migration 001 doesn't have it). Currently the code does `.eq("machine_id", machine_id)` which would fail. → **Phase B01** (`004_multi_org.sql`)

3. ✅ **Update existing routers to add auth dependency** — e.g., `predictions.py` endpoints should require authentication. This is a non-breaking addition of `Depends(get_current_user)`. → **Phase B04**

4. ✅ **Move health endpoint from `main.py` to `routers/health.py`** — cleaner separation. → **Phase B08**

---

## Phase Breakdown

| Phase | Document | Focus |
|-------|----------|-------|
| **Phase B1** | `B01-auth-and-multiorg.md` | Supabase Auth, JWT verification, multi-org tables, RBAC, org middleware |
| **Phase B2** | `B02-org-management.md` | Org CRUD, member management, admin panel endpoints, support tickets |
| **Phase B3** | `B03-storage-and-files.md` | Supabase Storage buckets, files table, upload/download endpoints |
| **Phase B4** | `B04-domain-auth-integration.md` | Add auth + org scoping to existing routers (predictions, anomalib, etc.) |
| **Phase B5** | `B05-chat-rag.md` | RAG chatbot service + router (Phase 3A from roadmap) |
| **Phase B6** | `B06-spare-parts-crisis.md` | Crisis service, auto-PO, alternative suppliers, spare parts router |
| **Phase B7** | `B07-notifications.md` | PUQ AI webhook client, notification router, multi-channel alerts |
| **Phase B8** | `B08-dashboard-aggregation.md` | Dashboard stats endpoints, factory overview, system health |
| **Phase B9** | `B09-integration-and-rls.md` | Lifespan consolidation, RLS policies, integration tests, error handling |

---

*Each phase document contains the complete prompt needed to implement that phase independently.*
