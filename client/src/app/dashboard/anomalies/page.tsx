'use client';

import { useState, useMemo } from 'react';
import { motion, type Variants } from 'framer-motion';
import { Search, Filter, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';
import { mockAnomalies } from '@/services/mock/anomalies';
import { SeverityBadge, StatusBadge, StatusDot } from '@/components/ui/index';
import { cn, formatRelativeTime } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.03 } } },
  item: { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } } },
};

type FilterSeverity = 'all' | 'critical' | 'high' | 'medium' | 'low';
type FilterStatus = 'all' | 'new' | 'reviewed' | 'resolved';

const severityFilters: { value: FilterSeverity; label: string }[] = [
  { value: 'all', label: 'Tümü' },
  { value: 'critical', label: 'Kritik' },
  { value: 'high', label: 'Yüksek' },
  { value: 'medium', label: 'Orta' },
  { value: 'low', label: 'Düşük' },
];

const statusFilters: { value: FilterStatus; label: string }[] = [
  { value: 'all', label: 'Tümü' },
  { value: 'new', label: 'Yeni' },
  { value: 'reviewed', label: 'İncelendi' },
  { value: 'resolved', label: 'Çözüldü' },
];

export default function AnomaliesPage() {
  const [severity, setSeverity] = useState<FilterSeverity>('all');
  const [status, setStatus] = useState<FilterStatus>('all');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return mockAnomalies.filter((a) => {
      if (severity !== 'all' && a.severity !== severity) return false;
      if (status !== 'all' && a.status !== status) return false;
      if (search && !a.machine_id.toLowerCase().includes(search.toLowerCase()) && !a.wear_type.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [severity, status, search]);

  const counts = useMemo(() => ({
    total: mockAnomalies.length,
    critical: mockAnomalies.filter((a) => a.severity === 'critical').length,
    new: mockAnomalies.filter((a) => a.status === 'new').length,
  }), []);

  return (
    <div className="p-6 space-y-6">
      {/* Header Stats */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Toplam Anomali', value: counts.total, color: 'text-foreground' },
          { label: 'Kritik', value: counts.critical, color: 'text-rose' },
          { label: 'Yeni (İncelenmemiş)', value: counts.new, color: 'text-amber' },
        ].map((s) => (
          <motion.div key={s.label} variants={stagger.item} className="bg-surface border border-border rounded-xl p-4">
            <p className="text-[11px] text-muted tracking-wide uppercase mb-1">{s.label}</p>
            <p className={cn('text-2xl font-heading font-bold', s.color)}>{s.value}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-surface border border-border rounded-xl p-4 space-y-4"
      >
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Makine ID veya aşınma türü ara..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface-2 border border-border text-sm text-foreground placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
          />
        </div>

        <div className="flex flex-wrap gap-6">
          {/* Severity */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-[11px] text-muted">
              <Filter className="w-3 h-3" />
              <span>Şiddet</span>
            </div>
            <div className="flex gap-1.5">
              {severityFilters.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setSeverity(f.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                    severity === f.value
                      ? 'bg-cyan/10 text-cyan border border-cyan/20'
                      : 'bg-surface-2 text-muted border border-transparent hover:text-foreground hover:border-border'
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Status */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-[11px] text-muted">
              <Filter className="w-3 h-3" />
              <span>Durum</span>
            </div>
            <div className="flex gap-1.5">
              {statusFilters.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setStatus(f.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                    status === f.value
                      ? 'bg-cyan/10 text-cyan border border-cyan/20'
                      : 'bg-surface-2 text-muted border border-transparent hover:text-foreground hover:border-border'
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Results count */}
      <p className="text-xs text-muted">
        <span className="text-foreground font-semibold">{filtered.length}</span> anomali bulundu
      </p>

      {/* Table */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="bg-surface border border-border rounded-xl overflow-hidden"
      >
        {/* Header */}
        <div className="grid grid-cols-12 gap-4 px-5 py-3 border-b border-border text-[11px] text-muted font-medium tracking-wide uppercase">
          <div className="col-span-2">Makine</div>
          <div className="col-span-2">Aşınma Türü</div>
          <div className="col-span-2">Aşınma</div>
          <div className="col-span-1">Skor</div>
          <div className="col-span-2">Şiddet</div>
          <div className="col-span-2">Durum</div>
          <div className="col-span-1">Zaman</div>
        </div>

        {/* Rows */}
        {filtered.map((a) => (
          <motion.div key={a.id} variants={stagger.item}>
            <Link
              href={`/dashboard/anomalies/${a.id}`}
              className="grid grid-cols-12 gap-4 px-5 py-3.5 hover:bg-surface-2 transition-all border-b border-border/50 last:border-0 group items-center"
            >
              <div className="col-span-2 flex items-center gap-2">
                <StatusDot status={a.severity === 'critical' ? 'critical' : 'safe'} pulse={a.severity === 'critical'} />
                <span className="text-xs font-semibold text-foreground">{a.machine_id}</span>
              </div>
              <div className="col-span-2 text-xs text-muted capitalize">{a.wear_type.replace('_', ' ')}</div>
              <div className="col-span-2">
                <span className="text-xs font-mono text-foreground font-medium">{a.estimated_wear_um} µm</span>
              </div>
              <div className="col-span-1">
                <span className={cn(
                  'text-xs font-mono font-semibold',
                  a.anomaly_score > 0.7 ? 'text-rose' : a.anomaly_score > 0.4 ? 'text-amber' : 'text-emerald'
                )}>
                  {a.anomaly_score.toFixed(2)}
                </span>
              </div>
              <div className="col-span-2"><SeverityBadge severity={a.severity} /></div>
              <div className="col-span-2"><StatusBadge status={a.status} /></div>
              <div className="col-span-1 flex items-center justify-between">
                <span className="text-[11px] text-muted">{formatRelativeTime(a.timestamp)}</span>
                <ArrowUpRight className="w-3 h-3 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
