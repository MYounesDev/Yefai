'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import {
  Cpu, Shield, TrendingUp, Zap, Eye, BarChart3,
  ArrowRight, ChevronRight, Activity, Layers, Globe,
} from 'lucide-react';

const HeroScene = dynamic(
  () => import('@/components/landing/hero-scene').then((m) => m.HeroScene),
  { ssr: false }
);

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
};

const features = [
  {
    icon: Eye,
    title: 'NovaVision AI',
    desc: 'Kamera ve sensör verilerini birleştirerek aşınma anomalilerini sıfır atışlı tespit eder.',
    gradient: 'from-cyan to-blue-500',
  },
  {
    icon: TrendingUp,
    title: 'Kestirimci Tahmin',
    desc: 'Makine aşınma hızını modelleyerek kritik eşiğe ne zaman ulaşılacağını tahmin eder.',
    gradient: 'from-violet to-purple-500',
  },
  {
    icon: Shield,
    title: 'Kriz Skoru',
    desc: 'Yedek parça stok durumu, tedarik süresi ve anomali şiddetini birleştiren akıllı risk puanı.',
    gradient: 'from-amber to-orange-500',
  },
  {
    icon: Zap,
    title: 'Gerçek Zamanlı Uyarılar',
    desc: 'Telegram, e-posta ve SMS üzerinden anlık bildirimlerle sıfır gecikme müdahale.',
    gradient: 'from-rose to-pink-500',
  },
  {
    icon: BarChart3,
    title: 'RAG Chatbot',
    desc: 'Doğal dil ile sorgulama yapın — AI asistan tüm fabrika verilerinizi analiz eder.',
    gradient: 'from-emerald to-teal-500',
  },
  {
    icon: Layers,
    title: 'Çoklu Organizasyon',
    desc: 'B2B SaaS mimarisi ile birden fazla fabrika ve ekibi tek platformda yönetin.',
    gradient: 'from-blue-400 to-cyan',
  },
];

const stats = [
  { value: '99.7%', label: 'Anomali Doğruluğu' },
  { value: '<50ms', label: 'Tepki Süresi' },
  { value: '8+', label: 'Sensör Türü' },
  { value: '24/7', label: 'Gerçek Zamanlı İzleme' },
];

export default function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 0.96]);

  return (
    <div ref={containerRef} className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* ═══════════ NAVBAR ═══════════ */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center shadow-lg shadow-cyan/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <span className="font-heading font-bold text-lg text-gradient tracking-tight">Yefai</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-xl text-sm font-medium text-foreground hover:text-cyan transition-colors"
            >
              Giriş Yap
            </Link>
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-cyan text-background hover:brightness-110 transition-all shadow-lg shadow-cyan/20 active:scale-95"
            >
              Demo Başlat
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* ═══════════ HERO ═══════════ */}
      <motion.section
        style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative min-h-screen flex items-center justify-center px-6"
      >
        <HeroScene />

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-b from-background/40 via-transparent to-background z-[1]" />
        <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-background to-transparent z-[1]" />

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
          >
            {/* Tagline chip */}
            <motion.div
              variants={fadeUp}
              custom={0}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan/8 border border-cyan/15 text-cyan text-xs font-medium mb-8"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Endüstriyel AI Platformu</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={fadeUp}
              custom={1}
              className="text-4xl sm:text-5xl md:text-7xl font-heading font-bold leading-[1.08] tracking-tight mb-6"
            >
              <span className="text-foreground">Kırılmadan</span>
              <br />
              <span className="text-gradient">Önce Bilin.</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeUp}
              custom={2}
              className="text-base sm:text-lg text-muted max-w-2xl mx-auto mb-10 leading-relaxed"
            >
              Çok modlu yapay zeka ile takım tezgahı aşınmasını gerçek zamanlı izleyin.
              Sensör verileri, kamera görüntüleri ve akustik sinyallerden beslenen
              kestirimci bakım platformu.
            </motion.p>

            {/* CTAs */}
            <motion.div
              variants={fadeUp}
              custom={3}
              className="flex flex-wrap items-center justify-center gap-4"
            >
              <Link
                href="/login"
                className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-cyan to-violet text-white hover:shadow-2xl hover:shadow-cyan/20 transition-all active:scale-95"
              >
                <span>Platformu Keşfet</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-sm font-medium border border-border hover:border-border-strong hover:bg-surface-2 text-foreground transition-all active:scale-95"
              >
                Daha Fazla Bilgi
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* ═══════════ STATS BAR ═══════════ */}
      <section className="relative z-10 py-16 border-y border-border bg-surface/50 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={stagger}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {stats.map((stat, i) => (
              <motion.div key={stat.label} variants={fadeUp} custom={i} className="text-center">
                <p className="text-3xl sm:text-4xl font-heading font-bold text-gradient mb-2">{stat.value}</p>
                <p className="text-xs text-muted tracking-wide uppercase">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ═══════════ FEATURES ═══════════ */}
      <section id="features" className="relative z-10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={stagger}
            className="text-center mb-16"
          >
            <motion.p variants={fadeUp} custom={0} className="text-xs font-medium text-cyan tracking-widest uppercase mb-4">
              Özellikler
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-heading font-bold mb-4">
              Endüstri 4.0 İçin <span className="text-gradient">Tasarlandı</span>
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="text-muted max-w-xl mx-auto">
              Sensör, görüntü ve akustik verilerinizi tek bir platformda birleştirerek
              fabrika genelinde tam görünürlük sağlayın.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-60px' }}
            variants={stagger}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i}
                className="group relative p-6 rounded-2xl bg-surface border border-border hover:border-border-strong transition-all duration-300 hover:shadow-elevated"
              >
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-4 shadow-lg group-hover:scale-105 transition-transform`}>
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-base font-heading font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ═══════════ CTA ═══════════ */}
      <section className="relative z-10 py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
          >
            <motion.h2 variants={fadeUp} custom={0} className="text-3xl sm:text-4xl font-heading font-bold mb-4">
              Üretime <span className="text-gradient">Hazır mısınız?</span>
            </motion.h2>
            <motion.p variants={fadeUp} custom={1} className="text-muted max-w-lg mx-auto mb-8">
              Yefai ile kestirimci bakım süreçlerinizi otomatikleştirin.
              Hemen demo hesabıyla platformu keşfetmeye başlayın.
            </motion.p>
            <motion.div variants={fadeUp} custom={2}>
              <Link
                href="/login"
                className="group inline-flex items-center gap-2.5 px-8 py-4 rounded-xl text-base font-semibold bg-gradient-to-r from-cyan to-violet text-white hover:shadow-2xl hover:shadow-cyan/20 transition-all active:scale-95"
              >
                <span>Ücretsiz Demo Başlat</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ═══════════ FOOTER ═══════════ */}
      <footer className="relative z-10 border-t border-border py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan to-violet flex items-center justify-center">
              <Cpu className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-heading font-bold text-sm text-gradient">Yefai</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-muted">
            <Globe className="w-3.5 h-3.5" />
            <span>© 2026 Yefai. Tüm hakları saklıdır.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
