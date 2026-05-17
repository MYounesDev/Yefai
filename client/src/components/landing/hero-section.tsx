'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09 } },
};

export function HeroSection() {
  return (
    <section
      className="w-full flex flex-col items-center justify-center text-center px-6 py-[120px]"
      style={{ background: 'var(--color-paper-canvas)' }}
    >
      <motion.div
        initial="hidden"
        animate="visible"
        variants={stagger}
        className="flex flex-col items-center gap-8"
        style={{ maxWidth: '860px' }}
      >
        {/* Tag */}
        <motion.div variants={fadeUp} custom={0}>
          <span
            className="font-mono text-[12px] tracking-[0.05px] uppercase px-4 py-2 rounded-[2000px] border"
            style={{
              color: 'var(--color-ink)',
              borderColor: 'var(--color-ink)',
            }}
          >
            Endüstriyel AI Platformu
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          variants={fadeUp}
          custom={1}
          className="font-serif font-[400] text-balance"
          style={{
            fontSize: 'clamp(40px, 8vw, 80px)',
            lineHeight: 1.2,
            letterSpacing: '-0.02em',
            color: 'var(--color-ink)',
          }}
        >
          Kırılmadan Önce Bilin.
        </motion.h1>

        {/* Sub-headline */}
        <motion.p
          variants={fadeUp}
          custom={2}
          className="font-sans text-[16px] leading-[1.35] tracking-[-0.02px] text-pretty max-w-xl"
          style={{ color: 'var(--color-pale-stone)' }}
        >
          Çok modlu yapay zeka ile takım tezgahı aşınmasını gerçek zamanlı izleyin.
          Sensör verileri, kamera görüntüleri ve akustik sinyallerden beslenen kestirimci bakım platformu.
        </motion.p>

        {/* CTAs */}
        <motion.div
          variants={fadeUp}
          custom={3}
          className="flex flex-wrap items-center justify-center gap-4"
        >
          <Link
            href="/login"
            className="font-mono text-[16px] tracking-[-0.02px] px-[24px] py-[16px] rounded-[100px] transition-all hover:opacity-90 active:scale-95"
            style={{
              background: 'var(--color-off-black)',
              color: 'var(--color-paper-canvas)',
            }}
          >
            Platformu Keşfet
          </Link>
          <Link
            href="#features"
            className="font-mono text-[16px] tracking-[-0.02px] px-[24px] py-[16px] rounded-[100px] border transition-all hover:bg-[#f0ede9]"
            style={{
              border: '1px solid var(--color-off-black)',
              color: 'var(--color-off-black)',
            }}
          >
            Daha Fazla Bilgi
          </Link>
        </motion.div>

        {/* Stats strip */}
        <motion.div
          variants={fadeUp}
          custom={4}
          className="mt-8 flex flex-wrap items-center justify-center gap-x-12 gap-y-4"
        >
          {[
            { value: '99.7%', label: 'Anomali Doğruluğu' },
            { value: '<50ms', label: 'Tepki Süresi' },
            { value: '8+', label: 'Sensör Türü' },
            { value: '24/7', label: 'Gerçek Zamanlı İzleme' },
          ].map((s) => (
            <div key={s.label} className="flex flex-col items-center gap-1">
              <span
                className="font-serif text-[28px] font-[400]"
                style={{ letterSpacing: '-0.02em', color: 'var(--color-ink)' }}
              >
                {s.value}
              </span>
              <span
                className="font-mono text-[12px] tracking-[0.05px] uppercase"
                style={{ color: 'var(--color-faint-text)' }}
              >
                {s.label}
              </span>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
