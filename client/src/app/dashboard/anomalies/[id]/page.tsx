'use client';

import { use, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Camera, Activity } from 'lucide-react';
import Link from 'next/link';
import {
  LineChart, Line, ResponsiveContainer, Tooltip, CartesianGrid, XAxis, YAxis,
} from 'recharts';
import { getAnomalyDetailById } from '@/services/mock/anomalies';
import { SeverityBadge, StatusBadge, ProgressBar } from '@/components/ui/index';
import { cn, formatDateTime } from '@/lib/utils';

const sensorColors: Record<string, string> = {
  accelerometer: '#00D4FF',
  acoustic: '#A78BFA',
  force_x: '#FB7185',
  force_y: '#FBBF24',
  force_z: '#34D399',
};

const sensorLabels: Record<string, string> = {
  accelerometer: 'İvmeölçer',
  acoustic: 'Akustik',
  force_x: 'Kuvvet X',
  force_y: 'Kuvvet Y',
  force_z: 'Kuvvet Z',
};

const wearTypeLabels: Record<string, string> = {
  flank_wear: 'Yanak Aşınması',
  adhesion: 'Yapışma',
  combination: 'Kombine',
};

export default function AnomalyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const anomaly = useMemo(() => getAnomalyDetailById(id), [id]);

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3">
        <Link
          href="/dashboard/anomalies"
          className="p-2 rounded-xl hover:bg-surface-2 text-muted hover:text-foreground transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-base font-heading font-bold text-foreground">
            Anomali Detayı — {anomaly.machine_id}
          </h1>
          <p className="text-[11px] text-muted">{anomaly.id} · {formatDateTime(anomaly.timestamp)}</p>
        </div>
      </div>

      {/* Top Info Cards */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Anomali Skoru', value: anomaly.anomaly_score.toFixed(3), color: anomaly.anomaly_score > 0.7 ? 'text-rose' : 'text-amber' },
          { label: 'Tahmini Aşınma', value: `${anomaly.estimated_wear_um} µm`, color: 'text-foreground' },
          { label: 'Aşınma Türü', value: wearTypeLabels[anomaly.wear_type] || anomaly.wear_type, color: 'text-cyan' },
          { label: 'Şiddet', value: '', color: '' },
        ].map((item, i) => (
          <div key={i} className="bg-surface border border-border rounded-xl p-4">
            <p className="text-[11px] text-muted tracking-wide uppercase mb-1.5">{item.label}</p>
            {item.label === 'Şiddet' ? (
              <div className="flex items-center gap-2">
                <SeverityBadge severity={anomaly.severity} />
                <StatusBadge status={anomaly.status} />
              </div>
            ) : (
              <p className={cn('text-lg font-heading font-bold', item.color)}>{item.value}</p>
            )}
          </div>
        ))}
      </motion.div>

      {/* Split View: Image + Sensors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Camera / Image */}
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <Camera className="w-4 h-4 text-cyan" />
            <h2 className="text-sm font-semibold font-heading text-foreground">Kamera Görüntüsü</h2>
          </div>
          <div className="relative aspect-[4/3] rounded-xl bg-surface-2 border border-border overflow-hidden">
            {/* Simulated heatmap overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 rounded-full bg-rose/15 border-2 border-rose/30 flex items-center justify-center mb-3 mx-auto animate-pulse-glow">
                  <AlertTriangle className="w-8 h-8 text-rose" />
                </div>
                <p className="text-xs text-muted">Anomali Bölgesi Tespit Edildi</p>
                <p className="text-[10px] text-muted mt-1">
                  Konum: ({anomaly.anomaly_region?.x}, {anomaly.anomaly_region?.y}) —
                  Boyut: {anomaly.anomaly_region?.w}×{anomaly.anomaly_region?.h}px
                </p>
              </div>
            </div>
            {/* Scanner line effect */}
            <div className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan to-transparent opacity-50" style={{ animation: 'scanner-line 3s linear infinite' }} />
          </div>

          {/* Wear Probabilities */}
          <div className="mt-5 space-y-3">
            <h3 className="text-xs font-semibold text-muted tracking-wide uppercase">Aşınma Olasılıkları</h3>
            {anomaly.wear_probabilities.map((wp) => (
              <div key={wp.type} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-foreground font-medium capitalize">{wearTypeLabels[wp.type] || wp.type}</span>
                  <span className="font-mono text-muted">{(wp.probability * 100).toFixed(0)}%</span>
                </div>
                <ProgressBar
                  value={wp.probability * 100}
                  max={100}
                  color={wp.probability > 0.6 ? 'rose' : wp.probability > 0.3 ? 'amber' : 'cyan'}
                  size="sm"
                />
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right: Sensor Data */}
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-violet" />
            <h2 className="text-sm font-semibold font-heading text-foreground">Sensör Verileri</h2>
          </div>
          <div className="space-y-5">
            {Object.entries(anomaly.sensor_data).map(([key, data]) => (
              <div key={key}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-foreground">{sensorLabels[key] || key}</span>
                  <span className="text-[10px] font-mono text-muted">{data.length} nokta</span>
                </div>
                <div className="h-20 rounded-lg bg-surface-2 border border-border/50 p-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.slice(0, 80)}>
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke={sensorColors[key] || '#00D4FF'}
                        strokeWidth={1.2}
                        dot={false}
                      />
                      <Tooltip
                        contentStyle={{
                          background: 'var(--color-surface)',
                          border: '1px solid var(--color-border)',
                          borderRadius: '8px',
                          fontSize: '10px',
                          color: 'var(--color-foreground)',
                        }}
                        formatter={(value: number) => [value.toFixed(3), sensorLabels[key]]}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
