import { NotificationLog } from '@/types';

const types: NotificationLog['type'][] = ['anomaly_alert', 'critical_warning', 'crisis_alert', 'po_notification', 'report'];
const channels: NotificationLog['channel'][] = ['telegram', 'telegram', 'telegram', 'email', 'email', 'sms'];
const targets = ['M-03/Tool-A', 'M-06/Tool-B', 'M-04/Tool-C', 'Insert Tip A-12', 'Spindle Bearing XR-9', 'M-07/Tool-A', 'Weekly Report', 'PO-2026-0042'];

function hoursAgo(h: number): string {
  return new Date(Date.now() - h * 3600 * 1000).toISOString();
}

export const mockNotificationLogs: NotificationLog[] = Array.from({ length: 35 }, (_, i) => {
  const statusRoll = Math.random();
  const status: NotificationLog['status'] = statusRoll > 0.85 ? 'failed' : statusRoll > 0.80 ? 'pending' : 'delivered';
  const type = types[i % types.length];
  const channel = channels[i % channels.length];
  const target = targets[i % targets.length];

  return {
    id: `notif_${String(i + 1).padStart(3, '0')}`,
    type,
    channel,
    target,
    status,
    timestamp: hoursAgo(i * 1.3 + Math.random()),
    payload: {
      event: type,
      machine: target,
      score: parseFloat((Math.random() * 0.5 + 0.5).toFixed(3)),
      threshold: 0.75,
      timestamp: hoursAgo(i * 1.3),
      org_id: 'org_001',
      channel,
    },
    error_message: status === 'failed' ? 'Connection timeout: upstream service unavailable' : undefined,
  };
});
