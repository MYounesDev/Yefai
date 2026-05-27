'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { Activity, AlertTriangle, TrendingUp, Package, CheckCircle2, Wifi } from 'lucide-react';

/* ── Mock chart bars ── */
function WearChart() {
  const bars = [22, 28, 31, 35, 38, 42, 45, 49, 53, 57, 62, 67];
  return (
    <div className="flex items-end gap-1 h-16 w-full">
      {bars.map((h, i) => (
        <motion.div
          key={i}
          className="flex-1 rounded-sm"
          style={{
            background: h > 55
              ? 'rgba(251,113,133,0.7)'
              : h > 40
                ? 'rgba(251,191,36,0.7)'
                : 'rgba(0,212,255,0.6)',
            height: 0,
          }}
          animate={{ height: `${(h / 67) * 100}%` }}
          transition={{ delay: 0.8 + i * 0.05, duration: 0.5, ease: 'easeOut' }}
        />
      ))}
    </div>
  );
}

/* ── Mock anomaly list row ── */
function AnomalyRow({ machine, score, status, delay }: { machine: string; score: number; status: 'critical' | 'warning' | 'normal'; delay: number }) {
  const colors = { critical: 'text-rose', warning: 'text-amber', normal: 'text-emerald' };
  const dotColors = { critical: 'bg-rose animate-pulse-glow', warning: 'bg-amber', normal: 'bg-emerald' };
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="flex items-center gap-3 py-2.5 border-b border-border last:border-0"
    >
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColors[status]}`} />
      <span className="text-xs font-mono text-foreground flex-1">{machine}</span>
      <div className="flex items-center gap-1.5">
        <div className="w-20 h-1.5 bg-surface-3 rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full ${status === 'critical' ? 'bg-rose' : status === 'warning' ? 'bg-amber' : 'bg-emerald'}`}
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ delay: delay + 0.2, duration: 0.6 }}
          />
        </div>
        <span className={`text-[10px] font-mono w-8 text-right ${colors[status]}`}>{score}%</span>
      </div>
    </motion.div>
  );
}

export function DashboardPreviewSection() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const cardY = useTransform(scrollYProgress, [0, 1], [60, -60]);
  const card2Y = useTransform(scrollYProgress, [0, 1], [40, -40]);

  return (
    <section ref={ref} className="relative z-10 py-28 px-6 overflow-hidden">
      {/* Separator */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

      {/* Background glow */}
      <div className="absolute top-1/2 right-0 w-[500px] h-[500px] bg-cyan/6 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

          {/* ── Left: Copy ── */}
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
          >
            {[
              <motion.p
                key="label"
                variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6 } } }}
                className="text-xs font-mono text-cyan tracking-[0.2em] uppercase mb-5"
              >
                Live Dashboard
              </motion.p>,
              <motion.h2
                key="h2"
                variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.7 } } }}
                className="text-3xl sm:text-5xl font-heading font-bold mb-6 text-balance"
              >
                Full Factory{' '}
                <span className="text-gradient">Visibility</span>
                <br />in One View
              </motion.h2>,
              <motion.p
                key="desc"
                variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6 } } }}
                className="text-muted text-base leading-relaxed mb-8 max-w-[480px]"
              >
                Yefai&apos;s unified dashboard aggregates every machine&apos;s health, anomaly history,
                wear trends, spare part inventory, and open purchase orders into a single real-time view.
              </motion.p>,
              <motion.ul
                key="list"
                variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }}
                className="space-y-3"
              >
                {[
                  { icon: Activity, text: 'Live anomaly feed with severity scoring' },
                  { icon: TrendingUp, text: 'Tool wear trend analysis per machine' },
                  { icon: Package, text: 'Spare parts inventory & reorder triggers' },
                  { icon: CheckCircle2, text: 'PO status tracking from creation to delivery' },
                ].map((item) => (
                  <motion.li
                    key={item.text}
                    variants={{ hidden: { opacity: 0, x: -16 }, visible: { opacity: 1, x: 0, transition: { duration: 0.5 } } }}
                    className="flex items-start gap-3"
                  >
                    <div className="w-6 h-6 rounded-lg bg-cyan/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <item.icon className="w-3.5 h-3.5 text-cyan" />
                    </div>
                    <span className="text-sm text-muted">{item.text}</span>
                  </motion.li>
                ))}
              </motion.ul>,
            ]}
          </motion.div>

          {/* ── Right: Floating UI panels ── */}
          <div className="relative min-h-[520px]">

            {/* Main dashboard card */}
            <motion.div
              style={{ y: cardY }}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="relative rounded-2xl border border-border bg-surface shadow-elevated overflow-hidden"
            >
              {/* Card top bar */}
              <div className="flex items-center gap-2 px-5 py-3.5 border-b border-border bg-surface-2">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald/60" />
                </div>
                <span className="text-[10px] font-mono text-muted flex-1 text-center">Factory Floor — Live</span>
                <div className="flex items-center gap-1.5 text-[10px] font-mono text-emerald">
                  <Wifi className="w-3 h-3" />
                  Connected
                </div>
              </div>

              <div className="p-5">
                {/* Header stats row */}
                <div className="grid grid-cols-3 gap-3 mb-5">
                  {[
                    { label: 'Machines Online', value: '12 / 14', color: 'text-emerald' },
                    { label: 'Active Anomalies', value: '3', color: 'text-rose' },
                    { label: 'Avg Wear Index', value: '44%', color: 'text-amber' },
                  ].map((s) => (
                    <div key={s.label} className="p-3 rounded-xl bg-surface-2 border border-border">
                      <p className={`text-lg font-heading font-bold ${s.color}`}>{s.value}</p>
                      <p className="text-[10px] text-muted mt-0.5 leading-tight">{s.label}</p>
                    </div>
                  ))}
                </div>

                {/* Wear trend chart */}
                <div className="mb-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-mono text-muted">Spindle-C Wear Trend (24h)</span>
                    <span className="text-[10px] font-mono text-rose">+29% / shift</span>
                  </div>
                  <WearChart />
                </div>

                {/* Anomaly list */}
                <div>
                  <span className="text-[11px] font-mono text-muted block mb-2">Recent Anomalies</span>
                  <AnomalyRow machine="CNC-03 · Spindle-C" score={82} status="critical" delay={1.0} />
                  <AnomalyRow machine="CNC-07 · Insert-B4" score={61} status="warning" delay={1.15} />
                  <AnomalyRow machine="CNC-01 · Drill-A2" score={23} status="normal" delay={1.30} />
                </div>
              </div>
            </motion.div>

            {/* Floating alert card */}
            <motion.div
              style={{ y: card2Y }}
              initial={{ opacity: 0, x: 30, scale: 0.9 }}
              whileInView={{ opacity: 1, x: 0, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
              className="absolute -bottom-8 -right-6 glass-card border border-rose/25 p-4 rounded-2xl min-w-[200px] shadow-[0_0_32px_rgba(251,113,133,0.12)]"
              style={{ backdropFilter: 'blur(20px)' } as React.CSSProperties}
            >
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-rose" />
                <span className="text-[11px] font-semibold text-rose">Crisis Alert</span>
              </div>
              <p className="text-[11px] text-foreground font-medium">CNC-03 Spindle-C</p>
              <p className="text-[10px] text-muted mt-0.5">Failure in ~2.3h · PO #4821 sent</p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
