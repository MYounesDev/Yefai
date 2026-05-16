# Phase 1.5 — Authentication, Multi-Org & Role-Based Access Control

> Build the complete auth system, multi-organization switching, role-based guards, admin panel, and member management. This is the B2B SaaS backbone.

## Context

Yefai is a **B2B SaaS** platform. Organizations (factories) subscribe to the platform. Users belong to one or more organizations with different roles. The platform admin creates organizations and assigns initial managers.

### Roles Recap

| Role | Scope | Access Level |
|------|-------|-------------|
| **Admin** | Platform | Manages orgs. Cannot see org data unless support ticket. |
| **Manager** | Org | Full org access. Manages members (can add any role, including Manager). |
| **Operator** | Org | Views dashboard, anomalies, predictions, chatbot. No spare parts, no PO, no settings. |
| **Technician** | Org | Operator + mark anomalies reviewed, view spare parts, add notes. No PO approve. |
| **Procurement** | Org | Spare parts, POs (approve/reject), suppliers. Read-only anomaly summaries. |
| **Viewer** | Org | Read-only access to everything. Cannot take any action. |

---

## Task

### 1. Auth API Endpoints in `api.ts`

Add these to `services/api.ts` (all with `apiCall` + mock fallback):

```typescript
// ===== AUTH =====
export async function login(email: string, password: string)
  // POST /api/auth/login → { user, token, organizations: [{ org, role }] }

export async function register(data: { name, email, password })
  // POST /api/auth/register → { user, token }

export async function logout()
  // POST /api/auth/logout

export async function getCurrentUser()
  // GET /api/auth/me → { user, organizations: [{ org_id, org_name, role, logo_url }] }

export async function forgotPassword(email: string)
  // POST /api/auth/forgot-password

export async function resetPassword(token: string, newPassword: string)
  // POST /api/auth/reset-password

export async function acceptInvitation(inviteToken: string)
  // POST /api/auth/accept-invite → { user, org, role }

// ===== ORGANIZATIONS =====
export async function getMyOrganizations()
  // GET /api/organizations → [{ id, name, logo_url, role, member_count, plan }]

export async function switchOrganization(orgId: string)
  // POST /api/organizations/switch → { org, role, token }
  // Updates active org in store

export async function getOrganizationDetails(orgId: string)
  // GET /api/organizations/{orgId} → { id, name, settings, plan, created_at }

export async function updateOrganization(orgId: string, data: Partial<Organization>)
  // PATCH /api/organizations/{orgId}

// ===== MEMBERS (Org-scoped, Manager only) =====
export async function getOrgMembers(orgId: string)
  // GET /api/organizations/{orgId}/members → [{ user_id, name, email, role, joined_at, status }]

export async function inviteMember(orgId: string, data: { email, role })
  // POST /api/organizations/{orgId}/members/invite

export async function updateMemberRole(orgId: string, userId: string, role: string)
  // PATCH /api/organizations/{orgId}/members/{userId} → { role }

export async function removeMember(orgId: string, userId: string)
  // DELETE /api/organizations/{orgId}/members/{userId}

// ===== ADMIN (Platform-level, Admin only) =====
export async function adminListOrganizations(params?: { page, search, plan })
  // GET /api/admin/organizations

export async function adminCreateOrganization(data: { name, plan, manager_email })
  // POST /api/admin/organizations

export async function adminGetOrganization(orgId: string)
  // GET /api/admin/organizations/{orgId} → org details + member list + usage stats

export async function adminListUsers(params?: { page, search, role })
  // GET /api/admin/users

export async function adminListSupportTickets(params?: { status })
  // GET /api/admin/support-tickets

export async function adminResolveSupportTicket(ticketId: string, resolution: string)
  // POST /api/admin/support-tickets/{ticketId}/resolve

export async function adminGetPlatformStats()
  // GET /api/admin/stats → { total_orgs, total_users, active_orgs, tickets_open }
```

### 2. Types (`src/types/auth.ts`)

