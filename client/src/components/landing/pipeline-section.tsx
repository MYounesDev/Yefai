'use client';

import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09 } },
};

const steps = [
  {
    label: 'Sensör Verisi',
    desc: 'Titreşim, sıcaklık, ses ve görüntü verileri toplanır.',
    tag: 'Girdi',
  },
  {
    label: 'AI Analizi',
    desc: 'NovaVision ve anomali modelleri çok modlu veriyi işler.',
    tag: 'İşlem',
  },
  {
    label: 'Risk Puanı',
    desc: 'Stok, tedarik ve şiddet değerlendirmesi tek puanda birleşir.',
    tag: 'Değerlendirme',
  },
  {
    label: 'Uyarı & Aksiyon',
    desc: 'Telegram, e-posta veya otomatik iş emri ile ekip harekete geçer.',
    tag: 'Çıktı',
  },
];

export function PipelineSection() {
  return (
    <section
      className="w-full px-6 py-[80px] border-t"
      style={{
        background: 'var(--color-paper-canvas)',
        borderColor: 'rgba(36,36,36,0.1)',
      }}
    >
      <div className="mx-auto" style={{ maxWidth: '1432px' }}>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
        >
          {/* Section header */}
          <motion.p
            variants={fadeUp}
            custom={0}
            className="font-mono text-[12px] tracking-[0.05px] uppercase mb-4"
            style={{ color: 'var(--color-faint-text)' }}
          >
            Nasıl Çalışır
          </motion.p>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="font-serif font-[400] mb-[40px] text-balance"
            style={{
              fontSize: '40px',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
              color: 'var(--color-ink)',
              maxWidth: '520px',
            }}
          >
            Veriden karara dört adımda.
          </motion.h2>

          {/* Steps */}
          <motion.div
            variants={stagger}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-[16px]"
          >
            {steps.map((step, i) => (
              <motion.div
                key={step.label}
                variants={fadeUp}
                custom={i + 2}
                className="flex flex-col gap-[16px] p-[40px] rounded-[40px] border"
                style={{
                  borderColor: 'rgba(36,36,36,0.14)',
                  background: 'var(--color-paper-canvas)',
                }}
              >
                {/* Step number + tag */}
                <div className="flex items-center gap-3">
                  <span
                    className="font-mono text-[28px] font-[400] leading-[1.2]"
                    style={{ color: 'var(--color-ink)', letterSpacing: '-0.02em' }}
                  >
                    0{i + 1}
                  </span>
                  <span
                    className="font-mono text-[12px] tracking-[0.05px] uppercase px-3 py-1 rounded-[2000px] border"
                    style={{
                      color: 'var(--color-faint-text)',
                      borderColor: 'var(--color-faint-text)',
                    }}
                  >
                    {step.tag}
                  </span>
                </div>

                <h3
                  className="font-mono font-[500] text-[20px] tracking-[-0.02px]"
                  style={{ color: 'var(--color-ink)', lineHeight: 1.2 }}
                >
                  {step.label}
                </h3>

                <p
                  className="font-sans text-[16px] leading-[1.35] tracking-[-0.02px]"
                  style={{ color: 'var(--color-pale-stone)' }}
                >
                  {step.desc}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
