'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Cpu, Menu, X } from 'lucide-react';

const navLinks = [
  { label: 'Platform', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Docs', href: '#' },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { scrollY } = useScroll();
  const navBg = useTransform(scrollY, [0, 80], ['rgba(6,9,15,0)', 'rgba(6,9,15,0.88)']);
  const navBorder = useTransform(scrollY, [0, 80], ['rgba(240,246,252,0)', 'rgba(240,246,252,0.06)']);

  useEffect(() => {
    return scrollY.on('change', (v) => setScrolled(v > 40));
  }, [scrollY]);

  return (
    <>
      <motion.nav
        style={{ backgroundColor: navBg, borderBottomColor: navBorder }}
        className="fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-xl"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-cyan flex items-center justify-center shadow-[0_0_20px_rgba(0,212,255,0.4)] group-hover:shadow-[0_0_32px_rgba(0,212,255,0.6)] transition-shadow">
              <Cpu className="w-4 h-4 text-background" />
            </div>
            <span className="font-heading font-bold text-lg text-foreground tracking-tight">
              Ye<span className="text-cyan">fai</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="px-4 py-2 rounded-lg text-sm font-medium text-muted hover:text-foreground hover:bg-surface-2 transition-all"
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Actions */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg text-sm font-medium text-muted hover:text-foreground transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-cyan text-background hover:brightness-110 transition-all active:scale-95 shadow-[0_0_20px_rgba(0,212,255,0.25)]"
            >
              Request Demo
            </Link>
          </div>

          {/* Mobile burger */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-surface-2 transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </motion.nav>

      {/* Mobile menu */}
      <motion.div
        className="fixed inset-x-0 top-[65px] z-40 md:hidden"
        initial={false}
        animate={{ height: mobileOpen ? 'auto' : 0, opacity: mobileOpen ? 1 : 0 }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        style={{ overflow: 'hidden' }}
      >
        <div className="bg-background/95 backdrop-blur-xl border-b border-border px-6 py-4 flex flex-col gap-2">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="px-4 py-3 rounded-xl text-sm font-medium text-muted hover:text-foreground hover:bg-surface-2 transition-all"
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className="flex gap-3 pt-2">
            <Link href="/login" className="flex-1 py-3 rounded-xl text-sm font-medium text-center border border-border hover:bg-surface-2 transition-all">
              Sign In
            </Link>
            <Link href="/login" className="flex-1 py-3 rounded-xl text-sm font-semibold text-center bg-cyan text-background transition-all">
              Request Demo
            </Link>
          </div>
        </div>
      </motion.div>
    </>
  );
}
