'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { Camera, Brain, BarChart2, ShoppingCart, ArrowDown } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Camera,
    title: 'Capture',
    subtitle: 'Edge Data Ingestion',
    desc: 'Industrial cameras, vibration sensors, and acoustic emission probes stream data continuously from CNC machines and assembly lines to the Yefai edge node.',
    detail: 'USB3 Vision · GigE · Modbus · OPC-UA · MQTT',
    color: 'cyan',
    dotColor: 'bg-cyan',
  },
  {
    number: '02',
    icon: Brain,
    title: 'Analyze',
    subtitle: 'Multimodal AI Inference',
    desc: 'NovaVision runs YOLO-NAS-L object detection on image frames while Anomalib scores acoustic and vibration signals — all fused in a unified wear index in <50ms.',
    detail: 'YOLO-NAS-L · Anomalib · EfficientAD',
    color: 'violet',
    dotColor: 'bg-violet',
  },
  {
    number: '03',
    icon: BarChart2,
    title: 'Predict',
    subtitle: 'Failure Horizon Forecasting',
    desc: 'Bayesian wear-rate models extrapolate current degradation curves to produce a failure ETA with confidence intervals — giving maintenance teams days of runway.',
    detail: '94% avg. forecast confidence · RUL estimation',
    color: 'amber',
    dotColor: 'bg-amber',
  },
  {
    number: '04',
    icon: ShoppingCart,
    title: 'Act',
    subtitle: 'Automated Procurement',
    desc: 'Crisis Score triggers automatic purchase orders through preferred supplier integrations, sends omnichannel alerts, and updates inventory — zero manual steps.',
    detail: 'PO auto-generation · Supplier API · ERP sync',
    color: 'emerald',
    dotColor: 'bg-emerald',
  },
];

const colorMap: Record<string, string> = {
  cyan: 'text-cyan border-cyan/30 shadow-[0_0_20px_rgba(0,212,255,0.12)]',
  violet: 'text-violet border-violet/30 shadow-[0_0_20px_rgba(167,139,250,0.12)]',
  amber: 'text-amber border-amber/30 shadow-[0_0_20px_rgba(251,191,36,0.12)]',
  emerald: 'text-emerald border-emerald/30 shadow-[0_0_20px_rgba(52,211,153,0.12)]',
};

const iconBgMap: Record<string, string> = {
  cyan: 'bg-cyan/10 text-cyan',
  violet: 'bg-violet/10 text-violet',
  amber: 'bg-amber/10 text-amber',
  emerald: 'bg-emerald/10 text-emerald',
};

const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.15 } } };
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as const } },
};

export function HowItWorksSection() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const lineHeight = useTransform(scrollYProgress, [0.1, 0.8], ['0%', '100%']);

  return (
    <section id="how-it-works" ref={ref} className="relative z-10 py-28 px-6 overflow-hidden">
      {/* Top separator */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

      {/* Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          variants={stagger}
          className="text-center mb-20"
        >
          <motion.p variants={fadeUp} className="text-xs font-mono text-cyan tracking-[0.2em] uppercase mb-5">
            The Pipeline
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-5xl font-heading font-bold mb-5 text-balance">
            From Raw Signal to{' '}
            <span className="text-gradient">Automated Action</span>
          </motion.h2>
          <motion.p variants={fadeUp} className="text-muted max-w-xl mx-auto text-base leading-relaxed">
            A fully automated loop — from sensor data capture to parts on the loading dock —
            with no manual intervention required.
          </motion.p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Vertical connecting line */}
          <div className="absolute left-8 top-8 bottom-8 w-px bg-border hidden md:block">
            <motion.div
              className="absolute top-0 left-0 w-full bg-gradient-to-b from-cyan via-violet to-emerald"
              style={{ height: lineHeight }}
            />
          </div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-60px' }}
            variants={stagger}
            className="flex flex-col gap-8"
          >
            {steps.map((step, i) => (
              <motion.div
                key={step.number}
                variants={fadeUp}
                className="relative flex flex-col md:flex-row gap-6 md:gap-10 items-start"
              >
                {/* Step number circle */}
                <div className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-2xl border bg-surface ${colorMap[step.color]} flex flex-col items-center justify-center`}>
                  <span className="text-[10px] font-mono opacity-60 leading-none">{step.number}</span>
                  <step.icon className="w-5 h-5 mt-0.5" />
                </div>

                {/* Content card */}
                <div className="flex-1 p-6 rounded-2xl border border-border bg-surface/60 hover:bg-surface transition-colors group">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <p className={`text-[11px] font-mono uppercase tracking-wider mb-1 ${colorMap[step.color].split(' ')[0]}`}>
                        {step.subtitle}
                      </p>
                      <h3 className="text-xl font-heading font-bold text-foreground">{step.title}</h3>
                    </div>
                  </div>
                  <p className="text-sm text-muted leading-relaxed mb-4">{step.desc}</p>
                  <div className="flex items-center gap-2 text-[10px] font-mono text-muted/60 border-t border-border pt-3">
                    <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${step.dotColor}`} />
                    {step.detail}
                  </div>
                </div>

                {/* Arrow between steps */}
                {i < steps.length - 1 && (
                  <motion.div
                    className="hidden md:flex absolute -bottom-5 left-8 -translate-x-1/2 z-20 w-6 h-6 rounded-full bg-surface border border-border items-center justify-center"
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.5 }}
                  >
                    <ArrowDown className="w-3 h-3 text-muted" />
                  </motion.div>
                )}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
