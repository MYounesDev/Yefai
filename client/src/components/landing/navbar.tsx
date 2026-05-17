'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export function LandingNavbar() {
  return (
    <>
      {/* Notification bar */}
      <div
        className="w-full flex items-center justify-center gap-4 px-6 py-3"
        style={{ background: 'var(--color-ink)', color: 'var(--color-paper-canvas)' }}
      >
        <p
          className="font-mono text-[14px] leading-[1.3] tracking-[-0.014px]"
          style={{ color: 'var(--color-paper-canvas)' }}
        >
          Yefai v1.0 — Kestirimci Bakım Platformu artık kullanılabilir
        </p>
        <Link
          href="/login"
          className="font-mono text-[14px] px-4 py-1 rounded-[2000px] border transition-opacity hover:opacity-80"
          style={{
            color: 'var(--color-paper-canvas)',
            borderColor: 'var(--color-paper-canvas)',
          }}
        >
          Demo Başlat →
        </Link>
      </div>

      {/* Nav bar */}
      <motion.nav
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="sticky top-0 z-50 w-full border-b px-8 py-4"
        style={{
          background: 'var(--color-paper-canvas)',
          borderColor: 'rgba(36,36,36,0.12)',
        }}
      >
        <div
          className="mx-auto flex items-center justify-between"
          style={{ maxWidth: '1432px' }}
        >
          {/* Brand */}
          <span
            className="font-mono font-[400] text-[20px] tracking-[-0.02px]"
            style={{ color: 'var(--color-ink)' }}
          >
            Yefai
          </span>

          {/* Nav links + CTA */}
          <div className="flex items-center gap-2">
            <Link
              href="#features"
              className="font-mono text-[16px] tracking-[-0.02px] px-[10px] py-2 hover:underline transition-all"
              style={{ color: 'var(--color-off-black)' }}
            >
              Platform
            </Link>
            <Link
              href="#faq"
              className="font-mono text-[16px] tracking-[-0.02px] px-[10px] py-2 hover:underline transition-all"
              style={{ color: 'var(--color-off-black)' }}
            >
              SSS
            </Link>
            <Link
              href="/login"
              className="font-mono text-[16px] tracking-[-0.02px] ml-4 px-[16px] py-[16px] rounded-[100px] border transition-colors hover:bg-off-black hover:text-paper-canvas"
              style={{
                border: '1px solid var(--color-off-black)',
                color: 'var(--color-off-black)',
                paddingTop: '10px',
                paddingBottom: '10px',
              }}
            >
              Demo Al →
            </Link>
          </div>
        </div>
      </motion.nav>
    </>
  );
}
