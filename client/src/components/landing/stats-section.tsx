'use client';

import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const stats = [
  { value: '99.7%', label: 'Anomali Tespit Doğruluğu', color: 'text-cyan' },
  { value: '<50ms', label: 'Gerçek Zamanlı Çıkarım Gecikmesi', color: 'text-violet' },
  { value: '8+', label: 'Farklı Sensör Modeli Birleşimi', color: 'text-amber' },
  { value: '40%', label: 'Duruş Süresinde Azalma', color: 'text-emerald' },
];

const logos = [
  'BOSCH', 'SIEMENS', 'ABB', 'FANUC', 'HAAS', 'DMG MORI',
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
  }),
};
const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.07 } } };

export function StatsSection() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const y = useTransform(scrollYProgress, [0, 1], [40, -40]);

  return (
    <section ref={ref} className="relative z-10 overflow-hidden py-20">
      {/* Separator line */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

      {/* Background */}
      <div className="absolute inset-0 bg-surface/30 backdrop-blur-sm" />

      <div className="relative max-w-6xl mx-auto px-6">
        {/* Stats */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16"
        >
          {stats.map((s, i) => (
            <motion.div key={s.label} variants={fadeUp} custom={i} className="text-center">
              <div className={`text-4xl sm:text-5xl font-heading font-bold mb-2 ${s.color}`}>{s.value}</div>
              <div className="text-xs text-muted tracking-wide leading-relaxed max-w-[160px] mx-auto">{s.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Social proof */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="text-center"
        >
          <motion.p variants={fadeUp} custom={0} className="text-xs text-muted/60 tracking-[0.2em] uppercase font-mono mb-6">
            Dünya çapındaki üretim liderleri tarafından güveniliyor
          </motion.p>
          <motion.div variants={fadeUp} custom={1} className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
            {logos.map((logo) => (
              <div
                key={logo}
                className="text-muted/30 font-heading font-bold text-sm tracking-[0.15em] hover:text-muted/60 transition-colors cursor-default select-none"
              >
                {logo}
              </div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
