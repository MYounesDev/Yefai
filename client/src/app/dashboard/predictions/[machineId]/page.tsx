'use client';

import { useMemo, use } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, ReferenceLine, Legend,
} from 'recharts';
import { getMockPrediction } from '@/services/mock/predictions';
import { StatusDot } from '@/components/ui/status-dot';
import { cn } from '@/lib/utils';

const confidenceColor: Record<string, string> = {
  high: 'text-emerald-400', medium: 'text-amber-400', low: 'text-rose-400',
};

const SCENARIO_COLORS = {
  pessimistic: '#F43F5E',
  baseline: '#06B6D4',
  optimistic: '#10B981',
};

function buildChartData(pred: ReturnType<typeof getMockPrediction>) {
  const hist = pred.historical_data;
  const lastHour = hist[hist.length - 1]?.hour ?? 0;
  const lastWear = hist[hist.length - 1]?.wear_um ?? pred.current_wear_um;

  const projectionPoints = 24;
  const projRows = Array.from({ length: projectionPoints }, (_, i) => {
    const hour = lastHour + (i + 1) * 2;
    const scenarios = pred.scenarios;
    return {
      hour,
      pessimistic: Math.min(pred.critical_threshold_um + 10, parseFloat((lastWear + scenarios[0].wear_rate_um_per_hour * (i + 1) * 2).toFixed(1))),
      baseline: Math.min(pred.critical_threshold_um + 10, parseFloat((lastWear + scenarios[1].wear_rate_um_per_hour * (i + 1) * 2).toFixed(1))),
      optimistic: Math.min(pred.critical_threshold_um + 10, parseFloat((lastWear + scenarios[2].wear_rate_um_per_hour * (i + 1) * 2).toFixed(1))),
      wear_um: undefined as number | undefined,
    };
  });

  const histRows = hist.map((d) => ({
    hour: d.hour,
    wear_um: d.wear_um,
    pessimistic: undefined as number | undefined,
    baseline: undefined as number | undefined,
    optimistic: undefined as number | undefined,
  }));

  // Connect at last historical point
  if (projRows.length > 0) {
    projRows[0].pessimistic = lastWear;
    projRows[0].baseline = lastWear;
    projRows[0].optimistic = lastWear;
  }

  return [...histRows, ...projRows];
}

export default function PredictionDetailPage({ params }: { params: Promise<{ machineId: string }> }) {
  const { machineId } = use(params);
  const pred = useMemo(() => getMockPrediction(machineId), [machineId]);
  const chartData = useMemo(() => buildChartData(pred), [pred]);

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard/predictions" className="flex items-center gap-1.5 text-xs text-muted hover:text-foreground transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Predictions
        </Link>
        <span className="text-muted">/</span>
        <span className="text-xs text-foreground">{pred.machine_name}</span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusDot status={pred.status} size="lg" />
          <div>
            <h1 className="text-xl font-bold font-heading text-foreground">{pred.machine_name}</h1>
            <p className="text-xs text-muted capitalize">{pred.status} · {pred.trend} wear trend</p>
          </div>
        </div>
        <button className="flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg bg-surface border border-border text-muted hover:text-foreground hover:border-border-strong transition-all">
          <RefreshCw className="w-3.5 h-3.5" />
          Recalculate
        </button>
      </div>

      {/* KPI strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Current Wear', value: `${pred.current_wear_um} µm`, sub: `/ ${pred.critical_threshold_um} µm threshold` },
          { label: 'Wear Rate', value: `${pred.wear_rate_um_per_hour} µm/h`, sub: 'baseline rate' },
          { label: 'Hours to Critical', value: `${pred.hours_to_critical.toFixed(0)}h`, sub: pred.scenarios[1].projected_date.slice(0, 10) },
          { label: 'Confidence', value: pred.confidence.charAt(0).toUpperCase() + pred.confidence.slice(1), sub: 'model confidence', color: confidenceColor[pred.confidence] },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-surface border border-border rounded-xl p-4">
            <p className="text-xs text-muted mb-1">{kpi.label}</p>
            <p className={cn('text-xl font-bold font-heading', kpi.color ?? 'text-foreground')}>{kpi.value}</p>
            <p className="text-[11px] text-muted mt-0.5">{kpi.sub}</p>
          </div>
        ))}
      </div>

      {/* Wear projection chart */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground font-heading">Wear Projection</h2>
          <div className="flex items-center gap-3">
            {pred.scenarios.map((s) => (
              <div key={s.label} className="flex items-center gap-1.5 text-[11px]">
                <div className="w-3 h-0.5 rounded-full" style={{ background: SCENARIO_COLORS[s.label] }} />
                <span className="text-muted capitalize">{s.label}</span>
                <span className="text-foreground font-mono">{s.hours_to_critical.toFixed(0)}h</span>
              </div>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis
              dataKey="hour"
              tick={{ fontSize: 11, fill: '#9CA3AF' }}
              label={{ value: 'Hours', position: 'insideBottomRight', offset: -8, fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#9CA3AF' }}
              label={{ value: 'Wear (µm)', angle: -90, position: 'insideLeft', fill: '#9CA3AF', fontSize: 11 }}
              domain={[0, pred.critical_threshold_um + 20]}
            />
            <Tooltip
              contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 11 }}
              labelFormatter={(v) => `Hour ${v}`}
            />
            <ReferenceLine
              y={pred.critical_threshold_um}
              stroke="#F43F5E"
              strokeDasharray="6 4"
              label={{ value: 'Critical', fill: '#F43F5E', fontSize: 10, position: 'insideTopRight' }}
            />
            {/* Historical */}
            <Line type="monotone" dataKey="wear_um" stroke="#E5E7EB" strokeWidth={2} dot={false} name="Historical" connectNulls={false} />
            {/* Projections */}
            <Area type="monotone" dataKey="pessimistic" stroke={SCENARIO_COLORS.pessimistic} strokeWidth={1.5} fill={SCENARIO_COLORS.pessimistic + '15'} dot={false} name="Pessimistic" connectNulls={false} />
            <Area type="monotone" dataKey="baseline" stroke={SCENARIO_COLORS.baseline} strokeWidth={2} fill={SCENARIO_COLORS.baseline + '10'} dot={false} name="Baseline" connectNulls={false} />
            <Area type="monotone" dataKey="optimistic" stroke={SCENARIO_COLORS.optimistic} strokeWidth={1.5} fill={SCENARIO_COLORS.optimistic + '10'} dot={false} name="Optimistic" connectNulls={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Last inspections table */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-sm font-semibold text-foreground font-heading mb-4">Inspection History</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border text-muted">
                <th className="pb-2 text-left font-medium">Inspection #</th>
                <th className="pb-2 text-right font-medium">Wear (µm)</th>
                <th className="pb-2 text-right font-medium">Rate (µm/h)</th>
                <th className="pb-2 text-right font-medium">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {pred.last_inspections.map((ins, i) => {
                const prev = pred.last_inspections[i - 1];
                const delta = prev ? ins.wear_um - prev.wear_um : null;
                return (
                  <tr key={ins.inspection_num} className="hover:bg-surface-2 transition-colors">
                    <td className="py-2.5 text-foreground font-mono">#{ins.inspection_num}</td>
                    <td className="py-2.5 text-right font-mono text-foreground">{ins.wear_um}</td>
                    <td className="py-2.5 text-right font-mono text-muted">{ins.rate}</td>
                    <td className="py-2.5 text-right font-mono">
                      {delta !== null ? (
                        <span className={delta > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                          {delta > 0 ? '+' : ''}{delta}
                        </span>
                      ) : <span className="text-muted">—</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
