# Phase 6 — Spare Parts Crisis Dashboard

> The third core problem: spare parts crisis management. Crisis dashboard, purchase order review screen, and supplier comparison.
> 
> **Role Access:** Full access for Manager and Procurement. Technician can view crisis dashboard and PO status (read-only). Viewer sees read-only. Operator CANNOT access these pages (redirect to dashboard).
> **Role-Gated Actions:** "Approve/Reject PO" → Manager, Procurement only. "Compare Suppliers" / "Switch to Alternative" → Manager, Procurement. Technician and Viewer see data without action buttons.

## Pages

### 1. Spare Parts Crisis Dashboard (`src/app/(dashboard)/spare-parts/page.tsx`)

**API calls:** `getSparePartsCatalog()`, `getPartTickets()`, `getInventorySnapshots()`, `getPurchaseOrders()`

#### Crisis Overview Stats (top row, 4 cards)

- **Crisis Tickets**: count of `risk_level = crisis`, pulsing red glow if > 0
- **At-Risk Parts**: count of `risk_level = at_risk`, amber badge
- **Pending POs**: count of `status = ready_for_review`
- **Stock Alerts**: count of parts where `on_hand < reorder_point`

#### Crisis Ticket Feed

Table/card list of active tickets sorted by `stockout_risk_score` (highest first):

Each ticket:
- Ticket ID + status badge (planned/waiting_part/ordered/stockout/closed)
- Machine + Tool reference
- Part name + part ID
- Risk level badge: none (gray) / watch (blue) / at_risk (amber) / crisis (red pulsing)
- Crisis score: 0-100, mini progress bar (green → red gradient)
- Needed by date vs expected replenishment date comparison
- Auto PO indicator: "PO Created" badge if `auto_po_id` exists
- Click → opens ticket detail modal or links to PO review

Filters: All / Watch / At-Risk / Crisis / Resolved

#### Inventory Status Grid

Grid of parts from `getSparePartsCatalog()` with inventory overlaid:

Each part card:
- Part name + ID
- Criticality class badge: A_vital (red), B_essential (amber), C_desirable (green)
- Stock bar: `on_hand` / `reorder_point` visual bar
- On order quantity
- Supplier count indicator
- Lead time (p50 / p90)
- "View Suppliers" button

Color coding: parts below reorder point have amber/red border glow.

#### Crisis Score Breakdown (Expandable)

When clicking on a crisis ticket, show the score breakdown:
```
stockout_risk_score = 82
├── Shortage Probability:  0.35 × 0.90 = 31.5
├── Lead Time Gap:         0.25 × 0.85 = 21.3
├── Criticality:           0.20 × 1.00 = 20.0
├── Supplier Risk:         0.10 × 0.70 = 7.0
└── Anomaly Severity:      0.10 × 0.25 = 2.5
```
Animated bar for each factor.

### 2. Purchase Order Review (`src/app/(dashboard)/spare-parts/purchase-orders/page.tsx`)

**API calls:** `getPurchaseOrders()`, `approvePurchaseOrder(poId)`, `rejectPurchaseOrder(poId)`, `getAlternativeSuppliers(partId)`

#### PO List

Cards for each PO in `ready_for_review` status (highlight) plus `draft` and `approved`:

Each PO card:
- **PO ID** (e.g., PO-2026-0042)
- **Urgency badge**: normal (gray), rush (amber), critical (red pulsing)
- **Status badge**: draft / ready_for_review / approved
- **Part**: name, required qty, unit cost, total cost
- **Supplier**: name, reliability score (star rating or bar), lead time (p50/p90)
- **Expected delivery** vs **needed by** — visual comparison bar
  - Green: delivery before needed-by
  - Red: delivery after needed-by (delayed)
- **Alternative supplier** section:
  - If alternative exists with better lead time: green badge "Alternative: HızlıParça A.Ş. — 5 days earlier"
  - If alternative is more expensive: amber badge "Alternative available but 30% more costly"
  - If no alternative: red badge "Single source — no alternative"
  - "Compare Suppliers" button → opens modal
- **Action buttons** (only for `ready_for_review`):
  - "Approve" (green button) → calls `approvePurchaseOrder(poId)` → toast "PO approved" → card turns green
  - "Reject" (red ghost button) → confirmation modal → calls `rejectPurchaseOrder(poId)`

#### Supplier Comparison Modal

When clicking "Compare Suppliers" on a PO:

Table comparing primary vs alternative suppliers:
| | Primary (GlobalTool GmbH) | Alternative (HızlıParça A.Ş.) |
|---|---|---|
| Lead Time (p50) | 14 days | 3 days |
| Lead Time (p90) | 21 days | 5 days |
| Delivery Feasible | ❌ No | ✅ Yes |
| Unit Cost | $45.00 | $51.75 (+15%) |
| Reliability | ████████ 85/100 | ██████ 72/100 |
| In Stock Prob. | 60% | 90% |
| **Score** | 52 | 78 ⭐ |

"Switch to Alternative" button → updates PO.

### 3. Suppliers Page (`src/app/(dashboard)/spare-parts/suppliers/page.tsx`)

**API calls:** `getAlternativeSuppliers(partId)` for each part or bulk call

Table of all suppliers with:
- Supplier name
- Parts they supply (count + list on expand)
- Average lead time
- Reliability score (visual bar)
- Primary/Secondary badge
- Cost competitiveness indicator

## Mock Data

### `src/services/mock/spareParts.ts`

**Spare Parts Catalog** (15-20 parts):
- Realistic Turkish/international industrial names: "Insert Tip A-12", "Spindle Bearing XR-9", "Coolant Nozzle CN-4", "Tool Holder TH-7", etc.
- Criticality mix: 15% A_vital, 35% B_essential, 50% C_desirable
- Compatible wear types mapped to MATWI types

**Inventory Snapshots**: current stock for each part, some below reorder point

**Part Tickets** (20-30 tickets):
- Mix of statuses and risk levels
- At least 3 crisis-level, 5 at-risk, 8 watch
- Linked to machines and parts

**Purchase Orders** (8-10):
- Mix of draft, ready_for_review, approved
- 3-4 in ready_for_review with critical urgency
- Realistic costs in USD

### `src/services/mock/suppliers.ts`

**Suppliers** (10-12):
- Mix of Turkish and international: "KES-Tedarik A.Ş.", "GlobalTool GmbH", "HızlıParça A.Ş.", "PrecisionParts Ltd", etc.
- Varying reliability, lead times, costs
- Some parts with single supplier (high risk)

## Deliverables

- [ ] Spare parts crisis dashboard with stats, tickets, inventory grid
- [ ] Crisis score breakdown component
- [ ] Purchase order review page with approve/reject
- [ ] Supplier comparison modal
- [ ] Suppliers listing page
- [ ] Alternative supplier badges and indicators
- [ ] Realistic mock data for parts, inventory, tickets, POs, suppliers
- [ ] Optimistic UI updates on PO approve/reject
- [ ] Toast feedback for all actions
- [ ] Responsive layout
