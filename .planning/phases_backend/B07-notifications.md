# Phase B7 — Notifications Service

> Implement the notification/alerting backend (Phase 3B from ROADMAP.md). Replace the placeholder `routers/notifications.py` with multi-channel notification dispatch (Telegram, email, SMS) via PUQ AI webhooks.

## Task

### 1. Notification Tables

```sql
CREATE TABLE IF NOT EXISTS notification_channels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    channel_type    TEXT NOT NULL CHECK (channel_type IN ('telegram', 'email', 'sms', 'webhook')),
    config          JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- config examples:
    -- telegram: { "bot_token": "...", "chat_id": "..." }
    -- email: { "smtp_host": "...", "from": "...", "to": [...] }
    -- webhook: { "url": "...", "secret": "..." }
    is_enabled      BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notification_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    channel_type    TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    -- event_type: 'anomaly_detected', 'crisis_alert', 'po_status_change', 'system_health', 'test'
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'sent', 'failed', 'skipped')),
    error_message   TEXT,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notification_channels_org_id ON notification_channels(org_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_org_id ON notification_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_event_type ON notification_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
```

### 2. Notification Service (`services/notification_service.py`)

```python
class NotificationService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def send_anomaly_alert(self, org_id: str, anomaly_data: dict) -> list[dict]:
        """
        Send anomaly alert through all enabled channels for the org.
        1. Fetch enabled notification_channels for org
        2. Format message for each channel type
        3. Dispatch via appropriate handler (Telegram API, email, webhook)
        4. Log result to notification_logs
        Returns list of log entries.
        """

    async def send_crisis_alert(self, org_id: str, crisis_data: dict) -> list[dict]:
        """Send crisis/spare parts alert."""

    async def send_test_notification(self, org_id: str, channel_id: str) -> dict:
        """Send test notification to verify channel config."""

    async def get_notification_logs(
        self, org_id: str, event_type: str = None, page: int = 1, limit: int = 50
    ) -> dict:
        """Paginated notification logs for an org."""

    # Channel dispatch handlers
    async def _send_telegram(self, config: dict, message: str) -> bool: ...
    async def _send_email(self, config: dict, subject: str, body: str) -> bool: ...
    async def _send_webhook(self, config: dict, payload: dict) -> bool: ...
```

### 3. Notifications Router (`routers/notifications.py`)

Replace the placeholder:

```python
router = APIRouter(prefix="/api/notifications", tags=["notifications"])

GET /api/notifications/logs
  Auth: VIEW_NOTIFICATIONS permission
  Query: event_type?, status?, page, limit
  → Paginated notification logs (org-scoped)

POST /api/notifications/trigger/anomaly/{anomaly_id}
  Auth: TRIGGER_NOTIFICATION permission (Manager only)
  → Manually trigger anomaly alert for the given anomaly
  → Sends through all enabled channels

POST /api/notifications/trigger/test
  Auth: Manager role
  Body: { channel_id }
  → Send test notification to verify channel setup

GET /api/notifications/channels
  Auth: Manager role
  → List configured notification channels for org

POST /api/notifications/channels
  Auth: Manager role
  Body: { channel_type, config, is_enabled }
  → Add notification channel

PATCH /api/notifications/channels/{channel_id}
  Auth: Manager role
  Body: { config?, is_enabled? }
  → Update channel config or enable/disable

DELETE /api/notifications/channels/{channel_id}
  Auth: Manager role
  → Delete notification channel
```

### 4. PUQ AI Integration (Mock First)

PUQ AI is the platform's webhook/notification relay service:
- For now, implement mock dispatchers that log to console + notification_logs
- Real integration: HTTP POST to PUQ AI API with payload
- PUQ AI handles actual Telegram/email/SMS delivery

```python
class PUQAIClient:
    """Mock PUQ AI client — logs notifications, returns success."""

    async def send(self, channel_type: str, payload: dict) -> dict:
        logger.info(f"[MOCK PUQ AI] {channel_type}: {payload}")
        return {"status": "sent", "mock": True}
```

## Deliverables

- [ ] Migration for `notification_channels` + `notification_logs` tables
- [ ] `services/notification_service.py` — multi-channel dispatch, logging
- [ ] `routers/notifications.py` — logs, trigger, channel CRUD
- [ ] Mock PUQ AI client
- [ ] Notifications org-scoped
- [ ] Channel management restricted to Manager
- [ ] Trigger restricted to Manager (TRIGGER_NOTIFICATION permission)
- [ ] `main.py` updated to include notifications router
