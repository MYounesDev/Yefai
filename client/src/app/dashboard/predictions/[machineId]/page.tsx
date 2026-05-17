'use client';

import { use, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, Clock, Activity, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import {
  LineChart, Line, ResponsiveContainer, Tooltip, CartesianGrid, XAxis, YAxis, Legend, ReferenceLine,
} from 'recharts';
import { getMockPrediction } from '@/services/mock/predictions';
import { StatusDot, ProgressBar } from '@/components/ui/index';
import { cn, formatDateTime } from '@/lib/utils';

const trendLabels: Record<string, string> = { accelerating: 'Hızlanıyor', stable: 'Sabit', decelerating: 'Yavaşlıyor' };
const scenarioLabels: Record<string, string> = { pessimistic: 'Kötümser', baseline: 'Baz', optimistic: 'İyimser' };

export default function PredictionDetailPage({ params }: { params: Promise<{ machineId: string }> }) {
  const { machineId } = use(params);
  const prediction = useMemo(() => getMockPrediction(machineId), [machineId]);

  // Build scenario projection data
  const projectionData = useMemo(() => {
    const historical = prediction.historical_data;
    const lastHour = historical[historical.length - 1]?.hour || 0;
    const currentWear = prediction.current_wear_um;
    const points = [];

    for (let i = 0; i <= 30; i++) {
      const hour = lastHour + i * 2;
      const point: Record<string, number> = { hour };

      if (i === 0) {
        point.pessimistic = currentWear;
        point.baseline = currentWear;
        point.optimistic = currentWear;
      } else {
        prediction.scenarios.forEach((s) => {
          point[s.label] = Math.min(250, currentWear + s.wear_rate_um_per_hour * i * 2);
        });
      }
      points.push(point);
    }
    return points;
  }, [prediction]);

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard/predictions" className="p-2 rounded-xl hover:bg-surface-2 text-muted hover:text-foreground transition-all">
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div className="flex items-center gap-3">
          <StatusDot status={prediction.status} />
          <div>
            <h1 className="text-base font-heading font-bold text-foreground">
              {prediction.machine_name} ({prediction.machine_id})
            </h1>
            <p className="text-[11px] text-muted">Son güncelleme: {formatDateTime(prediction.last_updated)}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Mevcut Aşınma', value: `${prediction.current_wear_um} µm`, icon: Activity, color: 'text-foreground' },
          { label: 'Kritiğe Kalan', value: `${prediction.hours_to_critical.toFixed(1)} saat`, icon: Clock, color: prediction.hours_to_critical < 24 ? 'text-rose' : 'text-emerald' },
          { label: 'Aşınma Hızı', value: `${prediction.wear_rate_um_per_hour} µm/s`, icon: TrendingUp, color: 'text-cyan' },
          { label: 'Trend', value: trendLabels[prediction.trend], icon: BarChart3, color: prediction.trend === 'accelerating' ? 'text-rose' : prediction.trend === 'decelerating' ? 'text-emerald' : 'text-muted' },
        ].map((s, i) => (
          <div key={i} className="bg-surface border border-border rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <s.icon className="w-3.5 h-3.5 text-muted" />
              <p className="text-[11px] text-muted tracking-wide uppercase">{s.label}</p>
            </div>
            <p className={cn('text-lg font-heading font-bold', s.color)}>{s.value}</p>
          </div>
        ))}
      </motion.div>

      {/* Wear bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-surface border border-border rounded-xl p-5"
      >
        <div className="flex justify-between text-xs mb-2">
          <span className="text-muted">Aşınma İlerlemesi</span>
          <span className="font-mono text-foreground">{prediction.current_wear_um} / {prediction.critical_threshold_um} µm</span>
        </div>
        <ProgressBar
          value={prediction.current_wear_um}
          max={prediction.critical_threshold_um}
          color={prediction.status === 'critical' ? 'rose' : prediction.status === 'warning' ? 'amber' : 'cyan'}
          size="md"
        />
      </motion.div>

      {/* Scenario Chart */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-surface border border-border rounded-xl p-5"
      >
        <h2 className="text-sm font-heading font-semibold text-foreground mb-4">Senaryo Projeksiyonları</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={projectionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="hour" tick={{ fontSize: 10, fill: 'var(--color-muted)' }} tickFormatter={(v) => `${v}s`} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--color-muted)' }} tickFormatter={(v) => `${v}µm`} />
              <Tooltip
                contentStyle={{
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '10px',
                  fontSize: '11px',
                  color: 'var(--color-foreground)',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <ReferenceLine y={prediction.critical_threshold_um} stroke="#FB7185" strokeDasharray="8 4" label={{ value: 'Kritik Eşik', position: 'right', fill: '#FB7185', fontSize: 10 }} />
              {prediction.scenarios.map((s) => (
                <Line
                  key={s.label}
                  type="monotone"
                  dataKey={s.label}
                  stroke={s.color}
                  strokeWidth={s.label === 'baseline' ? 2.5 : 1.5}
                  strokeDasharray={s.label !== 'baseline' ? '6 4' : undefined}
                  dot={false}
                  name={scenarioLabels[s.label]}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Scenarios + Inspections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scenarios Table */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <h2 className="text-sm font-heading font-semibold text-foreground mb-4">Senaryolar</h2>
          <div className="space-y-3">
            {prediction.scenarios.map((s) => (
              <div key={s.label} className="flex items-center justify-between p-3 rounded-xl bg-surface-2 border border-border/50">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                  <div>
                    <p className="text-xs font-semibold text-foreground">{scenarioLabels[s.label]}</p>
                    <p className="text-[10px] text-muted">{s.wear_rate_um_per_hour} µm/s</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs font-mono font-semibold text-foreground">{s.hours_to_critical.toFixed(0)} saat</p>
                  <p className="text-[10px] text-muted">{formatDateTime(s.projected_date)}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Last Inspections */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <h2 className="text-sm font-heading font-semibold text-foreground mb-4">Son Denetimler</h2>
          <div className="space-y-2">
            {prediction.last_inspections.map((insp) => (
              <div key={insp.inspection_num} className="flex items-center justify-between p-3 rounded-xl hover:bg-surface-2 transition-all">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-muted w-6">#{insp.inspection_num}</span>
                  <span className="text-xs text-foreground font-medium">{insp.wear_um} µm</span>
                </div>
                <span className="text-[11px] font-mono text-muted">{insp.rate} µm/s</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
