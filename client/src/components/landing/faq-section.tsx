'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const faqs = [
  {
    q: 'Yefai hangi makine türlerini destekliyor?',
    a: 'CNC tezgahları, frezeler, torna makineleri ve döner ekipmanlarda çalışır. Titreşim, sıcaklık, akustik emisyon ve görüntü sensörleri desteklenmektedir.',
  },
  {
    q: 'Entegrasyon ne kadar sürer?',
    a: 'Standart OPC-UA veya MQTT destekli makinelerde entegrasyon birkaç saat içinde tamamlanır. Özel protokoller için profesyonel destek sunulmaktadır.',
  },
  {
    q: 'Verilerim nerede saklanıyor?',
    a: 'Tüm veriler Supabase altyapısında, şifrelenmiş ve organizasyonunuza izole biçimde saklanır. GDPR uyumlu veri işleme politikaları uygulanır.',
  },
  {
    q: 'Kaç fabrika bağlanabilir?',
    a: 'Çoklu organizasyon mimarisi sayesinde sınırsız fabrika bağlantısı desteklenmektedir. Her fabrika izole bir namespace altında çalışır.',
  },
  {
    q: 'Demo hesabı nasıl alırım?',
    a: 'Sayfanın üst kısmındaki "Demo Başlat" butonuna tıklayın. Anında demo hesabına erişebilir, tüm özellikleri gerçek verilerle deneyimleyebilirsiniz.',
  },
];

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section
      id="faq"
      className="w-full px-6 py-[80px] border-t"
      style={{
        background: 'var(--color-paper-canvas)',
        borderColor: 'rgba(36,36,36,0.1)',
      }}
    >
      <div className="mx-auto" style={{ maxWidth: '800px' }}>
        {/* Header */}
        <p
          className="font-mono text-[12px] tracking-[0.05px] uppercase mb-4"
          style={{ color: 'var(--color-faint-text)' }}
        >
          SSS
        </p>
        <h2
          className="font-serif font-[400] mb-[40px] text-balance"
          style={{
            fontSize: '40px',
            lineHeight: 1.2,
            letterSpacing: '-0.02em',
            color: 'var(--color-ink)',
          }}
        >
          Sık sorulan sorular.
        </h2>

        {/* Accordion */}
        <div className="flex flex-col">
          {faqs.map((faq, i) => (
            <div
              key={i}
              className="border-b"
              style={{ borderColor: 'var(--color-pale-stone)' }}
            >
              <button
                className="w-full flex items-center justify-between gap-4 py-[24px] text-left"
                onClick={() => setOpen(open === i ? null : i)}
                aria-expanded={open === i}
              >
                <span
                  className="font-mono font-[400] text-[16px] tracking-[-0.02px]"
                  style={{ color: 'var(--color-ink)' }}
                >
                  {faq.q}
                </span>
                <span
                  className="font-mono text-[20px] shrink-0 transition-transform duration-200"
                  style={{
                    color: 'var(--color-pale-stone)',
                    transform: open === i ? 'rotate(45deg)' : 'rotate(0deg)',
                  }}
                >
                  +
                </span>
              </button>

              <AnimatePresence initial={false}>
                {open === i && (
                  <motion.div
                    key="answer"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden"
                  >
                    <p
                      className="font-sans text-[16px] leading-[1.35] tracking-[-0.02px] pb-[24px]"
                      style={{ color: 'var(--color-pale-stone)' }}
                    >
                      {faq.a}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
