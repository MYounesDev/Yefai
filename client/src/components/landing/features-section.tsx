'use client';

import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Eye, TrendingUp, Shield, Zap, BarChart3, Layers, Cpu, Bell } from 'lucide-react';

const features = [
  {
    icon: Eye,
    title: 'NovaVision AI',
    desc: 'YOLO-NAS-L powered computer vision fuses camera and sensor streams to detect wear anomalies with zero-shot precision at the sub-millimeter level.',
    color: 'cyan',
    gradient: 'from-cyan/20 to-transparent',
    borderGlow: 'hover:border-cyan/30 hover:shadow-[0_0_24px_rgba(0,212,255,0.12)]',
    iconBg: 'bg-cyan/10 text-cyan',
    badge: 'Computer Vision',
  },
  {
    icon: TrendingUp,
    title: 'Predictive Forecasting',
    desc: 'Physics-informed wear rate models project when a tool will reach its critical threshold — days ahead — enabling precise maintenance windows.',
    color: 'violet',
    gradient: 'from-violet/20 to-transparent',
    borderGlow: 'hover:border-violet/30 hover:shadow-[0_0_24px_rgba(167,139,250,0.12)]',
    iconBg: 'bg-violet/10 text-violet',
    badge: 'ML Forecasting',
  },
  {
    icon: Shield,
    title: 'Crisis Score',
    desc: 'Unified risk score combining anomaly severity, stock levels, and supplier lead times. Triages factory-wide risk in a single glance.',
    color: 'amber',
    gradient: 'from-amber/20 to-transparent',
    borderGlow: 'hover:border-amber/30 hover:shadow-[0_0_24px_rgba(251,191,36,0.12)]',
    iconBg: 'bg-amber/10 text-amber',
    badge: 'Risk Engine',
  },
  {
    icon: Zap,
    title: 'Automated Procurement',
    desc: 'When a threshold is crossed, Yefai automatically creates purchase orders, contacts preferred suppliers, and tracks delivery — zero human latency.',
    color: 'emerald',
    gradient: 'from-emerald/20 to-transparent',
    borderGlow: 'hover:border-emerald/30 hover:shadow-[0_0_24px_rgba(52,211,153,0.12)]',
    iconBg: 'bg-emerald/10 text-emerald',
    badge: 'Supply Chain',
  },
  {
    icon: Bell,
    title: 'Omnichannel Alerts',
    desc: 'Telegram, email, and SMS push instantly when anomalies breach configurable thresholds. Escalation trees and on-call routing built in.',
    color: 'rose',
    gradient: 'from-rose/20 to-transparent',
    borderGlow: 'hover:border-rose/30 hover:shadow-[0_0_24px_rgba(251,113,133,0.12)]',
    iconBg: 'bg-rose/10 text-rose',
    badge: 'Notifications',
  },
  {
    icon: BarChart3,
    title: 'RAG Analytics Chatbot',
    desc: 'Ask anything in natural language. The AI assistant retrieves live sensor data, historical trends, and anomaly reports across your entire fleet.',
    color: 'cyan',
    gradient: 'from-cyan/20 to-transparent',
    borderGlow: 'hover:border-cyan/30 hover:shadow-[0_0_24px_rgba(0,212,255,0.10)]',
    iconBg: 'bg-cyan/10 text-cyan',
    badge: 'LLM + RAG',
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.7, ease: [0.22, 1, 0.36, 1] as const },
  }),
};
const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.07 } } };

/* ── Big "spotlight" feature card ── */
function SpotlightCard({ feature, i }: { feature: typeof features[0]; i: number }) {
  return (
    <motion.div
      variants={fadeUp}
      custom={i}
      className={`group relative p-7 rounded-2xl bg-surface border border-border ${feature.borderGlow} transition-all duration-300 overflow-hidden`}
    >
      {/* Background gradient that reveals on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`} />

      {/* Corner lines — HUD style */}
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-current opacity-0 group-hover:opacity-30 transition-opacity" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-current opacity-0 group-hover:opacity-30 transition-opacity" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-5">
          <div className={`w-12 h-12 rounded-xl ${feature.iconBg} flex items-center justify-center group-hover:scale-105 transition-transform`}>
            <feature.icon className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-mono text-muted/60 border border-border px-2.5 py-1 rounded-full tracking-wider">
            {feature.badge}
          </span>
        </div>
        <h3 className="text-base font-heading font-semibold text-foreground mb-3">{feature.title}</h3>
        <p className="text-sm text-muted leading-relaxed">{feature.desc}</p>
      </div>
    </motion.div>
  );
}

export function FeaturesSection() {
  return (
    <section id="features" className="relative z-10 py-28 px-6 overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-violet/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.div variants={fadeUp} custom={0} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet/8 border border-violet/20 text-violet text-xs font-mono tracking-wider uppercase mb-5">
            <Layers className="w-3.5 h-3.5" />
            Platform Capabilities
          </motion.div>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-5xl font-heading font-bold mb-5 text-balance">
            Built for{' '}
            <span className="text-gradient">Industry 4.0</span>
          </motion.h2>
          <motion.p variants={fadeUp} custom={2} className="text-muted max-w-2xl mx-auto text-base leading-relaxed">
            Every layer — from edge inference on the factory floor to executive dashboards —
            is purpose-built to keep your machines running and procurement ahead of demand.
          </motion.p>
        </motion.div>

        {/* Grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
        >
          {features.map((f, i) => (
            <SpotlightCard key={f.title} feature={f} i={i} />
          ))}
        </motion.div>

        {/* Bottom floating sensor strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="mt-12 p-5 rounded-2xl border border-border bg-surface/50 backdrop-blur-sm"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <Cpu className="w-4 h-4 text-cyan" />
              <span className="text-sm font-medium text-foreground">Supported sensor modalities</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {['Vibration', 'Acoustic Emission', 'Temperature', 'Force / Torque', 'Current (Motor)', 'Camera RGB', 'Depth (LiDAR)', 'Spindle Load'].map((s) => (
                <span key={s} className="px-3 py-1 rounded-full text-[11px] font-mono text-muted border border-border bg-surface-2 hover:border-cyan/30 hover:text-cyan transition-colors">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
