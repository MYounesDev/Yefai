# Yefai Frontend — Build Prompt Overview

> **Goal:** Build a world-class, production-grade Next.js frontend for the **Yefai Predictive Maintenance Platform** — a **B2B SaaS** application with multi-organization support and role-based access control.  
> The backend is NOT ready. All API calls go through `services/api.ts` — if the request fails AND we're in dev mode, the function transparently falls back to realistic mock data so every page works out of the box.

---

## B2B SaaS Architecture

Yefai is a **multi-tenant B2B SaaS platform**. Each customer is an **Organization** (e.g., a factory). Users can belong to multiple organizations with different roles and switch between them.

### Role Hierarchy & Permissions

| Role | Scope | Description | Key Permissions |
|------|-------|-------------|----------------|
| **Admin** | Platform | App developers / platform operators. Default system role. | Create/manage organizations, assign Managers, view platform analytics. **Cannot** access organization data (anomalies, predictions, etc.) unless the org opens a tech support ticket. |
| **Manager** | Organization | Organization owner / factory manager. | Full access within their org: view all dashboards, manage members (add/remove with any role including Manager), configure org settings, view/approve POs, access chatbot, manage notifications. |
| **Operator** | Organization | Machine operator on the production floor. | View dashboard, anomalies, predictions, real-time alerts. Use RAG chatbot. Receive notifications. **Cannot** approve POs, manage members, or change settings. |
| **Technician** | Organization | Maintenance engineer / technician. | Everything Operator can do, plus: mark anomalies as reviewed/resolved, view spare parts details, view PO status (but not approve/reject), add maintenance notes. |
| **Procurement** | Organization | Purchasing / supply chain staff. | View spare parts crisis dashboard, approve/reject POs, manage suppliers, view inventory. Can view anomaly summaries (read-only) for context. **Cannot** manage members or system settings. |
| **Viewer** | Organization | Read-only stakeholder (e.g., executive, auditor). | View-only access to all dashboards, reports, and charts. **Cannot** take any actions (no approve, no trigger, no mark). |

### Permission Matrix

| Feature | Admin | Manager | Operator | Technician | Procurement | Viewer |
|---------|-------|---------|----------|------------|-------------|--------|
| Platform org management | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View dashboard & stats | ❌¹ | ✅ | ✅ | ✅ | 📊² | ✅ |
| View anomalies | ❌¹ | ✅ | ✅ | ✅ | 📊² | ✅ |
| Mark anomaly reviewed | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| View predictions | ❌¹ | ✅ | ✅ | ✅ | 📊² | ✅ |
| Recalculate prediction | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| View spare parts/crisis | ❌¹ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Approve/reject POs | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Manage suppliers | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Use RAG chatbot | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View notifications | ❌¹ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Trigger test notification | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage org members | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Org settings | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| System settings (platform) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

> ¹ Admin cannot access org data unless support ticket grants temporary access.  
> ² Procurement sees summary/read-only versions of anomaly and prediction data for context.

### Multi-Organization Switching

- A user can belong to **multiple organizations** with **different roles** in each.
- **Org Switcher** component in the sidebar/topbar allows instant switching.
- When switching orgs, all data (dashboard, anomalies, predictions, etc.) reloads for the selected org.
- Current org is stored in Zustand store and passed as `X-Organization-Id` header in API requests.
- URL structure is org-aware: data queries are scoped by the active org.
- The switcher shows: org name, org logo/avatar, user's role in that org, online status indicator.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Next.js 16 (App Router) | Pages, routing, layouts |
| **Styling** | Tailwind CSS v4 | Utility-first styling |
| **Animations** | Framer Motion | Page transitions, micro-interactions, staggered reveals |
| **3D / WebGL** | Three.js + React Three Fiber + Drei | Landing page hero, 3D machine visualizations |
| **Charts** | Recharts | Time-series graphs, wear projections, bar charts |
| **Data Fetching** | TanStack React Query v5 + Axios | Caching, retries, optimistic updates |
| **State** | Zustand | Global UI state (sidebar, theme, notifications) |
| **Icons** | Lucide React | Consistent icon set |
| **Fonts** | Google Fonts — Inter (body) + Space Grotesk (headings) | Modern, premium typography |
| **Toast / Feedback** | Sonner | Animated toast notifications |
| **Skeleton / Loading** | Custom + Framer Motion | Shimmer loading skeletons |

