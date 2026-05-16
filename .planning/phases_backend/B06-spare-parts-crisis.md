# Phase B6 — Spare Parts Crisis Service

> Implement the spare parts crisis management backend (Phase 3B from ROADMAP.md). Replace the placeholder `routers/spare_parts.py` with full crisis scoring, auto-PO generation, and supplier management.

## Context

The database already has the tables: `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `part_tickets`, `purchase_orders`. The ETL script `etl/generate_mock_spare_parts.py` seeds mock data. The crisis scoring algorithm is defined in `yedek-parca-krizi-mock-plan.md`.

## Task

### 1. Crisis Service (`services/crisis_service.py`)

The core business logic service. Implements the crisis score formula from `yedek-parca-krizi-mock-plan.md`:

```python
class CrisisService:
    def __init__(self, supabase: Client, prediction_service: PredictionService):
        self.supabase = supabase
        self.prediction_service = prediction_service

    async def calculate_crisis_score(self, org_id: str, part_id: str) -> dict:
        """
        Calculate crisis score (0-100) for a spare part.

        Formula components (from yedek-parca-krizi-mock-plan.md):
        1. Stock coverage ratio: on_hand / projected_demand → score component
        2. Lead time vs time-to-critical: if lead_time > hours_to_critical → high risk
        3. Part criticality: A=high weight, B=medium, C=low
        4. Demand pattern: sporadic=higher uncertainty bonus
        5. Supplier reliability: low reliability → higher crisis score

        Returns: {
            part_id, crisis_score, risk_level (safe/watch/at_risk/critical),
            breakdown: { stock_score, lead_time_score, criticality_score, supplier_score },
            recommendations: [...]
        }
        """

    async def get_crisis_dashboard(self, org_id: str) -> dict:
        """
        Get org-wide crisis overview:
        - Total parts, parts at risk, critical count
        - Top 5 crisis parts (sorted by score desc)
        - Overall risk distribution (safe/watch/at_risk/critical counts)
        - Recent PO activity
        """

    async def create_auto_order(self, org_id: str, ticket_id: str) -> dict:
        """
        Auto-generate purchase order for a ticket:
        1. Look up ticket → get part_id, quantity
        2. Find best supplier (primary + highest reliability)
        3. Calculate optimal order quantity (EOQ or reorder point)
        4. Create purchase_orders row with status='ready_for_review'
        5. Return PO details
        """

    async def get_alternative_suppliers(self, org_id: str, part_id: str) -> list[dict]:
        """
        Get alternative suppliers for a part:
        - All suppliers that can provide this part
        - Sorted by: reliability_score desc, lead_time_p50 asc
        - Include cost comparison, reliability comparison
        """
```

### 2. Spare Parts Router (`routers/spare_parts.py`)

Replace the placeholder:

```python
router = APIRouter(prefix="/api/spare-parts", tags=["spare-parts"])

# --- Crisis Dashboard ---

GET /api/spare-parts/crisis
  Auth: VIEW_SPARE_PARTS permission
  → Crisis dashboard overview (org-scoped)

GET /api/spare-parts/crisis/{part_id}
  Auth: VIEW_SPARE_PARTS permission
  → Detailed crisis score for a specific part

# --- Catalog ---

GET /api/spare-parts/catalog
  Auth: VIEW_SPARE_PARTS permission
  Query: criticality?, search?
  → Paginated parts catalog (org-scoped)

GET /api/spare-parts/catalog/{part_id}
  Auth: VIEW_SPARE_PARTS permission
  → Part details + current inventory + ticket count

# --- Inventory ---

GET /api/spare-parts/inventory/{part_id}
  Auth: VIEW_SPARE_PARTS permission
  → Inventory snapshot history for a part

# --- Tickets ---

GET /api/spare-parts/tickets
  Auth: VIEW_SPARE_PARTS permission
  Query: status?, part_id?, page, limit
  → Paginated ticket list (org-scoped)

POST /api/spare-parts/tickets/{ticket_id}/auto-order
  Auth: APPROVE_PO permission (Manager/Procurement)
  → Auto-generate PO for ticket, return PO details

# --- Purchase Orders ---

GET /api/spare-parts/purchase-orders
  Auth: VIEW_SPARE_PARTS permission
  Query: status?, part_id?, page, limit
  → Paginated PO list (org-scoped)

POST /api/spare-parts/purchase-orders/{po_id}/approve
  Auth: APPROVE_PO permission (Manager/Procurement)
  → Set status='approved', return updated PO

POST /api/spare-parts/purchase-orders/{po_id}/reject
  Auth: APPROVE_PO permission (Manager/Procurement)
  Body: { reason? }
  → Set status='rejected', return updated PO

# --- Suppliers ---

GET /api/spare-parts/suppliers
  Auth: VIEW_SPARE_PARTS permission
  → List all suppliers (org-scoped)

GET /api/spare-parts/suppliers/{part_id}/alternatives
  Auth: VIEW_SPARE_PARTS or MANAGE_SUPPLIERS permission
  → Alternative supplier comparison for a part
```

### 3. Data Updates

Add a `risk_level` computed field or column to help filtering:
```sql
-- Optional: add risk_level to part_tickets for query convenience
ALTER TABLE part_tickets ADD COLUMN IF NOT EXISTS risk_level TEXT DEFAULT 'safe'
    CHECK (risk_level IN ('safe', 'watch', 'at_risk', 'critical'));
```

### 4. Supplier-Part Relationship

Currently `suppliers` table doesn't have a direct link to parts. Add a junction table:

```sql
CREATE TABLE IF NOT EXISTS supplier_parts (
    id              SERIAL PRIMARY KEY,
    supplier_id     TEXT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    part_id         TEXT REFERENCES spare_parts_catalog(part_id) ON DELETE CASCADE,
    unit_cost       FLOAT,
    lead_time_days  INT,
    is_preferred    BOOLEAN DEFAULT false,
    org_id          UUID REFERENCES organizations(id),
    UNIQUE(supplier_id, part_id, org_id)
);

CREATE INDEX IF NOT EXISTS idx_supplier_parts_part_id ON supplier_parts(part_id);
CREATE INDEX IF NOT EXISTS idx_supplier_parts_supplier_id ON supplier_parts(supplier_id);
```

## Deliverables

- [ ] `services/crisis_service.py` — crisis score calculation, auto-PO, alt suppliers
- [ ] `routers/spare_parts.py` — full spare parts API (crisis, catalog, inventory, tickets, POs, suppliers)
- [ ] Migration for supplier_parts junction table + risk_level column
- [ ] Crisis score formula implemented per `yedek-parca-krizi-mock-plan.md`
- [ ] All endpoints org-scoped and auth-protected
- [ ] PO approve/reject restricted to Manager/Procurement
- [ ] Auto-order picks best supplier automatically
- [ ] `main.py` updated to include spare parts router
