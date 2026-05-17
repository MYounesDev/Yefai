'use client';

import { useMemo } from 'react';
import { motion, type Variants } from 'framer-motion';
import {
  AlertTriangle, TrendingUp, Activity, Package, ArrowUpRight,
  ArrowDownRight, Clock, Zap, Shield, Radio,
} from 'lucide-react';
import Link from 'next/link';
import {
  LineChart, Line, AreaChart, Area, ResponsiveContainer, Tooltip,
} from 'recharts';
import { mockAnomalies } from '@/services/mock/anomalies';
import { mockPredictions } from '@/services/mock/predictions';
import { SeverityBadge, StatusBadge, StatusDot, ProgressBar } from '@/components/ui/index';
import { cn, formatRelativeTime } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.05 } } },
  item: {
    hidden: { opacity: 0, y: 14 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } },
  },
};

function StatCard({
  label, value, unit, icon: Icon, trend, trendLabel, color, glowColor,
}: {
  label: string; value: string | number; unit?: string; icon: React.ElementType;
  trend?: 'up' | 'down'; trendLabel?: string; color: string; glowColor?: string;
}) {
  return (
    <motion.div
      variants={stagger.item}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className={cn(
        'bg-surface border border-border rounded-xl p-5 flex flex-col gap-3 transition-all hover:border-border-strong hover:shadow-card',
        glowColor
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-medium text-muted tracking-wide uppercase">{label}</p>
        <div className={cn('w-9 h-9 rounded-xl flex items-center justify-center', color)}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold font-heading text-foreground tabular-nums">{value}</span>
          {unit && <span className="text-xs text-muted font-medium">{unit}</span>}
        </div>
        {trendLabel && (
          <div className={cn('flex items-center gap-1 mt-1.5 text-xs font-medium', trend === 'up' ? 'text-rose' : 'text-emerald')}>
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
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-cyan" />
          <h2 className="text-sm font-semibold text-foreground font-heading">Makine Filosu</h2>
        </div>
        <Link href="/dashboard/predictions" className="text-xs text-cyan hover:text-cyan/80 transition-colors flex items-center gap-1 font-medium">
          Tahminlere git <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {mockPredictions.map((p) => (
          <Link
            key={p.machine_id}
            href={`/dashboard/predictions/${p.machine_id}`}
            className="group flex flex-col gap-2.5 p-3.5 rounded-xl bg-surface-2 border border-border hover:border-border-strong transition-all duration-200 hover:shadow-card"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground">{p.machine_id}</span>
              <StatusDot status={p.status} />
            </div>
            {/* Sparkline */}
            <div className="h-8 -mx-1">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={p.historical_data.slice(-6)}>
                  <defs>
                    <linearGradient id={`spark-${p.machine_id}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'} stopOpacity={0.3} />
                      <stop offset="100%" stopColor={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="wear_um"
                    stroke={p.status === 'critical' ? '#FB7185' : p.status === 'warning' ? '#FBBF24' : '#00D4FF'}
                    strokeWidth={1.5}
                    fill={`url(#spark-${p.machine_id})`}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            {/* Wear bar */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-muted">Aşınma</span>
                <span className="text-[10px] font-mono text-foreground font-medium">{p.current_wear_um} µm</span>
              </div>
              <ProgressBar
                value={p.current_wear_um}
                max={p.critical_threshold_um}
                color={p.status === 'critical' ? 'rose' : p.status === 'warning' ? 'amber' : p.status === 'watch' ? 'cyan' : 'emerald'}
                size="xs"
              />
            </div>
            <div className="text-[10px] text-muted">
              <span className={cn(
                'font-semibold',
                p.hours_to_critical < 24 ? 'text-rose' : p.hours_to_critical < 72 ? 'text-amber' : 'text-emerald'
              )}>
                {p.hours_to_critical.toFixed(0)}s
              </span>
              {' '}kritiğe kalan
            </div>
          </Link>
        ))}
      </div>
    </motion.div>
  );
}

function RecentAnomalies() {
  const recent = useMemo(() => mockAnomalies.slice(0, 6), []);
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose" />
          <h2 className="text-sm font-semibold text-foreground font-heading">Son Anomaliler</h2>
        </div>
        <Link href="/dashboard/anomalies" className="text-xs text-cyan hover:text-cyan/80 transition-colors flex items-center gap-1 font-medium">
          Tümünü gör <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>
      <div className="space-y-1">
        {recent.map((a) => (
          <Link
            key={a.id}
            href={`/dashboard/anomalies/${a.id}`}
            className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-2 transition-all group"
          >
            <div className={cn(
              'w-9 h-9 rounded-xl flex items-center justify-center shrink-0 transition-colors',
              a.severity === 'critical' ? 'bg-rose/10 group-hover:bg-rose/15' :
              a.severity === 'high' ? 'bg-amber/10 group-hover:bg-amber/15' :
              a.severity === 'medium' ? 'bg-cyan/10 group-hover:bg-cyan/15' : 'bg-emerald/10 group-hover:bg-emerald/15'
            )}>
              <AlertTriangle className={cn(
                'w-4 h-4',
                a.severity === 'critical' ? 'text-rose' :
                a.severity === 'high' ? 'text-amber' :
                a.severity === 'medium' ? 'text-cyan' : 'text-emerald'
              )} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-foreground">{a.machine_id}</span>
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
    { name: 'Veritabanı', status: 'healthy', latency: '12ms' },
  ];
  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-4 h-4 text-cyan" />
        <h2 className="text-sm font-semibold text-foreground font-heading">Sistem Durumu</h2>
      </div>
      <div className="space-y-3">
        {services.map((s) => (
          <div key={s.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <StatusDot status={s.status} pulse={false} />
              <span className="text-xs text-foreground font-medium">{s.name}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono text-muted">{s.latency}</span>
              <span className="text-[10px] text-emerald font-semibold uppercase tracking-wide">Aktif</span>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function WearTrendChart() {
  const data = useMemo(() => {
    return Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      wear: 80 + Math.sin(i * 0.3) * 20 + Math.random() * 10,
      anomalies: Math.floor(Math.random() * 4),
    }));
  }, []);

  return (
    <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-violet" />
        <h2 className="text-sm font-semibold text-foreground font-heading">24 Saat Aşınma Trendi</h2>
      </div>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <defs>
              <linearGradient id="wearGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00D4FF" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#00D4FF" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              contentStyle={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: '12px',
                fontSize: '11px',
                color: 'var(--color-foreground)',
              }}
            />
            <Line
              type="monotone"
              dataKey="wear"
              stroke="#00D4FF"
              strokeWidth={2}
              dot={false}
              name="Ortalama Aşınma (µm)"
            />
            <Line
              type="monotone"
              dataKey="anomalies"
              stroke="#FB7185"
              strokeWidth={1.5}
              dot={false}
              strokeDasharray="4 4"
              name="Anomali Sayısı"
            />
          </LineChart>
        </ResponsiveContainer>
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
      {/* Stats */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <StatCard
          label="Aktif Anomaliler"
          value={activeCount}
          icon={AlertTriangle}
          trend="up"
          trendLabel="Bu saat +3"
          color="bg-rose/10 text-rose"
        />
        <StatCard
          label="Kritik Makineler"
          value={criticalMachines}
          unit="/ 8"
          icon={Shield}
          trend="up"
          trendLabel="Müdahale gerekli"
          color="bg-amber/10 text-amber"
        />
        <StatCard
          label="Ort. Aşınma"
          value={avgWear}
          unit="µm"
          icon={TrendingUp}
          trend="down"
          trendLabel="Son kontrolden -%2.1"
          color="bg-cyan/10 text-cyan"
        />
        <StatCard
          label="Sonraki Kritik"
          value={nextCritical.toFixed(1)}
          unit="saat"
          icon={Clock}
          trend="up"
          trendLabel="M-06 hızlanıyor"
          color="bg-violet/10 text-violet"
        />
      </motion.div>

      {/* Main grid */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 xl:grid-cols-3 gap-6"
      >
        <div className="xl:col-span-2 space-y-6">
          <MachineStatusGrid />
          <WearTrendChart />
          <RecentAnomalies />
        </div>
        <div className="space-y-5">
          <SystemHealth />
          {/* Parts alert */}
          <motion.div variants={stagger.item} className="bg-surface border border-border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Package className="w-4 h-4 text-amber" />
              <h2 className="text-sm font-semibold text-foreground font-heading">Parça Uyarıları</h2>
            </div>
            <div className="space-y-2">
              {[
                { part: 'Karbür Uç #7', risk: 'crisis', score: 0.92 },
                { part: 'Matkap Ucu 12mm', risk: 'at_risk', score: 0.74 },
                { part: 'Parmak Freze 6mm', risk: 'watch', score: 0.51 },
              ].map((item) => (
                <Link
                  key={item.part}
                  href="/dashboard/spare-parts"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-surface-2 transition-all"
                >
                  <div>
                    <span className="text-xs text-foreground font-medium">{item.part}</span>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <div className="h-1 w-12 rounded-full bg-surface-3 overflow-hidden">
                        <div
                          className={cn(
                            'h-full rounded-full',
                            item.risk === 'crisis' ? 'bg-rose' :
                            item.risk === 'at_risk' ? 'bg-amber' : 'bg-cyan'
                          )}
                          style={{ width: `${item.score * 100}%` }}
                        />
                      </div>
                      <span className="text-[9px] font-mono text-muted">{(item.score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className={cn(
                    'text-[10px] px-2.5 py-1 rounded-lg font-semibold',
                    item.risk === 'crisis' ? 'bg-rose/10 text-rose' :
                    item.risk === 'at_risk' ? 'bg-amber/10 text-amber' :
                    'bg-cyan/10 text-cyan'
                  )}>
                    {item.risk === 'crisis' ? 'Kriz' : item.risk === 'at_risk' ? 'Risk' : 'İzle'}
                  </div>
                </Link>
              ))}
              <Link href="/dashboard/spare-parts" className="block text-center text-xs text-cyan hover:text-cyan/80 mt-3 transition-colors font-medium">
                Kriz panosunu görüntüle →
              </Link>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
