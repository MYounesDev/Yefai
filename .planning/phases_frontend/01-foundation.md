# Phase 1 — Foundation & Design System

> Build the entire foundation: design system, layout, providers, API layer, and reusable UI components.

## Task

### 1. Install Dependencies

```bash
cd client
npm install axios @tanstack/react-query zustand framer-motion recharts lucide-react sonner
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

Add Google Fonts (Inter + Space Grotesk) via `next/font/google`.

### 2. Tailwind Config

Extend with Yefai design tokens:

- **Colors:** background `#0A0E1A`/`#111827`/`#1F2937`, foreground `#F9FAFB`/`#9CA3AF`, accents: cyan `#06B6D4`, violet `#8B5CF6`, amber `#F59E0B`, rose `#F43F5E`, emerald `#10B981`
- **Borders:** `rgba(255,255,255,0.08)` default, `rgba(255,255,255,0.15)` hover
- **Glass:** `rgba(17,24,39,0.6)` / `rgba(17,24,39,0.8)`
- **Fonts:** `sans: Inter`, `heading: Space Grotesk`
- **Shadows:** glass shadow, glow-cyan, glow-violet
- **Keyframes:** shimmer, float, pulse-glow, gradient-shift

### 3. Global CSS

- Tailwind directives, custom scrollbar (thin, dark), selection color (cyan)
- Noise texture overlay, animated gradient mesh background
- Custom utilities: `.glass-card`, `.text-gradient`, `.glow-border`

### 4. Root Layout

- Font imports, QueryClientProvider, Sonner Toaster (dark, bottom-right)
- SEO metadata: title, description

### 5. Config (`src/config/index.ts`)

```typescript
export const config = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  IS_DEV: process.env.NODE_ENV === 'development',
  APP_NAME: 'Yefai',
};
```

### 6. API Layer (`src/services/api.ts`)

Central layer with axios. Pattern:

```typescript
async function apiCall<T>(requestFn, mockFn, endpoint): Promise<T> {
  try { return (await requestFn()).data; }
  catch { if (config.IS_DEV) { console.warn(`[DEV MOCK] ${endpoint}`); return mockFn(); } throw error; }
}
```

Define ALL these exported functions (each uses `apiCall` with real request + mock fallback):

**Dashboard:** `getDashboardOverview()`, `getHealthStatus()`
**Anomalies:** `getAnomalies(params)`, `getAnomalyById(id)`, `runAnomalibPredict(formData)`, `getAnomalibTrainingStatus(jobId)`
**Predictions:** `getPrediction(machineId)`, `getFactoryOverview()`, `recalculatePrediction(machineId)`
**Spare Parts:** `getCrisisScore(imageId)`, `createAutoOrder(ticketId)`, `getAlternativeSuppliers(partId)`, `getPurchaseOrders(params)`, `approvePurchaseOrder(poId)`, `rejectPurchaseOrder(poId)`, `getInventorySnapshots(partId)`, `getSparePartsCatalog()`, `getPartTickets(params)`
**Chat:** `sendChatMessage(sessionId, message)`, `getChatSessions()`, `getChatSessionById(sessionId)`, `searchHybrid(query, filters)`
**Notifications:** `getNotificationLogs(params)`, `triggerAnomalyNotification(anomalyId)`
**Embeddings:** `searchEmbeddings(query, topK)`
**NovaVision:** `getNovaVisionHealth()`, `getNovaVisionModels()`

### 7. Types (`src/types/`)

Define interfaces: `DashboardOverview`, `Anomaly`, `AnomalyDetail`, `Prediction`, `WearScenario`, `MachineStatus`, `FactoryOverview`, `SparePart`, `InventorySnapshot`, `PartTicket`, `PurchaseOrder`, `Supplier`, `ChatMessage`, `ChatSession`, `SearchResult`, `NotificationLog`, `HealthStatus`

### 8. UI Components (`src/components/ui/`)

All with Tailwind + Framer Motion:

- **Button** — primary (cyan gradient), secondary (glass), danger, ghost. Ripple on click. Loading state.
- **Card** — Glass card, hover lift with 3D perspective tilt. Optional glow border.
- **Badge** — cyan/violet/amber/rose/emerald. Pulse for danger.
- **Input** — Glass bg, cyan focus glow, animated float label.
- **Modal** — Animated backdrop + scale-in. AnimatePresence.
- **Skeleton** — Shimmer loading placeholder.
- **Tooltip** — Fade-in, dark glass.
- **ProgressBar** — Animated gradient fill with glow.
- **StatusDot** — Pulsing colored dot.
- **AnimatedCounter** — Spring animation on value change.
- **PageTransition** — Fade-slide entrance for page content.

### 9. Dashboard Layout (`src/app/(dashboard)/layout.tsx`)

- **Sidebar** (collapsible): logo, nav items (Dashboard, Anomalies, Predictions, Spare Parts, Chat, Notifications, Settings) with Lucide icons. Active = cyan accent bar. Smooth width animation.
- **Top Bar** (sticky): breadcrumb, search bar, notification bell with badge, health indicator dots.

### 10. Mock Data Stubs (`src/services/mock/`)

Create stub files: `dashboard.ts`, `anomalies.ts`, `predictions.ts`, `spareParts.ts`, `chat.ts`, `notifications.ts`, `suppliers.ts`. Export typed mock data. Realistic data filled in later phases.

## Deliverables

- All deps installed, Tailwind configured, global CSS, root layout with providers
- Complete `api.ts` with all endpoints + mock fallback
- TypeScript types, UI components, dashboard layout, mock stubs
- App compiles with `npm run dev`
