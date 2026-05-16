'use client';

import { useMemo } from 'react';
import { motion, type Variants } from 'framer-motion';
import { AlertTriangle, TrendingUp, Activity, Package, ArrowUpRight, ArrowDownRight, Clock, Zap } from 'lucide-react';
import Link from 'next/link';
import { mockAnomalies } from '@/services/mock/anomalies';
import { mockPredictions } from '@/services/mock/predictions';
import { SeverityBadge, StatusBadge } from '@/components/ui/badge';
import { StatusDot } from '@/components/ui/status-dot';
import { cn } from '@/lib/utils';
import { formatRelativeTime, formatWear } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.06 } } },
  item: { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 280, damping: 24 } } },
};

function StatCard({
  label, value, unit, icon: Icon, trend, trendLabel, color,
}: {
  label: string; value: string | number; unit?: string; icon: React.ElementType;
  trend?: 'up' | 'down'; trendLabel?: string; color: string;
}) {
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-muted">{label}</p>
        <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', color)}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div>
        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-bold font-heading text-foreground">{value}</span>
          {unit && <span className="text-xs text-muted">{unit}</span>}
        </div>
        {trendLabel && (
          <div className={cn('flex items-center gap-1 mt-1 text-xs', trend === 'up' ? 'text-rose-400' : 'text-emerald-400')}>
            {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            <span>{trendLabel}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function MachineStatusGrid() {
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground font-heading">Machine Fleet</h2>
        <Link href="/dashboard/predictions" className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1">
          View predictions <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {mockPredictions.map((p) => (
          <Link
            key={p.machine_id}
            href={`/dashboard/predictions/${p.machine_id}`}
            className="group flex flex-col gap-2 p-3 rounded-lg bg-surface-2 border border-border hover:border-border-strong transition-all"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-foreground">{p.machine_id}</span>
              <StatusDot status={p.status} />
            </div>
            {/* Wear bar */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-muted">Wear</span>
                <span className="text-[10px] font-mono text-foreground">{p.current_wear_um} µm</span>
              </div>
              <div className="h-1.5 rounded-full bg-surface-3 overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full transition-all',
                    p.status === 'critical' ? 'bg-rose-500' :
                    p.status === 'warning' ? 'bg-amber-500' :
                    p.status === 'watch' ? 'bg-cyan-500' : 'bg-emerald-500'
                  )}
                  style={{ width: `${Math.min(100, (p.current_wear_um / p.critical_threshold_um) * 100)}%` }}
                />
              </div>
            </div>
            <div className="text-[10px] text-muted">
              <span className={cn(p.hours_to_critical < 24 ? 'text-rose-400' : p.hours_to_critical < 72 ? 'text-amber-400' : 'text-emerald-400')}>
                {p.hours_to_critical.toFixed(0)}h
              </span>
              {' '}to critical
            </div>
          </Link>
        ))}
      </div>
    </motion.div>
  );
}

function RecentAnomalies() {
  const recent = useMemo(() => mockAnomalies.slice(0, 8), []);
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground font-heading">Recent Anomalies</h2>
        <Link href="/dashboard/anomalies" className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1">
          View all <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>
      <div className="space-y-2">
        {recent.map((a) => (
          <Link
            key={a.id}
            href={`/dashboard/anomalies/${a.id}`}
            className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-surface-2 transition-colors group"
          >
            <div className={cn(
              'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
              a.severity === 'critical' ? 'bg-rose-500/10' :
              a.severity === 'high' ? 'bg-amber-500/10' :
              a.severity === 'medium' ? 'bg-cyan-500/10' : 'bg-emerald-500/10'
            )}>
              <AlertTriangle className={cn(
                'w-4 h-4',
                a.severity === 'critical' ? 'text-rose-400' :
                a.severity === 'high' ? 'text-amber-400' :
                a.severity === 'medium' ? 'text-cyan-400' : 'text-emerald-400'
              )} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-foreground">{a.machine_id}</span>
                <SeverityBadge severity={a.severity} />
              </div>
              <p className="text-[11px] text-muted mt-0.5 truncate capitalize">
                {a.wear_type.replace('_', ' ')} · {a.estimated_wear_um} µm
              </p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-[11px] text-muted">{formatRelativeTime(a.timestamp)}</p>
              <StatusBadge status={a.status} />
            </div>
          </Link>
        ))}
      </div>
    </motion.div>
  );
}

function SystemHealth() {
  const services = [
    { name: 'AI Model', status: 'healthy', latency: '42ms' },
    { name: 'NovaVision', status: 'healthy', latency: '118ms' },
    { name: 'PUQ-AI', status: 'healthy', latency: '67ms' },
    { name: 'Database', status: 'healthy', latency: '12ms' },
  ];
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-4 h-4 text-cyan-400" />
        <h2 className="text-sm font-semibold text-foreground font-heading">System Health</h2>
      </div>
      <div className="space-y-2.5">
        {services.map((s) => (
          <div key={s.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-foreground">{s.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-muted">{s.latency}</span>
              <span className="text-[10px] text-emerald-400 font-medium">{s.status}</span>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const activeCount = mockAnomalies.filter((a) => a.status === 'new').length;
  const criticalMachines = mockPredictions.filter((p) => p.status === 'critical').length;
  const avgWear = Math.round(mockPredictions.reduce((s, p) => s + p.current_wear_um, 0) / mockPredictions.length);
  const nextCritical = Math.min(...mockPredictions.map((p) => p.hours_to_critical));

  return (
    <div className="p-6 space-y-6">
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <StatCard
          label="Active Anomalies"
          value={activeCount}
          icon={AlertTriangle}
          trend="up"
          trendLabel="+3 this hour"
          color="bg-rose-500/10 text-rose-400"
        />
        <StatCard
          label="Critical Machines"
          value={criticalMachines}
          unit="/ 8"
          icon={Activity}
          trend="up"
          trendLabel="Needs attention"
          color="bg-amber-500/10 text-amber-400"
        />
        <StatCard
          label="Avg. Wear"
          value={avgWear}
          unit="µm"
          icon={TrendingUp}
          trend="down"
          trendLabel="-2.1% from last check"
          color="bg-cyan-500/10 text-cyan-400"
        />
        <StatCard
          label="Next Critical"
          value={nextCritical.toFixed(1)}
          unit="hours"
          icon={Clock}
          trend="up"
          trendLabel="M-06 accelerating"
          color="bg-violet-500/10 text-violet-400"
        />
      </motion.div>

      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 xl:grid-cols-3 gap-6"
      >
        <div className="xl:col-span-2 space-y-6">
          <MachineStatusGrid />
          <RecentAnomalies />
        </div>
        <div className="space-y-4">
          <SystemHealth />
          {/* Spare parts alert strip */}
          <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Package className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-semibold text-foreground font-heading">Parts Alert</h2>
            </div>
            <div className="space-y-2">
              {[
                { part: 'Carbide Insert #7', risk: 'crisis', score: 0.92 },
                { part: 'Drill Bit 12mm', risk: 'at_risk', score: 0.74 },
                { part: 'End Mill 6mm', risk: 'watch', score: 0.51 },
              ].map((item) => (
                <Link
                  key={item.part}
                  href="/dashboard/spare-parts"
                  className="flex items-center justify-between p-2.5 rounded-lg hover:bg-surface-2 transition-colors"
                >
                  <span className="text-xs text-foreground">{item.part}</span>
                  <div className={cn(
                    'text-[10px] px-2 py-0.5 rounded-full font-medium',
                    item.risk === 'crisis' ? 'bg-rose-500/10 text-rose-400' :
                    item.risk === 'at_risk' ? 'bg-amber-500/10 text-amber-400' :
                    'bg-cyan-500/10 text-cyan-400'
                  )}>
                    {item.risk.replace('_', ' ')}
                  </div>
                </Link>
              ))}
              <Link href="/dashboard/spare-parts" className="block text-center text-xs text-cyan-400 hover:text-cyan-300 mt-2 transition-colors">
                View spare parts crisis board
              </Link>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
