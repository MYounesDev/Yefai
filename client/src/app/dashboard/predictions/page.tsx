'use client';

import { motion, type Variants } from 'framer-motion';
import { TrendingUp, ArrowUpRight, Clock, AlertTriangle, Gauge } from 'lucide-react';
import Link from 'next/link';
import { ResponsiveContainer, AreaChart, Area, Tooltip } from 'recharts';
import { mockPredictions } from '@/services/mock/predictions';
import { StatusDot, ProgressBar } from '@/components/ui/index';
import { cn } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.04 } } },
  item: { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } } },
};

const statusLabels: Record<string, string> = {
  safe: 'Güvenli',
  watch: 'İzleniyor',
  warning: 'Uyarı',
  critical: 'Kritik',
};

const trendLabels: Record<string, string> = {
  accelerating: 'Hızlanıyor',
  stable: 'Sabit',
  decelerating: 'Yavaşlıyor',
};

const confidenceLabels: Record<string, string> = {
  high: 'Yüksek',
  medium: 'Orta',
  low: 'Düşük',
};

export default function PredictionsPage() {
  const sorted = [...mockPredictions].sort((a, b) => a.hours_to_critical - b.hours_to_critical);
  const criticalCount = sorted.filter((m) => m.status === 'critical').length;
  const warningCount = sorted.filter((m) => m.status === 'warning').length;

  return (
    <div className="p-6 space-y-6">
      {/* Summary */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Toplam Makine', value: sorted.length, icon: Gauge, color: 'text-foreground', bg: 'bg-cyan/10 text-cyan' },
          { label: 'Kritik Durum', value: criticalCount, icon: AlertTriangle, color: 'text-rose', bg: 'bg-rose/10 text-rose' },
          { label: 'Uyarı Durumu', value: warningCount, icon: Clock, color: 'text-amber', bg: 'bg-amber/10 text-amber' },
        ].map((s) => (
          <motion.div key={s.label} variants={stagger.item} className="bg-surface border border-border rounded-xl p-4 flex items-center gap-3">
            <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', s.bg)}>
              <s.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] text-muted tracking-wide uppercase">{s.label}</p>
              <p className={cn('text-xl font-heading font-bold', s.color)}>{s.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Machine Grid */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4"
      >
        {sorted.map((p) => (
          <motion.div key={p.machine_id} variants={stagger.item}>
            <Link
              href={`/dashboard/predictions/${p.machine_id}`}
              className={cn(
                'block bg-surface border rounded-xl p-5 transition-all duration-200 hover:shadow-card group',
                p.status === 'critical' ? 'border-rose/25 hover:border-rose/40' :
                p.status === 'warning' ? 'border-amber/25 hover:border-amber/40' :
                'border-border hover:border-border-strong'
              )}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <StatusDot status={p.status} />
                  <span className="text-sm font-heading font-bold text-foreground">{p.machine_id}</span>
                </div>
                <span className={cn(
                  'text-[10px] px-2 py-0.5 rounded-lg font-semibold',
                  p.status === 'critical' ? 'bg-rose/10 text-rose' :
                  p.status === 'warning' ? 'bg-amber/10 text-amber' :
                  p.status === 'watch' ? 'bg-cyan/10 text-cyan' :
                  'bg-emerald/10 text-emerald'
                )}>
                  {statusLabels[p.status]}
                </span>
              </div>

              {/* Sparkline */}
              <div className="h-16 mb-4 -mx-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={p.historical_data}>
                    <defs>
                      <linearGradient id={`pred-${p.machine_id}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'} stopOpacity={0.25} />
                        <stop offset="100%" stopColor={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <Tooltip
                      contentStyle={{
                        background: 'var(--color-surface)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '10px',
                        fontSize: '10px',
                        color: 'var(--color-foreground)',
                      }}
                      formatter={(v: number) => [`${v} µm`, 'Aşınma']}
                    />
                    <Area
                      type="monotone"
                      dataKey="wear_um"
                      stroke={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'}
                      strokeWidth={1.5}
                      fill={`url(#pred-${p.machine_id})`}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Wear */}
              <div className="space-y-2 mb-3">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Aşınma</span>
                  <span className="font-mono text-foreground font-medium">{p.current_wear_um} / {p.critical_threshold_um} µm</span>
                </div>
                <ProgressBar
                  value={p.current_wear_um}
                  max={p.critical_threshold_um}
                  color={p.status === 'critical' ? 'rose' : p.status === 'warning' ? 'amber' : p.status === 'watch' ? 'cyan' : 'emerald'}
                />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-muted">Kritiğe kalan</span>
                  <span className={cn(
                    'font-semibold',
                    p.hours_to_critical < 24 ? 'text-rose' : p.hours_to_critical < 72 ? 'text-amber' : 'text-emerald'
                  )}>
                    {p.hours_to_critical.toFixed(0)}s
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Hız</span>
                  <span className="text-foreground font-mono">{p.wear_rate_um_per_hour} µm/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Trend</span>
                  <span className={cn(
                    'font-medium',
                    p.trend === 'accelerating' ? 'text-rose' : p.trend === 'decelerating' ? 'text-emerald' : 'text-muted'
                  )}>
                    {trendLabels[p.trend]}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Güven</span>
                  <span className="text-foreground">{confidenceLabels[p.confidence]}</span>
                </div>
              </div>

              {/* Arrow */}
              <div className="mt-3 flex justify-end">
                <ArrowUpRight className="w-4 h-4 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
