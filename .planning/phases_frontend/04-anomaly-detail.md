# Phase 4 — Anomaly Detail Page

> Deep-dive page for a single anomaly: image viewer, sensor data charts, anomaly heatmap, wear analysis, and linked spare part info.

## Page: `src/app/(dashboard)/anomalies/[id]/page.tsx`

**API calls:** `getAnomalyById(id)`, `getCrisisScore(imageId)`, `getPrediction(machineId)`

## Layout (2-column on desktop, stacked on mobile)

### Left Column (60%)

#### Image Viewer

- Large anomaly image with zoom capability (click to enlarge in modal)
- Overlay: anomaly heatmap (semi-transparent red/yellow overlay showing anomaly regions)
- Toggle button: "Show/Hide Heatmap"
- Image metadata below: filename, set, timestamp, resolution
- Framer Motion: image slides in from left

#### Sensor Data Charts (Recharts)

Tabbed chart section (tabs: Accelerometer, Acoustic, Force X, Force Y, Force Z):
- Line chart showing sensor readings over the machining pass
- Highlighted region where anomaly was detected
- Tooltip on hover showing exact values
- Each chart: glass-card container, smooth line, gradient area fill (cyan → transparent)

### Right Column (40%)

#### Anomaly Summary Card

Glass card with:
- **Anomaly Score**: large circular gauge (SVG animated), color-coded (green → amber → red)
- **Severity**: badge (Critical/High/Medium/Low)
- **Wear Type**: primary type with probability bar, secondary types listed
  - e.g., Flank Wear ████████████████████ 87%
  - Adhesive Wear ██████████ 34%
  - Combination ██████ 18%
- **Estimated Wear**: XX µm / 200 µm critical threshold — progress bar
- **Machine/Tool ID**: linked to prediction page
- **Timestamp**: formatted date/time
- **Set**: MATWI set reference

#### Prediction Preview Card

Mini version of the prediction panel:
- Hours to critical: large bold number with color
- Wear rate: µm/hour
- Trend: accelerating ↗ / stable → / decelerating ↘
- "View Full Prediction →" link to `/predictions/{machineId}`

#### Spare Part Impact Card

From `getCrisisScore(imageId)`:
- Required part name + part ID
- Current stock: `on_hand` / `reorder_point`
- Stock status badge: In Stock (green), Low (amber), Out of Stock (red)
- Crisis score: 0-100 with color bar
- Risk level badge: none/watch/at_risk/crisis
- If crisis: "Auto PO Created" badge with PO link
- "View Spare Parts →" link to `/spare-parts`

#### Actions Panel

- "Trigger Notification" button → calls `triggerAnomalyNotification(id)`, shows toast
- "Recalculate Prediction" button → calls `recalculatePrediction(machineId)`
- "Download Report" button (mock — generates summary text)
- "Mark as Reviewed" toggle button

## Mock Data (`src/services/mock/anomalies.ts`)

Extend with detailed anomaly data:
- Full sensor data arrays (100-200 data points per sensor channel)
- Image path (use placeholder or generated image)
- Anomaly heatmap data points
- Wear type probabilities
- Linked machine/tool IDs

## Deliverables

- [ ] Anomaly detail page with two-column layout
- [ ] Image viewer with heatmap overlay toggle
- [ ] Sensor data tabbed charts (5 channels)
- [ ] Anomaly score gauge (animated SVG)
- [ ] Wear type probability bars
- [ ] Prediction preview card
- [ ] Spare part impact card with crisis score
- [ ] Action buttons with API calls + toast feedback
- [ ] Skeleton loading for all sections
- [ ] Responsive stacking on mobile
