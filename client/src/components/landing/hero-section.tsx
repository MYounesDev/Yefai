'use client';

import { useRef, useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion';
import { ArrowRight, Play, Activity, ChevronRight } from 'lucide-react';
import dynamic from 'next/dynamic';

const HeroScene = dynamic(
  () => import('./hero-scene').then((m) => ({ default: m.HeroScene })),
  { ssr: false, loading: () => null }
);

const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.8, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

/* ── AI overlay bounding boxes floating on the video ── */
function AIOverlay() {
  return (
    <div className="absolute inset-0 pointer-events-none z-20">
      {/* Bounding box 1 */}
      <motion.div
        className="absolute border border-cyan/70 rounded"
        style={{ top: '22%', left: '18%', width: 110, height: 80 }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: [0, 1, 1, 0.7, 1], scale: 1 }}
        transition={{ delay: 1.2, duration: 0.6, repeat: Infinity, repeatDelay: 5 }}
      >
        <div className="absolute -top-5 left-0 text-[9px] font-mono text-cyan bg-background/80 px-1.5 py-0.5 rounded-sm whitespace-nowrap">
          TOOL_01 · WEAR: 38%
        </div>
        <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan" />
        <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan" />
        <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan" />
        <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan" />
      </motion.div>

      {/* Bounding box 2 — anomaly */}
      <motion.div
        className="absolute border border-rose/80 rounded"
        style={{ top: '45%', right: '22%', width: 90, height: 70 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0.8, 1] }}
        transition={{ delay: 2.0, duration: 0.5, repeat: Infinity, repeatDelay: 4.5 }}
      >
        <div className="absolute -top-5 left-0 text-[9px] font-mono text-rose bg-background/80 px-1.5 py-0.5 rounded-sm whitespace-nowrap">
          ANOMALY · CRITICAL
        </div>
        <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-rose" />
        <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-rose" />
        <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-rose" />
        <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-rose" />
      </motion.div>

      {/* Scan line */}
      <motion.div
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan/40 to-transparent"
        style={{ top: '60%' }}
        animate={{ top: ['10%', '90%'] }}
        transition={{ duration: 3.5, repeat: Infinity, repeatType: 'reverse', ease: 'linear' }}
      />

      {/* Corner HUD elements */}
      <div className="absolute top-3 right-3 flex flex-col gap-1">
        <div className="flex items-center gap-1.5 text-[9px] font-mono text-cyan/80">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse-glow-cyan" />
          LIVE · 60 FPS
        </div>
        <div className="text-[9px] font-mono text-muted/60">AI INFERENCE: 8ms</div>
      </div>
      <div className="absolute bottom-3 left-3 text-[9px] font-mono text-muted/60">
        NovaVision v2.4 · YOLO-NAS-L
      </div>
    </div>
  );
}

