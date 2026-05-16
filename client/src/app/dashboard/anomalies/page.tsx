'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, AlertTriangle, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { mockAnomalies } from '@/services/mock/anomalies';
import { SeverityBadge, StatusBadge } from '@/components/ui/badge';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { Severity, AnomalyStatus, WearType } from '@/types';

const SEVERITY_OPTS: (Severity | 'all')[] = ['all', 'critical', 'high', 'medium', 'low'];
const STATUS_OPTS: (AnomalyStatus | 'all')[] = ['all', 'new', 'reviewed', 'resolved'];
const WEAR_OPTS: (WearType | 'all')[] = ['all', 'flank_wear', 'adhesion', 'combination'];

export default function AnomaliesPage() {
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState<Severity | 'all'>('all');
  const [status, setStatus] = useState<AnomalyStatus | 'all'>('all');
  const [wearType, setWearType] = useState<WearType | 'all'>('all');

  const filtered = useMemo(() => {
    return mockAnomalies.filter((a) => {
      if (severity !== 'all' && a.severity !== severity) return false;
      if (status !== 'all' && a.status !== status) return false;
      if (wearType !== 'all' && a.wear_type !== wearType) return false;
      if (search) {
        const q = search.toLowerCase();
        if (!a.machine_id.toLowerCase().includes(q) && !a.id.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [search, severity, status, wearType]);

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold font-heading text-foreground">Anomaly Log</h1>
          <p className="text-xs text-muted mt-0.5">{filtered.length} of {mockAnomalies.length} anomalies</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-surface border border-border rounded-xl p-4 space-y-3">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by machine ID..."
              className="w-full pl-9 pr-3 py-2 text-sm bg-surface-2 border border-border rounded-lg text-foreground placeholder:text-muted focus:outline-none focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div className="flex items-center gap-1 text-xs text-muted">
            <Filter className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          {/* Severity filter */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-muted">Severity:</span>
            {SEVERITY_OPTS.map((s) => (
              <button
                key={s}
                onClick={() => setSeverity(s)}
                className={cn(
                  'text-xs px-2.5 py-1 rounded-lg border transition-all capitalize',
                  severity === s
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-400'
                    : 'bg-surface-2 border-border text-muted hover:border-border-strong hover:text-foreground'
                )}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-muted">Status:</span>
            {STATUS_OPTS.map((s) => (
              <button
                key={s}
                onClick={() => setStatus(s)}
                className={cn(
                  'text-xs px-2.5 py-1 rounded-lg border transition-all capitalize',
                  status === s
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-400'
                    : 'bg-surface-2 border-border text-muted hover:border-border-strong hover:text-foreground'
                )}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Wear type filter */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-muted">Wear:</span>
            {WEAR_OPTS.map((w) => (
              <button
                key={w}
                onClick={() => setWearType(w)}
                className={cn(
                  'text-xs px-2.5 py-1 rounded-lg border transition-all capitalize',
                  wearType === w
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-400'
                    : 'bg-surface-2 border-border text-muted hover:border-border-strong hover:text-foreground'
                )}
              >
                {w === 'all' ? 'all' : w.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="grid grid-cols-[1fr_auto_auto_auto_auto_auto] gap-0 text-[11px] font-medium text-muted px-4 py-2.5 border-b border-border bg-surface-2">
          <span>Machine / ID</span>
          <span className="px-4">Wear Type</span>
          <span className="px-4">Wear</span>
          <span className="px-4">Score</span>
          <span className="px-4">Severity</span>
          <span className="px-4">Status</span>
        </div>
        <div className="divide-y divide-border">
          {filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-muted">
              <AlertTriangle className="w-8 h-8 mb-2 opacity-30" />
              <p className="text-sm">No anomalies match your filters</p>
            </div>
          )}
          {filtered.map((a, i) => (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.02 }}
            >
              <Link
                href={`/dashboard/anomalies/${a.id}`}
                className="grid grid-cols-[1fr_auto_auto_auto_auto_auto] gap-0 items-center px-4 py-3 hover:bg-surface-2 transition-colors group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      'w-1.5 h-1.5 rounded-full shrink-0',
                      a.severity === 'critical' ? 'bg-rose-500 animate-pulse' :
                      a.severity === 'high' ? 'bg-amber-500' :
                      a.severity === 'medium' ? 'bg-cyan-500' : 'bg-emerald-500'
                    )} />
                    <span className="text-sm font-medium text-foreground">{a.machine_id}</span>
                    <span className="text-xs text-muted font-mono">{a.id}</span>
                  </div>
                  <p className="text-xs text-muted mt-0.5 ml-3.5">{formatRelativeTime(a.timestamp)}</p>
                </div>
                <div className="px-4">
                  <span className="text-xs text-foreground capitalize">{a.wear_type.replace('_', ' ')}</span>
                </div>
                <div className="px-4">
                  <span className="text-xs font-mono text-foreground">{a.estimated_wear_um} µm</span>
                </div>
                <div className="px-4">
                  <span className={cn(
                    'text-xs font-mono font-bold',
                    a.anomaly_score > 0.75 ? 'text-rose-400' :
                    a.anomaly_score > 0.5 ? 'text-amber-400' :
                    a.anomaly_score > 0.3 ? 'text-cyan-400' : 'text-emerald-400'
                  )}>
                    {(a.anomaly_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="px-4">
                  <SeverityBadge severity={a.severity} />
                </div>
                <div className="px-4 flex items-center gap-2">
                  <StatusBadge status={a.status} />
                  <ChevronRight className="w-3.5 h-3.5 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
