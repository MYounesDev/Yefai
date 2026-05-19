'use client';

import { useMemo } from 'react';
import { motion, type Variants } from 'framer-motion';
import { Bell, Mail, MessageSquare, Smartphone, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { mockNotificationLogs } from '@/services/mock/notifications';
import { cn, formatRelativeTime } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.03 } } },
  item: { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } } },
};

const typeLabels: Record<string, string> = {
  anomaly_alert: 'Anomali Uyarısı',
  critical_warning: 'Kritik Uyarı',
  report: 'Rapor',
  crisis_alert: 'Kriz Uyarısı',
  po_notification: 'Satın Alma Bildirimi',
};

const channelIcons: Record<string, React.ElementType> = {
  telegram: MessageSquare,
  email: Mail,
  sms: Smartphone,
};

const channelLabels: Record<string, string> = {
  telegram: 'Telegram',
  email: 'E-posta',
  sms: 'SMS',
};

const statusIcons: Record<string, React.ElementType> = {
  delivered: CheckCircle,
  failed: XCircle,
  pending: Clock,
};

const statusLabels: Record<string, string> = {
  delivered: 'İletildi',
  failed: 'Başarısız',
  pending: 'Bekliyor',
};

export default function NotificationsPage() {
  const grouped = useMemo(() => {
    const groups: Record<string, typeof mockNotificationLogs> = {};
    mockNotificationLogs.forEach((log) => {
      const date = new Date(log.timestamp).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
      if (!groups[date]) groups[date] = [];
      groups[date].push(log);
    });
    return groups;
  }, []);

  const stats = useMemo(() => ({
    total: mockNotificationLogs.length,
    delivered: mockNotificationLogs.filter((l) => l.status === 'delivered').length,
    failed: mockNotificationLogs.filter((l) => l.status === 'failed').length,
    pending: mockNotificationLogs.filter((l) => l.status === 'pending').length,
  }), []);

  return (
    <div className="p-6 space-y-6">
      {/* Stats */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Toplam Bildirim', value: stats.total, icon: Bell, color: 'bg-cyan/10 text-cyan' },
          { label: 'İletildi', value: stats.delivered, icon: CheckCircle, color: 'bg-emerald/10 text-emerald' },
          { label: 'Başarısız', value: stats.failed, icon: XCircle, color: 'bg-rose/10 text-rose' },
          { label: 'Bekliyor', value: stats.pending, icon: Clock, color: 'bg-amber/10 text-amber' },
        ].map((s) => (
          <motion.div key={s.label} variants={stagger.item} className="bg-surface border border-border rounded-xl p-4 flex items-center gap-3">
            <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', s.color)}>
              <s.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] text-muted tracking-wide uppercase">{s.label}</p>
              <p className="text-xl font-heading font-bold text-foreground">{s.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Timeline */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        {Object.entries(grouped).map(([date, logs]) => (
          <div key={date}>
            <motion.h3
              variants={stagger.item}
              className="text-xs font-semibold text-muted tracking-wide uppercase mb-3 flex items-center gap-2"
            >
              <div className="w-2 h-2 rounded-full bg-cyan" />
              {date}
            </motion.h3>
            <div className="space-y-2">
              {logs.map((log) => {
                const ChannelIcon = (channelIcons[log.channel] || Bell) as React.ComponentType<{ className?: string }>;
                const StatusIcon = (statusIcons[log.status] || Clock) as React.ComponentType<{ className?: string }>;

                return (
                  <motion.div
                    key={log.id}
                    variants={stagger.item}
                    className={cn(
                      'bg-surface border rounded-xl p-4 flex items-center gap-4 transition-all hover:shadow-card',
                      log.type === 'critical_warning' || log.type === 'crisis_alert' ? 'border-rose/20' : 'border-border'
                    )}
                  >
                    {/* Icon */}
                    <div className={cn(
                      'w-10 h-10 rounded-xl flex items-center justify-center shrink-0',
                      log.type === 'critical_warning' || log.type === 'crisis_alert' ? 'bg-rose/10' :
                      log.type === 'anomaly_alert' ? 'bg-amber/10' :
                      'bg-cyan/10'
                    )}>
                      {log.type === 'critical_warning' || log.type === 'crisis_alert' ? (
                        <AlertTriangle className={cn('w-5 h-5', log.type === 'crisis_alert' ? 'text-rose' : 'text-amber')} />
                      ) : (
                        <Bell className="w-5 h-5 text-cyan" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-foreground">{typeLabels[log.type] || log.type}</span>
                        <span className={cn(
                          'text-[10px] px-2 py-0.5 rounded-lg font-semibold flex items-center gap-1',
                          log.status === 'delivered' ? 'bg-emerald/10 text-emerald' :
                          log.status === 'failed' ? 'bg-rose/10 text-rose' :
                          'bg-amber/10 text-amber'
                        )}>
                          <StatusIcon className="w-3 h-3" />
                          {statusLabels[log.status]}
                        </span>
                      </div>
                      <p className="text-[11px] text-muted mt-0.5 truncate">
                        {log.target}
                      </p>
                    </div>

                    {/* Channel + Time */}
                    <div className="flex items-center gap-4 shrink-0">
                      <div className="flex items-center gap-1.5 text-muted">
                        <ChannelIcon className="w-3.5 h-3.5" />
                        <span className="text-[11px]">{channelLabels[log.channel]}</span>
                      </div>
                      <span className="text-[11px] text-muted">{formatRelativeTime(log.timestamp)}</span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