/* ── Floating dashboard cards around the video ── */
function FloatingCard({
  className,
  delay,
  children,
}: {
  className?: string;
  delay: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      className={`absolute z-30 glass-card border border-border-strong px-3 py-2.5 rounded-xl shadow-elevated ${className}`}
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      style={{ backdropFilter: 'blur(20px)' }}
    >
      {children}
    </motion.div>
  );
}

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 40, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 40, damping: 20 });

  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ['start start', 'end start'] });
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '30%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);

  const videoX = useTransform(springX, [-200, 200], [-8, 8]);
  const videoY = useTransform(springY, [-200, 200], [-6, 6]);
  const videoRotateY = useTransform(springX, [-200, 200], [3, -3]);
  const videoRotateX = useTransform(springY, [-200, 200], [-2, 2]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      mouseX.set(e.clientX - cx);
      mouseY.set(e.clientY - cy);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <motion.section
      ref={sectionRef}
      style={{ opacity: heroOpacity }}
      className="relative w-full min-h-screen flex items-center overflow-hidden pt-20"
    >
      {/* 3D WebGL background */}
      <HeroScene />

      {/* Background noise + grid */}
      <div className="absolute inset-0 bg-grid opacity-40 pointer-events-none z-0" />

      {/* Main radial glows */}
      <motion.div
        style={{ x: useTransform(springX, [-200, 200], ['-5%', '5%']) }}
        className="absolute top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-cyan/10 blur-[140px] rounded-full pointer-events-none z-0"
      />
      <motion.div
        style={{ x: useTransform(springX, [-200, 200], ['5%', '-5%']) }}
        className="absolute top-1/3 right-1/4 translate-x-1/4 -translate-y-1/2 w-[600px] h-[600px] bg-violet/10 blur-[120px] rounded-full pointer-events-none z-0"
      />

      {/* Content layout */}
      <motion.div style={{ y: heroY }} className="relative z-10 w-full max-w-[1400px] mx-auto px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">

          {/* ── Left: Text ── */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="flex flex-col items-center lg:items-start text-center lg:text-left"
          >
            {/* Badge */}
            <motion.div
              variants={fadeUp}
              custom={0}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan/8 border border-cyan/20 text-cyan text-xs font-medium mb-8 backdrop-blur-sm"
            >
              <Activity className="w-3.5 h-3.5 animate-pulse" />
              <span className="font-mono tracking-wide">Industry 4.0 · AI Predictive Maintenance</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={fadeUp}
              custom={1}
              className="text-[clamp(2.8rem,6vw,5.5rem)] font-heading font-bold leading-[1.04] tracking-tight mb-6 text-balance"
            >
              <span className="text-foreground">Know Before</span>
              <br />
              <span className="text-foreground">It</span>{' '}
              <span className="text-gradient">Breaks.</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeUp}
              custom={2}
              className="text-base sm:text-lg text-muted max-w-[520px] mb-10 leading-relaxed"
            >
              Yefai fuses computer vision, acoustic sensors, and multimodal AI to detect
              tool wear in real time — forecasting failures before they stop your line and
              automating spare parts procurement end-to-end.
            </motion.p>

            {/* CTAs */}
            <motion.div
              variants={fadeUp}
              custom={3}
              className="flex flex-wrap items-center justify-center lg:justify-start gap-4 mb-12"
            >
              <Link
                href="/login"
                className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-sm font-semibold bg-cyan text-background hover:brightness-110 transition-all active:scale-95 shadow-[0_0_32px_rgba(0,212,255,0.3)]"
              >
                <span>Start Free Demo</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-sm font-medium border border-border-strong hover:border-cyan/30 hover:bg-cyan/5 text-foreground transition-all active:scale-95">
                <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-cyan/20 transition-colors">
                  <Play className="w-3 h-3 fill-current ml-0.5" />
                </div>
                Watch Demo
              </button>
            </motion.div>

            {/* Micro-stats */}
            <motion.div
              variants={fadeUp}
              custom={4}
              className="flex items-center gap-6 text-sm text-muted"
            >
              {[['99.7%', 'Detection Accuracy'], ['<50ms', 'Response Time'], ['24/7', 'Live Monitoring']].map(([val, lbl]) => (
                <div key={lbl} className="flex flex-col items-center lg:items-start gap-0.5">
                  <span className="text-lg font-heading font-bold text-foreground">{val}</span>
                  <span className="text-[11px] text-muted/70 tracking-wide">{lbl}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* ── Right: Video card with parallax ── */}
          <motion.div
            className="relative w-full"
            style={{
              x: videoX,
              y: videoY,
              rotateY: videoRotateY,
              rotateX: videoRotateX,
              transformStyle: 'preserve-3d',
              perspective: 1000,
            }}
            initial={{ opacity: 0, scale: 0.92, x: 40 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 1.4, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Glow halo behind the card */}
            <div className="absolute -inset-4 bg-cyan/10 blur-[60px] rounded-[3rem] pointer-events-none" />

            {/* Main video frame */}
            <div className="relative rounded-[1.75rem] overflow-hidden border border-white/10 shadow-[0_0_80px_rgba(0,212,255,0.18),0_40px_80px_rgba(0,0,0,0.6)] ring-1 ring-white/5">
              {/* Top bar — mock browser chrome */}
              <div className="flex items-center gap-1.5 px-4 py-3 bg-surface-2/90 border-b border-border backdrop-blur-md">
                <div className="w-2.5 h-2.5 rounded-full bg-rose/70" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber/70" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald/70" />
                <div className="flex-1 mx-4 flex items-center justify-center">
                  <div className="px-4 py-1 rounded-md bg-background/60 border border-border text-[10px] font-mono text-muted/70 tracking-wide">
                    yefai.io/dashboard/live-view
                  </div>
                </div>
              </div>

              {/* Video */}
              <div className="relative">
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  className="w-full h-auto aspect-[4/3] object-cover"
                >
                  <source src="https://files.catbox.moe/p5wnuc.mp4" type="video/mp4" />
                </video>
                <AIOverlay />

                {/* Bottom gradient overlay */}
                <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-background/70 to-transparent pointer-events-none z-20" />
              </div>
            </div>

            {/* Floating card: Wear Score */}
            <FloatingCard className="-top-4 -left-6 min-w-[150px]" delay={1.2}>
              <div className="text-[10px] text-muted font-mono uppercase tracking-wider mb-1.5">Wear Index</div>
              <div className="flex items-end gap-1.5 mb-2">
                <span className="text-2xl font-heading font-bold text-cyan">38</span>
                <span className="text-xs text-muted mb-0.5">/ 100</span>
              </div>
              <div className="w-full h-1.5 bg-surface-3 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-emerald to-cyan rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: '38%' }}
                  transition={{ delay: 1.8, duration: 1, ease: 'easeOut' }}
                />
              </div>
            </FloatingCard>

            {/* Floating card: Alert */}
            <FloatingCard className="-bottom-4 -right-6 min-w-[160px]" delay={1.5}>
              <div className="flex items-center gap-2 mb-1.5">
                <div className="w-2 h-2 rounded-full bg-rose animate-pulse-glow" />
                <span className="text-[10px] font-mono text-rose uppercase tracking-wide">Critical Alert</span>
              </div>
              <p className="text-[11px] text-foreground font-medium leading-tight">Insert B-4 · Replace in 2.3h</p>
              <p className="text-[10px] text-muted mt-0.5">Procurement triggered</p>
            </FloatingCard>

            {/* Floating card: Prediction */}
            <FloatingCard className="top-1/2 -translate-y-1/2 -right-8 min-w-[140px] hidden xl:block" delay={1.8}>
              <div className="text-[10px] text-muted font-mono uppercase tracking-wider mb-2">Next Failure</div>
              <div className="text-lg font-heading font-bold text-amber">~14.2h</div>
              <div className="text-[10px] text-muted mt-0.5">ETA Confidence: 94%</div>
            </FloatingCard>
          </motion.div>
        </div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2, duration: 0.6 }}
      >
        <div className="text-[10px] font-mono text-muted/50 tracking-widest uppercase">Scroll</div>
        <div className="w-px h-8 bg-gradient-to-b from-muted/30 to-transparent" />
        <motion.div
          className="w-1 h-1 rounded-full bg-cyan"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        />
      </motion.div>
    </motion.section>
  );
}
