'use client';

import { useMemo, use } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle2, Eye, EyeOff, Activity, Cpu } from 'lucide-react';
import Link from 'next/link';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine,
} from 'recharts';
import { getAnomalyDetailById } from '@/services/mock/anomalies';
import { SeverityBadge, StatusBadge } from '@/components/ui/badge';
import { cn, formatDateTime } from '@/lib/utils';
import { useState } from 'react';

const SENSOR_KEYS = ['accelerometer', 'acoustic', 'force_x', 'force_y', 'force_z'] as const;
const SENSOR_COLORS: Record<string, string> = {
  accelerometer: '#06B6D4',
  acoustic: '#8B5CF6',
  force_x: '#F43F5E',
  force_y: '#F59E0B',
  force_z: '#10B981',
};

function ScoreGauge({ score }: { score: number }) {
  const pct = score * 100;
  const radius = 52;
  const circumference = Math.PI * radius; // half circle
  const strokeDashoffset = circumference * (1 - score);
  const color = score > 0.75 ? '#F43F5E' : score > 0.5 ? '#F59E0B' : score > 0.3 ? '#06B6D4' : '#10B981';

  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox="0 0 120 70" className="w-32">
        {/* Track */}
        <path
          d="M 10 60 A 50 50 0 0 1 110 60"
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Fill */}
        <path
          d="M 10 60 A 50 50 0 0 1 110 60"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={`${circumference * (1 - score)}`}
          style={{ filter: `drop-shadow(0 0 6px ${color}80)` }}
        />
        <text x="60" y="56" textAnchor="middle" fill={color} fontSize="18" fontWeight="bold" fontFamily="monospace">
          {pct.toFixed(0)}
        </text>
        <text x="60" y="66" textAnchor="middle" fill="#9CA3AF" fontSize="9">
          SCORE
        </text>
      </svg>
    </div>
  );
}

