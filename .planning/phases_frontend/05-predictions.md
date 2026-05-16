# Phase 5 — Predictions (Wear Forecasting)

> Wear prediction pages: per-machine detailed forecast and factory-wide overview. Core value prop of the platform.

## Pages

### 1. Factory Overview (`src/app/(dashboard)/predictions/page.tsx`)

**API calls:** `getFactoryOverview()`

#### Machine Grid (8 machines)

Large responsive grid (4×2 on desktop, 2×4 on tablet, 1×8 on mobile).

Each machine card:
- Machine name (large, e.g., "Machine #5")
- Status indicator: 🟢 Safe / 🟡 Watch / 🟠 Warning / 🔴 Critical — pulsing dot
- Current wear level: large number + µm unit
- Mini progress bar (0-200µm, gradient green→amber→red)
- **Hours to Critical**: bold number with icon ⏰
- Wear rate: `2.8 µm/hour` with trend arrow (↗ accelerating / → stable / ↘ decelerating)
- Confidence badge: Low/Medium/High
- Mini sparkline chart (last 5 data points, tiny line chart)
- Click → `/predictions/{machineId}`

Card colors shift based on status (subtle border glow: green → amber → red).
Cards animate in with stagger on page load.

#### Summary Bar (top)

- Total machines monitored
- Machines in critical state (count, red highlight)
- Average hours to critical across all machines
- Next scheduled maintenance (mock date)

### 2. Machine Prediction Detail (`src/app/(dashboard)/predictions/[machineId]/page.tsx`)

**API calls:** `getPrediction(machineId)`, `getAnomalies({ machine_id: machineId, limit: 10 })`

#### Header

- Machine name + ID
- Status badge (large, prominent)
- Last updated timestamp
- "Recalculate" button → `recalculatePrediction(machineId)` with loading spinner + toast

#### Current Status Panel

Glass card:
- **Current Wear Level**: large animated counter (145 µm), circular progress gauge
- **Critical Threshold**: 200 µm (red dashed line reference)
- **Wear Rate**: 2.8 µm/hour with trend
- **Hours to Critical**: 20 hours (large, bold, color-coded)
- **Last Inspection**: "15 minutes ago"
- **Confidence**: Medium badge + tooltip explaining (based on r² and data point count)

#### Wear Projection Chart (Recharts — MAIN VISUAL)

Large line chart (`components/charts/WearProjectionChart.tsx`):
- **X-axis**: Time (hours, extending into future)
- **Y-axis**: Wear level (µm, 0-250)
- **Blue solid line**: Historical wear measurements (data points as dots)
- **Blue dashed line (Baseline)**: Linear projection at current rate
- **Red dashed line (Pessimistic)**: +25% wear rate scenario
- **Green dashed line (Optimistic)**: -25% wear rate scenario
- **Red horizontal line**: Critical threshold (200 µm) — labeled
- **Red vertical dashed line**: Predicted critical moment
- **Green vertical line**: Current time — "NOW" label
- **Shaded area**: Confidence band between optimistic and pessimistic (light violet, semi-transparent)
- Interactive tooltip on hover: exact wear value, time, scenario
- Animated draw-in on page load (Recharts animation)

#### 3-Scenario Comparison Table

| Scenario | Wear Rate | Hours to Critical | Projected Date |
|----------|-----------|-------------------|----------------|
| 🔴 Pessimistic (+25%) | 3.5 µm/hr | 16 hours | May 17, 04:00 |
| 🔵 Baseline | 2.8 µm/hr | 20 hours | May 17, 08:00 |
| 🟢 Optimistic (-25%) | 2.1 µm/hr | 27 hours | May 17, 15:00 |

Glass-card table with row highlighting.

#### Wear Type Analysis

Horizontal bar chart showing wear type probabilities:
- Flank Wear: 87% (cyan bar)
- Adhesive Wear: 34% (violet bar)
- Combination: 18% (amber bar)

Framer Motion: bars animate width on mount.

#### Wear Rate Trend (Last 5 Inspections)

Bar chart or horizontal bars:
```
Inspection #8:  ████████████ 120 µm  (rate: 3.1 µm/hr)
Inspection #9:  █████████████ 135 µm  (rate: 2.9 µm/hr)
Inspection #10: █████████████ 142 µm  (rate: 2.8 µm/hr)
Inspection #11: █████████████ 145 µm  (rate: 2.8 µm/hr) ← Current
```

#### Spare Part Readiness (from crisis integration)

Card showing:
- Required part name
- Stock status vs hours to critical
- `hours_to_critical` vs `lead_time_days_p90` comparison bar
- Status: "Stock OK" (green), "Lead time at risk" (amber), "Stockout imminent" (red)
- Link to spare parts page

#### Recommendation Panel

AI-generated recommendation (mock):
- "⚠️ Tool change should be planned within the next shift"
- "📦 Insert Tip A-12 is in stock (3 units). Lead time is not a concern."
- OR "🔴 Critical: Part out of stock. Auto-PO generated. Alternative supplier available."

## Mock Data (`src/services/mock/predictions.ts`)

Generate for 8 machines:
- Each with unique wear levels, rates, confidence
- Historical data points (10-15 per machine)
- 3 scenario projections
- Wear type probabilities
- Different status levels (2 critical, 2 warning, 1 watch, 3 safe)

## Deliverables

- [ ] Factory overview page with 8 machine cards
- [ ] Machine prediction detail page
- [ ] WearProjectionChart component with 3 scenarios
- [ ] Animated counters and gauges
- [ ] Wear type bar chart
- [ ] Wear rate trend visualization
- [ ] Spare part readiness card
- [ ] Recommendation panel
- [ ] Realistic mock prediction data
- [ ] Skeleton loading for all sections
- [ ] Responsive layout
