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
          TAKIM_01 · AŞINMA: %38
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
          ANOMALİ · KRİTİK
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
          CANLI · 60 FPS
        </div>
        <div className="text-[9px] font-mono text-muted/60">YZ ÇIKARIM: 8ms</div>
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



            {/* Headline */}
            <motion.h1
              variants={fadeUp}
              custom={1}
              className="text-[clamp(2.8rem,6vw,5.5rem)] font-heading font-bold leading-[1.04] tracking-tight mb-6 text-balance"
            >
              <span className="text-foreground">Bozulmadan</span>
              <br />
              <span className="text-foreground">Önce</span>{' '}
              <span className="text-gradient">Bilin.</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeUp}
              custom={2}
              className="text-base sm:text-lg text-muted max-w-[520px] mb-10 leading-relaxed"
            >
              Yefai, bilgisayarlı görü, akustik sensörler ve çok modlu yapay zekayı birleştirerek takım aşınmasını gerçek zamanlı tespit eder — arızaları üretim hattınızı durdurmadan önce tahmin eder ve yedek parça tedarikini uçtan uca otomatikleştirir.
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
                <span>Ücretsiz Demoyu Başlat</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>


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
              <div className="text-[10px] text-muted font-mono uppercase tracking-wider mb-1.5">Aşınma Endeksi</div>
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
                <span className="text-[10px] font-mono text-rose uppercase tracking-wide">Kritik Uyarı</span>
              </div>
              <p className="text-[11px] text-foreground font-medium leading-tight">Uç B-4 · 2.3s içinde değiştirin</p>
              <p className="text-[10px] text-muted mt-0.5">Tedarik başlatıldı</p>
            </FloatingCard>

            {/* Floating card: Prediction */}
            <FloatingCard className="top-1/2 -translate-y-1/2 -right-8 min-w-[140px] hidden xl:block" delay={1.8}>
              <div className="text-[10px] text-muted font-mono uppercase tracking-wider mb-2">Sonraki Arıza</div>
              <div className="text-lg font-heading font-bold text-amber">~14.2s</div>
              <div className="text-[10px] text-muted mt-0.5">Tahmin Güveni: %94</div>
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
        <div className="text-[10px] font-mono text-muted/50 tracking-widest uppercase">Kaydır</div>
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