```typescript
type Role = 'admin' | 'manager' | 'operator' | 'technician' | 'procurement' | 'viewer';

interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  created_at: string;
}

interface UserWithOrgs extends User {
  organizations: OrgMembership[];
}

interface OrgMembership {
  org_id: string;
  org_name: string;
  org_logo_url?: string;
  role: Role;
  joined_at: string;
}

interface Organization {
  id: string;
  name: string;
  logo_url?: string;
  plan: 'free' | 'pro' | 'enterprise';
  member_count: number;
  created_at: string;
  settings?: OrgSettings;
}

interface OrgSettings {
  notification_channels: { telegram: boolean; email: boolean; sms: boolean };
  critical_threshold_hours: number;
  crisis_score_threshold: number;
  refresh_interval_seconds: number;
}

interface OrgMember {
  user_id: string;
  name: string;
  email: string;
  avatar_url?: string;
  role: Role;
  joined_at: string;
  status: 'active' | 'invited' | 'disabled';
  last_active?: string;
}

interface SupportTicket {
  id: string;
  org_id: string;
  org_name: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  created_at: string;
  resolved_at?: string;
  resolution?: string;
}
```

### 3. Permissions Module (`src/lib/permissions.ts`)

Central permission logic:

```typescript
import { Role } from '@/types/auth';

// Define permissions as string constants
export type Permission =
  | 'view:dashboard' | 'view:anomalies' | 'action:mark_anomaly_reviewed'
  | 'view:predictions' | 'action:recalculate_prediction'
  | 'view:spare_parts' | 'action:approve_po' | 'action:manage_suppliers'
  | 'view:chat' | 'view:notifications' | 'action:trigger_notification'
  | 'manage:members' | 'manage:org_settings'
  | 'admin:manage_orgs' | 'admin:manage_users' | 'admin:view_tickets' | 'admin:platform_settings';

// Role → Permission mapping
const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: ['admin:manage_orgs', 'admin:manage_users', 'admin:view_tickets', 'admin:platform_settings'],
  manager: [/* all org permissions */],
  operator: ['view:dashboard', 'view:anomalies', 'view:predictions', 'view:chat', 'view:notifications'],
  technician: ['view:dashboard', 'view:anomalies', 'action:mark_anomaly_reviewed', 'view:predictions', 'action:recalculate_prediction', 'view:spare_parts', 'view:chat', 'view:notifications'],
  procurement: ['view:spare_parts', 'action:approve_po', 'action:manage_suppliers', 'view:notifications'],
  viewer: ['view:dashboard', 'view:anomalies', 'view:predictions', 'view:spare_parts', 'view:notifications'],
};

export function hasPermission(role: Role, permission: Permission): boolean { ... }
export function canAccessRoute(role: Role, pathname: string): boolean { ... }
export function getNavItems(role: Role): NavItem[] { ... }  // Returns only nav items the role can see
```

### 4. Zustand Stores

#### `src/store/authStore.ts`

```typescript
interface AuthState {
  user: UserWithOrgs | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email, password) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;  // Called on app init, checks stored token
}
```

#### `src/store/orgStore.ts`

```typescript
interface OrgState {
  activeOrgId: string | null;
  activeOrg: Organization | null;
  activeRole: Role | null;
  organizations: OrgMembership[];
  switchOrg: (orgId: string) => void;  // Updates active org + role, triggers data refetch
  setOrganizations: (orgs: OrgMembership[]) => void;
}
```

### 5. Guard Components (`src/components/auth/`)

#### `AuthGuard`
- Wraps protected routes. Checks `isAuthenticated` from `authStore`.
- If not authenticated → redirect to `/login`.
- Shows loading spinner while checking auth state.

#### `RoleGuard`
- Wraps route content. Accepts `allowedRoles: Role[]` or `requiredPermission: Permission`.
- If user's active role doesn't match → shows "Access Denied" page (403-style, glass card, lock icon, "You don't have permission to view this page").
- Used in layout files to protect entire route groups.

#### `OrgSwitcher`
- Dropdown/popover in sidebar or topbar.
- Shows current org (name + logo/avatar + role badge).
- Click → expands list of user's organizations.
- Each org: name, logo, role badge (color-coded by role), member count.
- Click org → calls `switchOrg()` → all React Query caches invalidate → data reloads.
- Animated transition (Framer Motion) on switch.
- If user has only one org, show it but disable the dropdown.

