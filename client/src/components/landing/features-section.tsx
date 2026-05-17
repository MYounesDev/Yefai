'use client';

import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07 } },
};

const features = [
  {
    tag: 'Görüntü AI',
    title: 'NovaVision AI',
    desc: 'Kamera ve sensör verilerini birleştirerek aşınma anomalilerini sıfır-shot tespiti ile yakalar. Üretim hattında anlık görsel denetim.',
  },
  {
    tag: 'Tahmin',
    title: 'Kestirimci Analiz',
    desc: 'Makine aşınma hızını modelleyerek kritik eşiğe ne zaman ulaşılacağını tahmin eder. Planlı bakım ile beklenmedik duruş sıfıra iner.',
  },
  {
    tag: 'Risk',
    title: 'Kriz Skoru',
    desc: 'Yedek parça stok durumu, tedarik süresi ve anomali şiddetini birleştiren akıllı risk puanı. Önceliklendirme otomatik yapılır.',
  },
  {
    tag: 'Bildirim',
    title: 'Gerçek Zamanlı Uyarılar',
    desc: 'Telegram, e-posta ve SMS üzerinden anlık bildirimlerle sıfır gecikme müdahale. Kritik olaylar asla kaçırılmaz.',
  },
  {
    tag: 'Chatbot',
    title: 'RAG Asistan',
    desc: 'Doğal dil ile sorgulama yapın — AI asistan tüm fabrika verilerinizi analiz eder. Raporlar, analizler, kararlar tek yerden.',
  },
  {
    tag: 'Multi-tenant',
    title: 'Çoklu Organizasyon',
    desc: 'B2B SaaS mimarisi ile birden fazla fabrika ve ekibi tek platformda yönetin. Rol tabanlı erişim, izolasyon, ölçeklenebilirlik.',
  },
];

export function FeaturesSection() {
  return (
    <section
      id="features"
      className="w-full px-6 py-[80px]"
      style={{ background: 'var(--color-paper-canvas)' }}
    >
      <div className="mx-auto" style={{ maxWidth: '1432px' }}>
        {/* Section header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
          className="mb-[40px]"
        >
          <motion.p
            variants={fadeUp}
            custom={0}
            className="font-mono text-[12px] tracking-[0.05px] uppercase mb-4"
            style={{ color: 'var(--color-faint-text)' }}
          >
            Platform
          </motion.p>
          <motion.h2
            variants={fadeUp}
            custom={1}
            className="font-serif font-[400] text-balance"
            style={{
              fontSize: '40px',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
              color: 'var(--color-ink)',
              maxWidth: '560px',
            }}
          >
            Endüstri 4.0 için tasarlandı.
          </motion.h2>
        </motion.div>

        {/* Feature cards grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-40px' }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[16px]"
        >
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              variants={fadeUp}
              custom={i}
              className="flex flex-col gap-4 p-[40px] rounded-[40px]"
              style={{ background: 'var(--color-atmosphere-wash)' }}
            >
              {/* Tag pill */}
              <span
                className="font-mono text-[12px] tracking-[0.05px] uppercase self-start px-3 py-1 rounded-[2000px] border"
                style={{
                  color: 'var(--color-ink)',
                  borderColor: 'var(--color-ink)',
                }}
              >
                {f.tag}
              </span>

              {/* Title */}
              <h3
                className="font-mono font-[500] text-[20px] tracking-[-0.02px]"
                style={{ color: 'var(--color-ink)', lineHeight: 1.2 }}
              >
                {f.title}
              </h3>

              {/* Description */}
              <p
                className="font-sans text-[16px] leading-[1.35] tracking-[-0.02px]"
                style={{ color: 'var(--color-pale-stone)' }}
              >
                {f.desc}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
