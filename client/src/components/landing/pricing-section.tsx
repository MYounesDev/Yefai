'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Check, Zap } from 'lucide-react';

const plans = [
  {
    name: 'Başlangıç',
    price: 'Özel',
    period: 'tesis başına / ay',
    tagline: 'Pilot programlar ve tek hatlı kurulumlar için',
    features: [
      'En fazla 5 makine izleme',
      'NovaVision yapay zeka çıkarımı',
      'Gerçek zamanlı anomali uyarıları',
      'Telegram + e-posta bildirimleri',
      'Temel aşınma trend grafikleri',
      'Topluluk desteği',
    ],
    cta: 'Pilotu Başlat',
    highlight: false,
  },
  {
    name: 'Büyüme',
    price: 'Özel',
    period: 'tesis başına / ay',
    tagline: 'Kestirimci bakımı ölçeklendiren çok hatlı fabrikalar için',
    features: [
      'En fazla 50 makine izleme',
      'Tam çok modlu sensör füzyonu',
      'Kestirimci arıza tahminleme',
      'Otomatik tedarik + Sipariş (PO) oluşturma',
      'RAG sohbet robotu analitiği',
      'Öncelikli destek + SLA',
      'Çoklu organizasyon yönetimi',
      'ERP / CMMS entegrasyonları',
    ],
    cta: 'Demo Talep Et',
    highlight: true,
    badge: 'En Popüler',
  },
  {
    name: 'Kurumsal',
    price: 'Özel',
    period: 'görüşülerek belirlenir',
    tagline: 'Karmaşık ortamlara sahip küresel üreticiler için',
    features: [
      'Sınırsız makine izleme',
      'Size özel uç altyapı',
      'Özel model ince ayarı',
      'White-label & Kurumsal Kimlik (SSO)',
      'Denetim kayıtları ve uyumluluk',
      'Özel CSM + entegrasyon desteği',
      '%99.9 çalışma süresi (SLA)',
      'Yerinde (On-prem) kurulum seçeneği',
    ],
    cta: 'Satış Ekibiyle Görüş',
    highlight: false,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.7, ease: [0.22, 1, 0.36, 1] as const },
  }),
};
const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.1 } } };

export function PricingSection() {
  return (
    <section id="pricing" className="relative z-10 py-28 px-6 overflow-hidden">
      {/* Separator */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-violet/6 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          variants={stagger}
          className="text-center mb-16"
        >
          <motion.div variants={fadeUp} custom={0} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber/8 border border-amber/20 text-amber text-xs font-mono tracking-wider uppercase mb-5">
            <Zap className="w-3.5 h-3.5" />
            Fiyatlandırma
          </motion.div>
          <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-5xl font-heading font-bold mb-5 text-balance">
            Şeffaf,{' '}
            <span className="text-gradient">Sonuç Odaklı</span>
            {' '}Fiyatlandırma
          </motion.h2>
          <motion.p variants={fadeUp} custom={2} className="text-muted max-w-xl mx-auto text-base leading-relaxed">
            Tüm planlar fabrika büyüklüğünüze göre ölçeklendirilir. Makine sayınıza ve sensör karışımnııza göre size özel detaylı bir teklif için bizimle iletişime geçin.
          </motion.p>
        </motion.div>

        {/* Plans grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              variants={fadeUp}
              custom={i}
              className={`relative flex flex-col rounded-2xl border p-8 transition-all duration-300 ${
                plan.highlight
                  ? 'border-cyan/40 bg-surface shadow-[0_0_48px_rgba(0,212,255,0.12)] scale-[1.02]'
                  : 'border-border bg-surface hover:border-border-strong'
              }`}
            >
              {/* Popular badge */}
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-cyan text-background text-[11px] font-bold tracking-wide shadow-[0_0_20px_rgba(0,212,255,0.4)]">
                  {plan.badge}
                </div>
              )}

              {/* Plan header */}
              <div className="mb-6">
                <p className={`text-[11px] font-mono tracking-widest uppercase mb-2 ${plan.highlight ? 'text-cyan' : 'text-muted/60'}`}>
                  {plan.name}
                </p>
                <div className="flex items-baseline gap-2 mb-3">
                  <span className="text-4xl font-heading font-bold text-foreground">{plan.price}</span>
                  <span className="text-xs text-muted">{plan.period}</span>
                </div>
                <p className="text-sm text-muted leading-relaxed">{plan.tagline}</p>
              </div>

              {/* Divider */}
              <div className={`h-px mb-6 ${plan.highlight ? 'bg-cyan/20' : 'bg-border'}`} />

              {/* Feature list */}
              <ul className="space-y-3 flex-1 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-3">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${plan.highlight ? 'bg-cyan/15 text-cyan' : 'bg-surface-2 text-muted'}`}>
                      <Check className="w-3 h-3" />
                    </div>
                    <span className="text-sm text-muted">{f}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <Link
                href="/login"
                className={`block text-center py-3.5 rounded-xl text-sm font-semibold transition-all active:scale-95 ${
                  plan.highlight
                    ? 'bg-cyan text-background hover:brightness-110 shadow-[0_0_24px_rgba(0,212,255,0.3)]'
                    : 'border border-border-strong hover:bg-surface-2 text-foreground'
                }`}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom note */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="text-center text-xs text-muted/50 font-mono mt-10"
        >
          Tüm planlar 30 günlük deneme süresi içerir. Taahhüt yok. KVKK/GDPR uyumlu.
        </motion.p>
      </div>
    </section>
  );
}