### 6. Auth Pages (`src/app/(auth)/`)

All auth pages share a clean layout: centered card on animated gradient background (similar to landing page atmosphere), Yefai logo at top.

#### Login Page (`login/page.tsx`)
- Email + password inputs (glass styled)
- "Remember me" checkbox
- "Login" button (cyan, full width, loading state)
- "Forgot password?" link
- "Don't have an account? Register" link
- Error handling: invalid credentials toast, validation errors inline
- On success: redirect to `/dashboard` (or to org selection if multiple orgs)

#### Register Page (`register/page.tsx`)
- Name, email, password, confirm password
- Password strength indicator (animated bar: red → amber → green)
- "Register" button
- "Already have an account? Login" link
- On success: redirect to login with "Check your email" message

#### Forgot Password Page (`forgot-password/page.tsx`)
- Email input
- "Send Reset Link" button
- Success message: "If an account exists, you'll receive a reset link"
- Back to Login link

#### Accept Invite Page (`accept-invite/page.tsx`)
- Shown when user clicks invite link from email
- Shows: org name, role they're being invited as
- If user exists: "Accept Invitation" button → login → redirect to new org
- If new user: mini registration form + accept

### 7. Admin Panel (`src/app/(admin)/`)

Completely separate layout from dashboard. Different sidebar with admin-specific navigation.

#### Admin Layout (`layout.tsx`)
- **Admin Sidebar** (distinctive from dashboard — different accent color, e.g., violet instead of cyan):
  - Nav items: Organizations, Users, Support Tickets, Platform Settings
  - "Switch to Org View" button (if admin is also a member of an org)
- **Admin TopBar**: "Admin Panel" label, platform stats summary, user menu

#### Organizations Page (`organizations/page.tsx`)
- **Stats bar**: Total orgs, active orgs, total users, revenue (mock)
- **"Create Organization"** button → modal with: org name, plan (free/pro/enterprise), initial manager email
- **Org table**: name, plan badge, member count, created date, status (active/suspended), actions (View, Suspend)
- Search + filter by plan
- Click org → org detail page

#### Organization Detail (`organizations/[orgId]/page.tsx`)
- Org info card: name, plan, created date, status
- **Member list**: table with name, email, role badge, joined date, last active, actions (Change Role, Remove — but NOT access to org data)
- **Usage stats**: mock — anomalies detected, predictions made, POs created
- **"Assign Manager"** button → email input, sends invitation
- ⚠️ Clear banner: "You are viewing organization metadata only. You cannot access factory data, anomalies, or predictions."

#### Users Page (`users/page.tsx`)
- Table of all platform users
- Columns: name, email, organizations (count + list tooltip), role(s), registered date, last active
- Search + filter by role
- Actions: View profile, Disable account (confirmation modal)

#### Support Tickets Page (`support-tickets/page.tsx`)
- Table of tickets from organizations
- Columns: ticket ID, org name, subject, status badge (open/in_progress/resolved/closed), created date
- Click → ticket detail modal: full description, conversation thread (mock), "Resolve" button with resolution text area
- Status filter pills: All / Open / In Progress / Resolved

#### Platform Settings Page (`platform-settings/page.tsx`)
- API configuration display
- Default org settings template
- Platform-wide notification settings
- System health overview
- Mostly read-only displays for demo

### 8. Member Management Page (`src/app/(dashboard)/members/page.tsx`)

**Access**: Manager role only (RoleGuard wraps this page).

- **"Invite Member"** button → modal:
  - Email input
  - Role dropdown (Manager, Operator, Technician, Procurement, Viewer)
  - Role descriptions shown on selection
  - "Send Invitation" button → toast "Invitation sent to user@email.com"
- **Member table**:
  - Avatar + name + email
  - Role badge (color-coded: Manager=violet, Operator=cyan, Technician=amber, Procurement=emerald, Viewer=gray)
  - Status: Active (green dot) / Invited (amber dot) / Disabled (gray dot)
  - Joined date
  - Last active (relative time)
  - **Actions**:
    - "Change Role" → dropdown, confirmation dialog ("Change Ahmet's role from Operator to Technician?")
    - "Remove" → confirmation dialog with warning ("This will revoke access to the organization")
