# Phase 8 — Notifications & Settings

> Notification center with webhook logs, and system settings page.
> 
> **Role Access:** Notification logs visible to all org roles. "Trigger Test Notification" → Manager only. Settings page → Manager only (RoleGuard). Other roles attempting to access `/settings` see 403.
> **Note:** Settings on this page are **org-level settings** (managed by Manager). Platform-level settings are in the Admin panel (Phase 1.5).

## Pages

### 1. Notifications Page (`src/app/(dashboard)/notifications/page.tsx`)

**API calls:** `getNotificationLogs()`, `triggerAnomalyNotification()`

#### Notification Stats (top)

- Total notifications sent (counter)
- Today's notifications
- Failed deliveries (red if > 0)
- Channels breakdown: Telegram / Email / SMS counts

#### Notification Log Table

Table with columns:
- **Timestamp**: formatted date/time, relative time on hover
- **Type**: Anomaly Alert / Critical Warning / Report / Crisis Alert / PO Notification — badge
- **Channel**: Telegram (blue) / Email (violet) / SMS (amber) — icon + badge
- **Target**: machine/tool reference or part ID
- **Status**: Delivered (green ✓) / Failed (red ✗) / Pending (amber spinner)
- **Payload preview**: truncated, expandable on click
- **Actions**: Retry (if failed), View Detail

Filters: All / Anomaly / Crisis / PO / Report | All Channels / Telegram / Email / SMS | Success / Failed

Expandable row: click to see full webhook payload (formatted JSON in code block, glass-card).

#### Test Notification Panel

Card with:
- Dropdown: select anomaly to test with
- Channel checkboxes: Telegram / Email / SMS
- "Send Test Notification" button → `triggerAnomalyNotification()`
- Response display (success/fail toast)

### 2. Settings Page (`src/app/(dashboard)/settings/page.tsx`)

Organized in sections with glass cards:

#### System Configuration

- **API Base URL**: display (read-only in frontend)
- **Environment**: Development / Production badge
- **Backend Version**: from health check (or "Unavailable")

#### Notification Settings

- Toggle switches for each channel: Telegram / Email / SMS
- Webhook URL display (masked, with copy button)
- Test connection buttons per channel
- Notification thresholds:
  - Critical threshold (hours): slider for "send alert if hours_to_critical < X"
  - Crisis score threshold: slider for "send crisis alert if score > X"

#### AI Model Settings

- Anomalib model status: Loaded / Not Loaded badge
- NovaVision container: Running / Stopped badge
- Jina CLIP v2 status: Ready / Loading badge
- "Reload Models" button (mock)

#### Display Preferences

- Theme: Dark (default) / Light (future — disabled with "Coming Soon" badge)
- Language: English / Turkish (toggle)
- Dashboard refresh interval: 15s / 30s / 60s dropdown
- Animations: Enable / Reduce (respects prefers-reduced-motion)

#### Data Management

- "Clear Cache" button
- "Export All Data" button (mock download)
- "Reset Dashboard" button (confirmation modal)
- Database size indicator (mock: "Supabase: 8.2 MB / 500 MB")

All toggles and sliders: smooth transitions, cyan accent for active state.

## Mock Data (`src/services/mock/notifications.ts`)

**Notification Logs** (30+ entries):
- Mix of types: anomaly alerts, crisis alerts, PO notifications
- Mix of channels: Telegram (50%), Email (30%), SMS (20%)
- Mix of statuses: 85% delivered, 10% failed, 5% pending
- Realistic timestamps (last 48 hours)
- Payload samples matching PUQ AI format from planning docs

## Deliverables

- [ ] Notifications page with stats, log table, test panel
- [ ] Expandable log rows with payload detail
- [ ] Filters for type, channel, status
- [ ] Settings page with all sections
- [ ] Toggle switches, sliders, dropdowns with smooth animations
- [ ] Mock notification log data
- [ ] Toast feedback for test notifications and settings changes
- [ ] Responsive layout