function WearProbabilities({ probs }: { probs: { type: string; probability: number }[] }) {
  const sorted = [...probs].sort((a, b) => b.probability - a.probability);
  return (
    <div className="space-y-2">
      {sorted.map((p) => (
        <div key={p.type}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-foreground capitalize">{p.type.replace('_', ' ')}</span>
            <span className="text-xs font-mono text-muted">{(p.probability * 100).toFixed(0)}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-surface-3 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${p.probability * 100}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500"
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function SensorChart({ data, label, color }: { data: { t: number; value: number }[]; label: string; color: string }) {
  const peak = Math.max(...data.map((d) => d.value));
  const avgVal = data.reduce((s, d) => s + d.value, 0) / data.length;
  const anomalyIdx = data.findIndex((d) => d.value > avgVal * 1.6);

  return (
    <div className="bg-surface-2 rounded-xl p-4 border border-border">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-foreground capitalize">{label.replace('_', ' ')}</span>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-muted">peak: {peak.toFixed(3)}</span>
          <div className="w-2 h-2 rounded-full" style={{ background: color }} />
        </div>
      </div>
      <ResponsiveContainer width="100%" height={72}>
        <LineChart data={data} margin={{ top: 2, right: 2, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <YAxis hide domain={['auto', 'auto']} />
          <XAxis hide dataKey="t" />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#9CA3AF' }}
            itemStyle={{ color }}
            formatter={(v: unknown) => [(v as number).toFixed(3), label.replace('_', ' ')]}
          />
          {anomalyIdx > 0 && (
            <ReferenceLine x={data[anomalyIdx]?.t} stroke="rgba(244,63,94,0.5)" strokeDasharray="4 4" />
          )}
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={1.5} dot={false} activeDot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function AnomalyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const anomaly = useMemo(() => getAnomalyDetailById(id), [id]);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [activeSensors, setActiveSensors] = useState<string[]>(['accelerometer', 'acoustic', 'force_z']);

  const toggleSensor = (k: string) =>
    setActiveSensors((prev) => prev.includes(k) ? prev.filter((s) => s !== k) : [...prev, k]);

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard/anomalies" className="flex items-center gap-1.5 text-xs text-muted hover:text-foreground transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Anomalies
        </Link>
        <span className="text-muted">/</span>
        <span className="text-xs font-mono text-foreground">{anomaly.id}</span>
      </div>

      {/* Hero row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Image panel */}
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-sm font-semibold text-foreground font-heading">{anomaly.machine_id} — Tool Inspection</h2>
              <SeverityBadge severity={anomaly.severity} />
              <StatusBadge status={anomaly.status} />
            </div>
            <button
              onClick={() => setShowHeatmap((p) => !p)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-surface-2 border border-border text-muted hover:text-foreground hover:border-border-strong transition-all"
            >
              {showHeatmap ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              {showHeatmap ? 'Raw Image' : 'Heatmap'}
            </button>
          </div>

          {/* Image placeholder with bounding box overlay */}
          <div className="relative w-full aspect-video bg-surface-2 rounded-xl border border-border overflow-hidden flex items-center justify-center">
            <div className="text-center text-muted space-y-2">
              <Cpu className="w-10 h-10 mx-auto opacity-20" />
              <p className="text-xs">{showHeatmap ? 'Grad-CAM Heatmap' : 'Tool Inspection Image'}</p>
              <p className="text-[11px] opacity-50">{anomaly.image_id}</p>
            </div>
            {/* Bounding box */}
            {anomaly.anomaly_region && (
              <div
                className="absolute border-2 border-rose-500 rounded"
                style={{
                  left: `${(anomaly.anomaly_region.x / 800) * 100}%`,
                  top: `${(anomaly.anomaly_region.y / 600) * 100}%`,
                  width: `${(anomaly.anomaly_region.w / 800) * 100}%`,
                  height: `${(anomaly.anomaly_region.h / 600) * 100}%`,
                  boxShadow: '0 0 8px rgba(244,63,94,0.6)',
                }}
              >
                <span className="absolute -top-5 left-0 text-[10px] bg-rose-500 text-white px-1 rounded">
                  Anomaly Region
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4 text-xs text-muted">
            <span>Detected: {formatDateTime(anomaly.timestamp)}</span>
            <span className="text-border">|</span>
            <span>Set: {anomaly.set_id}</span>
            <span className="text-border">|</span>
            <span>Tool: {anomaly.tool_id}</span>
          </div>
        </div>

        {/* Score + probs */}
        <div className="space-y-4">
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="text-xs font-medium text-muted mb-4">Anomaly Score</h3>
            <ScoreGauge score={anomaly.anomaly_score} />
            <div className="mt-3 text-center">
              <p className="text-xs text-muted">Estimated wear</p>
              <p className="text-xl font-bold font-heading text-foreground">{anomaly.estimated_wear_um} <span className="text-sm font-normal text-muted">µm</span></p>
            </div>
          </div>

          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="text-xs font-medium text-muted mb-4">Wear Type Probabilities</h3>
            <WearProbabilities probs={anomaly.wear_probabilities} />
          </div>

          <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium hover:bg-cyan-500/20 transition-all">
            <CheckCircle2 className="w-4 h-4" />
            Mark as Reviewed
          </button>
        </div>
      </div>

      {/* Sensor charts */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-foreground font-heading">Sensor Data</h2>
          </div>
          <div className="flex items-center gap-2">
            {SENSOR_KEYS.map((k) => (
              <button
                key={k}
                onClick={() => toggleSensor(k)}
                className={cn(
                  'text-[11px] px-2.5 py-1 rounded-lg border transition-all capitalize',
                  activeSensors.includes(k)
                    ? 'border-transparent text-white'
                    : 'border-border bg-surface-2 text-muted hover:text-foreground'
                )}
                style={activeSensors.includes(k) ? {
                  background: SENSOR_COLORS[k] + '20',
                  borderColor: SENSOR_COLORS[k] + '50',
                  color: SENSOR_COLORS[k],
                } : {}}
              >
                {k.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {SENSOR_KEYS.filter((k) => activeSensors.includes(k)).map((key) => (
            <SensorChart
              key={key}
              data={anomaly.sensor_data[key]}
              label={key}
              color={SENSOR_COLORS[key]}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
