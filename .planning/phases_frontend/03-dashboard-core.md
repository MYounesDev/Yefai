# Phase 3 — Dashboard Core (Overview + Anomaly List)

> The main dashboard overview page with real-time stats, anomaly feed, and system health. Plus the anomaly list page with filtering and sorting.
> 
> **Role Access:** Dashboard is visible to Manager, Operator, Technician, Viewer. Procurement sees a simplified summary. Admin cannot access.
> **Org-Scoped:** All data on these pages is scoped to the active organization via `X-Organization-Id` header. The org name should appear in the page header.

## Pages

### 1. Dashboard Overview (`src/app/(dashboard)/dashboard/page.tsx`)

**API calls:** `getDashboardOverview()`, `getHealthStatus()`, `getFactoryOverview()`

#### Top Stats Row (4 cards, responsive grid)

Glass cards with icon, label, value, and trend indicator:

1. **Active Anomalies** — count, red/green trend arrow, `AnimatedCounter`
2. **Average Wear Level** — µm value with progress bar (gradient: green → amber → red)
3. **Crisis Alerts** — count of tickets with `risk_level >= at_risk`, pulsing red dot if > 0
4. **System Uptime** — percentage, green StatusDot

Each card: glass-card styling, subtle hover lift, icon with colored background circle.

#### Machine Status Grid (8 machines, responsive)

Grid of machine status cards from `getFactoryOverview()`:

Each card shows:
- Machine name + ID
- Color-coded status dot: 🟢 safe (< 100µm), 🟡 watch (100-160µm), 🟠 warning (160-185µm), 🔴 critical (> 185µm)
- Current wear level (µm) with mini progress bar
- Hours to critical (large, bold)
- Click → navigates to `/predictions/{machineId}`

Framer Motion: staggered entrance, cards flip from 0 opacity/rotateX.

#### Recent Anomalies Feed

List of last 5 anomalies from `getAnomalies({ limit: 5 })`:
- Timestamp, machine/tool ID, anomaly score bar, wear type badge
- Severity badge (Low/Medium/High/Critical — color coded)
- Click → `/anomalies/{id}`
- "View All" link → `/anomalies`
- Auto-refresh every 30s (React Query `refetchInterval`)

#### System Health Panel

Horizontal bar showing service statuses from `getHealthStatus()`:
- Database (Supabase) — StatusDot
- AI Model (Anomalib) — StatusDot
- NovaVision Container — StatusDot
- PUQ AI — StatusDot
- Last check timestamp

#### Quick Actions

Row of action buttons — **role-aware visibility**:
- "Run Inference" (cyan) → opens modal with image upload (**Manager, Technician only**)
- "View Predictions" → `/predictions` (**hidden for Procurement**)
- "Check Spare Parts" → `/spare-parts` (**hidden for Operator**)
- "Open Chat" → `/chat` (**hidden for Procurement, Viewer**)

Use `hasPermission(activeRole, 'view:...')` from `permissions.ts` to conditionally render buttons. For Viewer role, all action buttons should be hidden (they only view).

### 2. Anomaly List Page (`src/app/(dashboard)/anomalies/page.tsx`)

**API calls:** `getAnomalies(params)`

#### Filters Bar (sticky)

- Severity filter: All / Low / Medium / High / Critical (pill buttons, active = filled)
- Wear type filter: All / Flank Wear / Adhesive Wear / Combination (dropdown)
- Date range picker (glass styled)
- Search by machine/tool ID
- Sort: Newest / Oldest / Highest Score / Lowest Score

#### Anomaly Table/Cards

Responsive: table on desktop, card list on mobile.

Table columns:
- Timestamp
- Machine ID + Tool ID
- Anomaly Score (mini bar chart, color graded)
- Wear Type (badge)
- Severity (badge)
- Estimated Wear (µm)
- Status (New / Reviewed / Resolved)
- Actions: View Detail →

Card view (mobile): compact version with same data, stacked.

Framer Motion: rows/cards stagger in on page load and filter change.

#### Pagination

- Page numbers + prev/next
- "Showing X-Y of Z anomalies"

## Mock Data (`src/services/mock/anomalies.ts`)

Generate 50+ realistic anomaly records:
- Spread across 8 machines (Machine-01 through Machine-08)
- Each with tools (Tool-A through Tool-D)
- Realistic timestamps (last 7 days)
- Anomaly scores: 0.1 to 0.98
- Wear types: flank_wear (55%), adhesion (25%), combination (20%)
- Estimated wear: 20-200 µm
- Severity derived from score: < 0.3 Low, 0.3-0.5 Medium, 0.5-0.75 High, > 0.75 Critical

## Mock Data (`src/services/mock/dashboard.ts`)

Dashboard overview with:
- `total_anomalies: 47`, `active_anomalies: 12`, `avg_wear_um: 98.5`, `crisis_count: 3`, `uptime: 99.2`
- Health status: all services "healthy" with timestamps
- NovaVision health/models mock data

## Deliverables

- [ ] Dashboard overview page with stats, machine grid, anomaly feed, health panel
- [ ] Anomaly list page with filters, table/cards, pagination
- [ ] Role-based quick action visibility
- [ ] Org name displayed in page header
- [ ] Realistic mock data for anomalies and dashboard
- [ ] React Query hooks for data fetching with loading/error states
- [ ] Skeleton loading states for all data areas
- [ ] Responsive layout
- [ ] Staggered animations on data load