- **Role summary cards** (top): count by role with icon

### 9. Org Settings Page Update (`src/app/(dashboard)/settings/page.tsx`)

This page is Manager-only. Update from Phase 8 to be scoped to org:

- **Organization Info**: name, logo upload (mock), plan badge
- **Notification Settings**: per-org channel toggles, threshold sliders
- **AI Settings**: per-org model config (read-only for now)
- **Danger Zone**: "Leave Organization" (for non-owners), "Delete Organization" (owner only, confirmation modal)

### 10. Sidebar Navigation Updates

The sidebar in dashboard layout should be **role-aware**. Use `getNavItems(role)` from `permissions.ts`:

| Nav Item | Visible For |
|----------|-------------|
| Dashboard | Manager, Operator, Technician, Viewer |
| Anomalies | Manager, Operator, Technician, Viewer, Procurement (read-only) |
| Predictions | Manager, Operator, Technician, Viewer |
| Spare Parts | Manager, Technician, Procurement, Viewer |
| Chat | Manager, Operator, Technician |
| Notifications | All org roles |
| Members | Manager only |
| Settings | Manager only |

Items the role can't see → simply hidden from sidebar. Direct URL access → RoleGuard shows 403.

### 11. TopBar Updates

- **Org Switcher** (left area, next to breadcrumb or above it):
  - Current org avatar + name + role badge
  - Click → dropdown with org list
- **User Menu** (right area):
  - User avatar + name
  - Dropdown: My Profile, My Organizations, Logout
  - If user is Admin: "Admin Panel" link in dropdown

### 12. Mock Data (`src/services/mock/auth.ts`)

```typescript
// Mock current user with multiple org memberships
export const mockCurrentUser: UserWithOrgs = {
  id: 'usr_001',
  name: 'Ahmet Yılmaz',
  email: 'ahmet@yefai.io',
  avatar_url: null,
  created_at: '2026-01-15T10:00:00Z',
  organizations: [
    { org_id: 'org_001', org_name: 'Yılmaz Makina A.Ş.', role: 'manager', joined_at: '2026-01-15' },
    { org_id: 'org_002', org_name: 'Demir Çelik Fabrikası', role: 'operator', joined_at: '2026-03-01' },
    { org_id: 'org_003', org_name: 'Anadolu CNC', role: 'viewer', joined_at: '2026-04-20' },
  ],
};

// Mock admin user
export const mockAdminUser: UserWithOrgs = {
  id: 'usr_admin',
  name: 'Platform Admin',
  email: 'admin@yefai.io',
  organizations: [],  // Admin has no org membership by default
};

// Mock organizations (for admin panel)
// 5-6 orgs with Turkish names, different plans, member counts

// Mock org members (for member management page)
// 8-10 members per org with mixed roles

// Mock support tickets
// 5-8 tickets with mixed statuses
```

In dev mode, `login()` accepts any email. If email contains "admin" → returns admin user. Otherwise → returns regular user with 3 org memberships. This lets developers test both flows.

## Deliverables

- [ ] Auth API functions in `api.ts` with mock fallbacks
- [ ] Auth types (User, Role, Organization, OrgMember, etc.)
- [ ] Permissions module (`lib/permissions.ts`)
- [ ] Auth store (Zustand) + Org store (Zustand)
- [ ] AuthGuard + RoleGuard + OrgSwitcher components
- [ ] Login, Register, Forgot Password, Accept Invite pages
- [ ] Admin panel: Organizations, Users, Support Tickets, Platform Settings
- [ ] Member management page (Manager only)
- [ ] Org settings page updates
- [ ] Role-aware sidebar navigation
- [ ] TopBar with org switcher + user menu
- [ ] Mock auth data (users, orgs, members, tickets)
- [ ] Axios interceptor for auth token + org ID headers
- [ ] All pages protected by AuthGuard, role-restricted pages by RoleGuard
- [ ] App compiles and runs, login flow works with mock data
