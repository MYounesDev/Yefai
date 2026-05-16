'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Bell, CheckCircle2, XCircle, Clock, MessageSquare, Mail, Phone } from 'lucide-react';
import { mockNotificationLogs } from '@/services/mock/notifications';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { NotificationChannel, NotificationStatus } from '@/types';

const CHANNEL_ICONS: Record<NotificationChannel, React.ElementType> = {
  telegram: MessageSquare,
  email: Mail,
  sms: Phone,
};

const CHANNEL_COLORS: Record<NotificationChannel, string> = {
  telegram: 'text-cyan-400 bg-cyan-500/10',
  email: 'text-violet-400 bg-violet-500/10',
  sms: 'text-emerald-400 bg-emerald-500/10',
};

const STATUS_ICON: Record<NotificationStatus, React.ElementType> = {
  delivered: CheckCircle2,
  failed: XCircle,
  pending: Clock,
};

const STATUS_COLOR: Record<NotificationStatus, string> = {
  delivered: 'text-emerald-400',
  failed: 'text-rose-400',
  pending: 'text-amber-400',
};

const TYPE_LABELS: Record<string, string> = {
  anomaly_alert: 'Anomaly Alert',
  critical_warning: 'Critical Warning',
  crisis_alert: 'Crisis Alert',
  po_notification: 'PO Notification',
  report: 'Report',
};

export default function NotificationsPage() {
  const [channelFilter, setChannelFilter] = useState<NotificationChannel | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<NotificationStatus | 'all'>('all');

  const filtered = useMemo(() => {
    return mockNotificationLogs.filter((n) => {
      if (channelFilter !== 'all' && n.channel !== channelFilter) return false;
      if (statusFilter !== 'all' && n.status !== statusFilter) return false;
      return true;
    });
  }, [channelFilter, statusFilter]);

  const deliveredCount = mockNotificationLogs.filter((n) => n.status === 'delivered').length;
  const failedCount = mockNotificationLogs.filter((n) => n.status === 'failed').length;
  const deliveryRate = Math.round((deliveredCount / mockNotificationLogs.length) * 100);

  return (
    <div className="p-6 space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-surface border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-bold font-heading text-emerald-400">{deliveryRate}%</p>
          <p className="text-xs text-muted mt-0.5">Delivery Rate</p>
        </div>
        <div className="bg-surface border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-bold font-heading text-foreground">{deliveredCount}</p>
          <p className="text-xs text-muted mt-0.5">Delivered</p>
        </div>
        <div className="bg-surface border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-bold font-heading text-rose-400">{failedCount}</p>
          <p className="text-xs text-muted mt-0.5">Failed</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-surface border border-border rounded-xl p-4 flex flex-wrap gap-4">
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-muted">Channel:</span>
          {(['all', 'telegram', 'email', 'sms'] as const).map((c) => (
            <button
              key={c}
              onClick={() => setChannelFilter(c)}
              className={cn(
                'text-xs px-2.5 py-1 rounded-lg border transition-all capitalize',
                channelFilter === c
                  ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-400'
                  : 'bg-surface-2 border-border text-muted hover:border-border-strong hover:text-foreground'
              )}
            >
              {c}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-muted">Status:</span>
          {(['all', 'delivered', 'failed', 'pending'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                'text-xs px-2.5 py-1 rounded-lg border transition-all capitalize',
                statusFilter === s
                  ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-400'
                  : 'bg-surface-2 border-border text-muted hover:border-border-strong hover:text-foreground'
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Notification log */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-surface-2">
          <Bell className="w-3.5 h-3.5 text-muted" />
          <span className="text-xs font-medium text-muted">{filtered.length} notifications</span>
        </div>
        <div className="divide-y divide-border">
          {filtered.map((notif, i) => {
            const ChannelIcon = CHANNEL_ICONS[notif.channel];
            const StatusIcon = STATUS_ICON[notif.status];
            return (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.015 }}
                className="flex items-start gap-3 px-4 py-3 hover:bg-surface-2 transition-colors"
              >
                {/* Channel icon */}
                <div className={cn('w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5', CHANNEL_COLORS[notif.channel])}>
                  <ChannelIcon className="w-3.5 h-3.5" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-medium text-foreground">{TYPE_LABELS[notif.type] ?? notif.type}</span>
                    <span className="text-[11px] text-muted">{notif.target}</span>
                  </div>
                  {notif.error_message && (
                    <p className="text-[11px] text-rose-400 mt-0.5">{notif.error_message}</p>
                  )}
                </div>

                {/* Status + time */}
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <div className={cn('flex items-center gap-1', STATUS_COLOR[notif.status])}>
                    <StatusIcon className="w-3 h-3" />
                    <span className="text-[11px] capitalize">{notif.status}</span>
                  </div>
                  <span className="text-[10px] text-muted">{formatRelativeTime(notif.timestamp)}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