---

## Design System Principles

1. **Dark-first theme** — Deep navy/charcoal base (`#0A0E1A`, `#111827`) with electric accent palette (cyan `#06B6D4`, violet `#8B5CF6`, amber `#F59E0B`, rose `#F43F5E`)
2. **Glassmorphism** — Frosted glass cards with `backdrop-blur`, subtle borders (`border-white/10`), soft inner glow
3. **Depth & Layers** — CSS 3D transforms, perspective cards, parallax scroll layers, floating elements
4. **Intentional whitespace** — Generous padding, breathing room between sections
5. **Micro-interactions everywhere** — Button ripples, magnetic hover, card tilt on hover, staggered list entrance
6. **Motion choreography** — Easing curves that feel natural (`[0.22, 1, 0.36, 1]`), sequential entrance animations, scroll-triggered reveals
7. **Atmospheric backgrounds** — Animated gradient mesh, subtle particle system, noise texture overlays, grid patterns
8. **Accessibility** — `prefers-reduced-motion` respect, proper ARIA labels, focus indicators, keyboard navigation
9. **Responsive-first** — Mobile-first breakpoints, touch-friendly tap targets, adaptive layouts

---

## Project Structure

```
client/
├── public/
│   └── assets/              # Static images, 3D models, textures
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (landing)/       # Landing page (public)
│   │   │   └── page.tsx
│   │   ├── (auth)/          # Auth pages (public)
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx
│   │   │   └── accept-invite/
│   │   │       └── page.tsx # Accept org invitation
│   │   ├── (dashboard)/     # Dashboard layout group (org-scoped)
│   │   │   ├── layout.tsx   # Dashboard shell (sidebar, topbar, org switcher, role guard)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx # Main dashboard overview
│   │   │   ├── anomalies/
│   │   │   │   ├── page.tsx # Anomaly list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx # Anomaly detail
│   │   │   ├── predictions/
│   │   │   │   ├── page.tsx # Factory overview (all machines)
│   │   │   │   └── [machineId]/
│   │   │   │       └── page.tsx # Machine prediction detail
│   │   │   ├── spare-parts/
│   │   │   │   ├── page.tsx       # Spare parts crisis dashboard
│   │   │   │   ├── purchase-orders/
│   │   │   │   │   └── page.tsx   # PO review screen
│   │   │   │   └── suppliers/
│   │   │   │       └── page.tsx   # Supplier comparison
│   │   │   ├── chat/
│   │   │   │   └── page.tsx # RAG chatbot
│   │   │   ├── notifications/
│   │   │   │   └── page.tsx # Notification logs
│   │   │   ├── members/
│   │   │   │   └── page.tsx # Org member management (Manager only)
│   │   │   └── settings/
│   │   │       └── page.tsx # Org settings (Manager only)
│   │   ├── (admin)/         # Platform admin panel (Admin role only)
│   │   │   ├── layout.tsx   # Admin layout (different sidebar)
│   │   │   ├── organizations/
│   │   │   │   ├── page.tsx       # Org list + create
│   │   │   │   └── [orgId]/
│   │   │   │       └── page.tsx   # Org detail + assign manager
│   │   │   ├── users/
│   │   │   │   └── page.tsx       # All platform users
│   │   │   ├── support-tickets/
│   │   │   │   └── page.tsx       # Tech support tickets
│   │   │   └── platform-settings/
│   │   │       └── page.tsx       # Platform-wide settings
│   │   ├── layout.tsx       # Root layout (providers, fonts, auth)
│   │   └── globals.css      # Tailwind + custom CSS
│   ├── components/
│   │   ├── ui/              # Primitive UI (Button, Card, Badge, Input, Modal, Skeleton, etc.)
│   │   ├── charts/          # Recharts wrappers (WearProjectionChart, AnomalyScoreChart, etc.)
│   │   ├── 3d/              # Three.js / R3F components (HeroScene, MachineModel, ParticleField)
│   │   ├── auth/            # AuthGuard, RoleGuard, OrgSwitcher, LoginForm, InviteAccept
│   │   ├── dashboard/       # Dashboard-specific composites (Sidebar, TopBar, StatsCard, etc.)
│   │   ├── admin/           # Admin panel composites (OrgTable, UserTable, TicketCard, etc.)
│   │   ├── landing/         # Landing page sections (Hero, Features, Demo, CTA)
│   │   └── shared/          # Layout wrappers, PageTransition, AnimatedCounter, etc.
│   ├── services/
│   │   ├── api.ts           # ★ Central API layer — axios + dev mock fallback
│   │   └── mock/
│   │       ├── auth.ts      # Mock auth, users, orgs, roles
│   │       ├── dashboard.ts
│   │       ├── anomalies.ts
│   │       ├── predictions.ts
│   │       ├── spareParts.ts
│   │       ├── chat.ts
│   │       ├── notifications.ts
│   │       └── suppliers.ts
│   ├── hooks/               # Custom hooks (useAuth, useOrg, useAnomaly, usePrediction, etc.)
│   ├── store/               # Zustand stores (authStore, orgStore, uiStore)
│   ├── types/               # TypeScript interfaces (User, Org, Role, API responses, domain models)
│   ├── lib/
│   │   ├── utils.ts         # cn, formatters, constants
│   │   └── permissions.ts   # Role-permission mapping, hasPermission(), canAccess() helpers
│   └── config/
│       └── index.ts         # Environment config (API_BASE_URL, IS_DEV, etc.)
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
└── package.json
```

