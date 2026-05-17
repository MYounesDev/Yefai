'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export function CtaFooter() {
  return (
    <>
      {/* CTA Section */}
      <section
        className="w-full px-6 py-[80px] border-t"
        style={{
          background: 'var(--color-atmosphere-wash)',
          borderColor: 'rgba(36,36,36,0.1)',
        }}
      >
        <div
          className="mx-auto flex flex-col items-center text-center gap-8"
          style={{ maxWidth: '700px' }}
        >
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col items-center gap-6"
          >
            <h2
              className="font-serif font-[400] text-balance"
              style={{
                fontSize: 'clamp(32px, 5vw, 40px)',
                lineHeight: 1.2,
                letterSpacing: '-0.02em',
                color: 'var(--color-ink)',
              }}
            >
              Üretime hazır mısınız?
            </h2>
            <p
              className="font-sans text-[16px] leading-[1.35] tracking-[-0.02px] max-w-md"
              style={{ color: 'var(--color-pale-stone)' }}
            >
              Yefai ile kestirimci bakım süreçlerinizi otomatikleştirin.
              Hemen demo hesabıyla platformu keşfetmeye başlayın.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/login"
                className="font-mono text-[16px] tracking-[-0.02px] px-[24px] py-[16px] rounded-[100px] transition-all hover:opacity-90 active:scale-95"
                style={{
                  background: 'var(--color-off-black)',
                  color: 'var(--color-paper-canvas)',
                }}
              >
                Ücretsiz Demo Başlat
              </Link>
              <Link
                href="#features"
                className="font-mono text-[16px] tracking-[-0.02px] px-[24px] py-[16px] rounded-[100px] border transition-all hover:bg-[rgba(36,36,36,0.06)]"
                style={{
                  border: '1px solid var(--color-off-black)',
                  color: 'var(--color-off-black)',
                }}
              >
                Özellikleri Gör
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="w-full px-8 py-8 border-t"
        style={{
          background: 'var(--color-paper-canvas)',
          borderColor: 'rgba(36,36,36,0.1)',
        }}
      >
        <div
          className="mx-auto flex flex-col sm:flex-row items-center justify-between gap-4"
          style={{ maxWidth: '1432px' }}
        >
          <span
            className="font-mono font-[400] text-[16px] tracking-[-0.02px]"
            style={{ color: 'var(--color-ink)' }}
          >
            Yefai
          </span>
          <div className="flex items-center gap-8">
            <Link
              href="/login"
              className="font-mono text-[14px] tracking-[-0.014px] hover:underline"
              style={{ color: 'var(--color-faint-text)' }}
            >
              Giriş Yap
            </Link>
            <Link
              href="#features"
              className="font-mono text-[14px] tracking-[-0.014px] hover:underline"
              style={{ color: 'var(--color-faint-text)' }}
            >
              Platform
            </Link>
            <Link
              href="#faq"
              className="font-mono text-[14px] tracking-[-0.014px] hover:underline"
              style={{ color: 'var(--color-faint-text)' }}
            >
              SSS
            </Link>
          </div>
          <p
            className="font-mono text-[12px] tracking-[0.05px]"
            style={{ color: 'var(--color-faint-text)' }}
          >
            © 2026 Yefai. Tüm hakları saklıdır.
          </p>
        </div>
      </footer>
    </>
  );
}
