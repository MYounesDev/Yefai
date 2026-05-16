'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { mockPredictions } from '@/services/mock/predictions';
import { StatusDot } from '@/components/ui/status-dot';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { MachineStatusLevel } from '@/types';

const STATUS_ORDER: MachineStatusLevel[] = ['critical', 'warning', 'watch', 'safe'];

function TrendIcon({ trend }: { trend: string }) {
  if (trend === 'accelerating') return <TrendingUp className="w-3.5 h-3.5 text-rose-400" />;
  if (trend === 'decelerating') return <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />;
  return <Minus className="w-3.5 h-3.5 text-muted" />;
}

const confidenceColor = { high: 'text-emerald-400', medium: 'text-amber-400', low: 'text-rose-400' };

const STATUS_BG: Record<MachineStatusLevel, string> = {
  critical: 'border-rose-500/30 bg-rose-500/5',
  warning: 'border-amber-500/30 bg-amber-500/5',
  watch: 'border-cyan-500/20 bg-cyan-500/5',
  safe: 'border-border bg-surface',
};

export default function PredictionsPage() {
  const sorted = [...mockPredictions].sort(
    (a, b) => STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status)
  );

  const criticalCount = sorted.filter((p) => p.status === 'critical').length;
  const warningCount = sorted.filter((p) => p.status === 'warning').length;

  return (
    <div className="p-6 space-y-6">
      {/* Summary strip */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20">
          <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
          <span className="text-xs text-rose-400 font-medium">{criticalCount} Critical</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
          <div className="w-2 h-2 rounded-full bg-amber-500" />
          <span className="text-xs text-amber-400 font-medium">{warningCount} Warning</span>
        </div>
        <span className="text-xs text-muted ml-auto flex items-center gap-1">
          <RefreshCw className="w-3 h-3" />
          Updated moments ago
        </span>
      </div>

      {/* Machine cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
        {sorted.map((p, i) => (
          <motion.div
            key={p.machine_id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Link
              href={`/dashboard/predictions/${p.machine_id}`}
              className={cn(
                'group block bg-surface border rounded-xl p-5 hover:shadow-lg transition-all space-y-4',
                STATUS_BG[p.status]
              )}
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StatusDot status={p.status} />
                  <span className="text-sm font-semibold text-foreground font-heading">{p.machine_name}</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>

              {/* Wear progress */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted">Wear</span>
                  <span className="font-mono text-foreground">
                    {p.current_wear_um} / {p.critical_threshold_um} µm
                  </span>
                </div>
                <div className="h-2 rounded-full bg-surface-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, (p.current_wear_um / p.critical_threshold_um) * 100)}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut', delay: i * 0.05 }}
                    className={cn(
                      'h-full rounded-full',
                      p.status === 'critical' ? 'bg-rose-500' :
                      p.status === 'warning' ? 'bg-amber-500' :
                      p.status === 'watch' ? 'bg-cyan-400' : 'bg-emerald-500'
                    )}
                  />
                </div>
              </div>

              {/* Stats row */}
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center">
                  <p className="text-[10px] text-muted mb-0.5">Time to Critical</p>
                  <p className={cn(
                    'text-sm font-bold font-heading',
                    p.hours_to_critical < 24 ? 'text-rose-400' :
                    p.hours_to_critical < 72 ? 'text-amber-400' : 'text-emerald-400'
                  )}>
                    {p.hours_to_critical.toFixed(0)}h
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-muted mb-0.5">Rate</p>
                  <p className="text-sm font-bold font-heading text-foreground">
                    {p.wear_rate_um_per_hour} <span className="text-[10px] font-normal text-muted">µm/h</span>
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-muted mb-0.5">Trend</p>
                  <div className="flex items-center justify-center gap-1">
                    <TrendIcon trend={p.trend} />
                    <span className="text-[11px] text-muted capitalize">{p.trend.slice(0, 5)}</span>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-1 border-t border-border">
                <span className="text-[10px] text-muted">Confidence</span>
                <span className={cn('text-[11px] font-medium capitalize', confidenceColor[p.confidence])}>
                  {p.confidence}
                </span>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