---

## API Layer Strategy (`services/api.ts`)

### Core Pattern

```typescript
import axios, { AxiosError } from 'axios';
import { config } from '@/config';
import { useAuthStore } from '@/store/authStore';
import { useOrgStore } from '@/store/orgStore';

const apiClient = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor: attach auth token + active org ID to every request
apiClient.interceptors.request.use((cfg) => {
  const token = useAuthStore.getState().token;
  const activeOrgId = useOrgStore.getState().activeOrgId;
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  if (activeOrgId) cfg.headers['X-Organization-Id'] = activeOrgId;
  return cfg;
});

// Generic wrapper: try real API → catch → if dev mode, return mock
async function apiCall<T>(
  requestFn: () => Promise<T>,
  mockFn: () => T | Promise<T>,
  endpoint: string
): Promise<T> {
  try {
    return await requestFn();
  } catch (error) {
    if (config.IS_DEV) {
      console.warn(`[DEV MOCK] ${endpoint} — API failed, using mock data`);
      return await mockFn();
    }
    throw error;
  }
}
```

### Rules
1. **Every API function** is defined in `services/api.ts` and exported by name
2. **Every function** calls `apiCall()` with the real axios request AND a mock fallback
3. **Mock data files** live in `services/mock/` — realistic, matching the backend response shape
4. **Pages and hooks** import ONLY from `services/api.ts` — never from mock files directly
5. **`config.IS_DEV`** is derived from `process.env.NODE_ENV === 'development'`
6. All mock data should look realistic — Turkish company names, real-looking sensor values, plausible timestamps
7. **Auth token** is attached via interceptor from `authStore` — no manual passing needed
8. **Active org ID** is attached via `X-Organization-Id` header — all org-scoped data is filtered server-side

---

## Phase Breakdown

| Phase | Document | Focus |
|-------|----------|-------|
| **Phase 1** | `01a-foundation.md` | Project setup, design system, layout shell, providers, api.ts skeleton |
| **Phase 1.5** | `01b-auth-and-rbac.md` | Auth pages, multi-org switching, role guards, admin panel, member management |
| **Phase 2** | `02-landing-page.md` | 3D landing page with hero scene, features, demo section, CTA |
| **Phase 3** | `03-dashboard-core.md` | Dashboard layout, overview page, real-time stats, anomaly list |
| **Phase 4** | `04-anomaly-detail.md` | Anomaly detail page, image viewer, sensor charts, anomaly score |
| **Phase 5** | `05-predictions.md` | Wear prediction page, projection charts, factory overview, scenarios |
| **Phase 6** | `06-spare-parts-crisis.md` | Spare parts crisis dashboard, PO review, supplier comparison |
| **Phase 7** | `07-rag-chatbot.md` | RAG chatbot page, streaming messages, image cards, session history |
| **Phase 8** | `08-notifications-settings.md` | Notification center, webhook logs, settings page |
| **Phase 9** | `09-polish.md` | Final polish — page transitions, loading states, responsive QA, performance |

---

*Each phase document contains the complete prompt needed to implement that phase independently.*
