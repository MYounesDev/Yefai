# Phase 1 — Foundation & Design System

> Build the entire foundation: design system, layout, providers, API layer, and reusable UI components.
> **Note:** This is a B2B SaaS app with multi-org support and RBAC. Auth pages, role guards, admin panel, and member management are in **Phase 1.5 (`01b-auth-and-rbac.md`)**. This phase sets up the skeleton; Phase 1.5 builds the auth system on top.

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

**Auth:** `login(email, password)`, `register(data)`, `logout()`, `getCurrentUser()`, `forgotPassword(email)`, `resetPassword(token, password)`, `acceptInvitation(inviteToken)`
**Organizations:** `getMyOrganizations()`, `switchOrganization(orgId)`, `getOrganizationDetails(orgId)`, `updateOrganization(orgId, data)`
**Members:** `getOrgMembers(orgId)`, `inviteMember(orgId, data)`, `updateMemberRole(orgId, userId, role)`, `removeMember(orgId, userId)`
**Admin:** `adminListOrganizations(params)`, `adminCreateOrganization(data)`, `adminGetOrganization(orgId)`, `adminListUsers(params)`, `adminListSupportTickets(params)`, `adminResolveSupportTicket(ticketId, resolution)`, `adminGetPlatformStats()`
**Dashboard:** `getDashboardOverview()`, `getHealthStatus()`
**Anomalies:** `getAnomalies(params)`, `getAnomalyById(id)`, `runAnomalibPredict(formData)`, `getAnomalibTrainingStatus(jobId)`
**Predictions:** `getPrediction(machineId)`, `getFactoryOverview()`, `recalculatePrediction(machineId)`
**Spare Parts:** `getCrisisScore(imageId)`, `createAutoOrder(ticketId)`, `getAlternativeSuppliers(partId)`, `getPurchaseOrders(params)`, `approvePurchaseOrder(poId)`, `rejectPurchaseOrder(poId)`, `getInventorySnapshots(partId)`, `getSparePartsCatalog()`, `getPartTickets(params)`
**Chat:** `sendChatMessage(sessionId, message)`, `getChatSessions()`, `getChatSessionById(sessionId)`, `searchHybrid(query, filters)`
**Notifications:** `getNotificationLogs(params)`, `triggerAnomalyNotification(anomalyId)`
**Embeddings:** `searchEmbeddings(query, topK)`
**NovaVision:** `getNovaVisionHealth()`, `getNovaVisionModels()`

The axios instance must have an interceptor that attaches `Authorization: Bearer <token>` from `authStore` and `X-Organization-Id` from `orgStore` on every request.

### 7. Types (`src/types/`)

Define interfaces:

**Auth & Org:** `User`, `UserWithOrgs`, `OrgMembership`, `Organization`, `OrgSettings`, `OrgMember`, `SupportTicket`, `Role` (union type: `'admin' | 'manager' | 'operator' | 'technician' | 'procurement' | 'viewer'`), `Permission`

**Domain:** `DashboardOverview`, `Anomaly`, `AnomalyDetail`, `Prediction`, `WearScenario`, `MachineStatus`, `FactoryOverview`, `SparePart`, `InventorySnapshot`, `PartTicket`, `PurchaseOrder`, `Supplier`, `ChatMessage`, `ChatSession`, `SearchResult`, `NotificationLog`, `HealthStatus`

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

### 9. Zustand Stores (`src/store/`)

- **`authStore.ts`** — `user`, `token`, `isAuthenticated`, `isLoading`, `login()`, `logout()`, `loadUser()`
- **`orgStore.ts`** — `activeOrgId`, `activeOrg`, `activeRole`, `organizations`, `switchOrg()`, `setOrganizations()`
- **`uiStore.ts`** — `sidebarCollapsed`, `theme`, `toggleSidebar()`

### 10. Permissions (`src/lib/permissions.ts`)

- Define `Permission` type and `ROLE_PERMISSIONS` mapping
- Export `hasPermission(role, permission)`, `canAccessRoute(role, pathname)`, `getNavItems(role)`
- Sidebar nav items are filtered by the user's active role via `getNavItems()`

### 11. Dashboard Layout (`src/app/(dashboard)/layout.tsx`)

- **Sidebar** (collapsible): logo, **Org Switcher** at top (current org + role badge, click to switch), **role-aware nav items** (only items the active role has permission for) with Lucide icons. Active = cyan accent bar. Smooth width animation. Bottom: user avatar + logout.
- **Top Bar** (sticky): breadcrumb, search bar, notification bell with badge, health indicator dots, user menu dropdown (profile, my orgs, logout, "Admin Panel" if admin).

### 12. Mock Data Stubs (`src/services/mock/`)

Create stub files: `auth.ts`, `dashboard.ts`, `anomalies.ts`, `predictions.ts`, `spareParts.ts`, `chat.ts`, `notifications.ts`, `suppliers.ts`. Export typed mock data. Realistic data filled in later phases.

The `auth.ts` mock should include:
- A default user ("Ahmet Yılmaz") with 3 org memberships and different roles in each
- An admin user for testing admin panel
- `login()` mock that returns admin user if email contains "admin", otherwise returns regular user

## Deliverables

- All deps installed, Tailwind configured, global CSS, root layout with providers
- Complete `api.ts` with all endpoints (auth, org, admin, domain) + mock fallback
- Axios interceptor for auth token + org ID headers
- TypeScript types (auth + domain), permission module
- Zustand stores (auth, org, ui)
- UI components, dashboard layout with org switcher + role-aware nav
- Mock stubs (including auth mock)
- App compiles with `npm run dev`
- **Next:** Proceed to Phase 1.5 for auth pages, role guards, admin panel, and member management
