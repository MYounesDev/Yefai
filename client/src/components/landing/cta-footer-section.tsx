'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Cpu, Globe, Mail, Twitter, Linkedin } from 'lucide-react';

const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.1 } } };
const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.7, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

const footerLinks = [
  {
    heading: 'Platform',
    links: ['NovaVision AI', 'Predictive Forecasting', 'Crisis Score', 'Procurement Automation', 'Analytics Chatbot'],
  },
  {
    heading: 'Company',
    links: ['About', 'Blog', 'Careers', 'Press', 'Contact'],
  },
  {
    heading: 'Resources',
    links: ['Documentation', 'API Reference', 'Changelog', 'Status', 'Security'],
  },
  {
    heading: 'Legal',
    links: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'GDPR'],
  },
];

export function CtaFooterSection() {
  return (
    <>
      {/* ── CTA Section ── */}
      <section className="relative z-10 py-28 px-6 overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

        {/* Large background glow */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan/4 to-transparent pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-cyan/8 blur-[140px] rounded-full pointer-events-none" />

        <div className="max-w-3xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="text-center"
          >
            {/* Decorative border element */}
            <motion.div variants={fadeUp} custom={0} className="inline-flex mb-6">
              <div className="relative p-px rounded-2xl bg-gradient-to-r from-cyan/40 via-violet/20 to-cyan/40">
                <div className="px-5 py-2.5 rounded-[calc(1rem-1px)] bg-background text-xs font-mono text-cyan tracking-widest uppercase">
                  Ready to transform your factory?
                </div>
              </div>
            </motion.div>

            <motion.h2
              variants={fadeUp}
              custom={1}
              className="text-4xl sm:text-6xl font-heading font-bold mb-6 text-balance leading-tight"
            >
              Stop Reacting.
              <br />
              <span className="text-gradient">Start Predicting.</span>
            </motion.h2>

            <motion.p
              variants={fadeUp}
              custom={2}
              className="text-muted text-lg leading-relaxed mb-10 max-w-xl mx-auto"
            >
              Join manufacturers who reduced unplanned downtime by 40% in their first quarter with Yefai.
              Request a live demo tailored to your production environment.
            </motion.p>

            <motion.div
              variants={fadeUp}
              custom={3}
              className="flex flex-wrap gap-4 justify-center"
            >
              <Link
                href="/login"
                className="group inline-flex items-center gap-2.5 px-8 py-4 rounded-xl text-base font-semibold bg-cyan text-background hover:brightness-110 transition-all active:scale-95 shadow-[0_0_40px_rgba(0,212,255,0.35)]"
              >
                Request Live Demo
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl text-base font-medium border border-border-strong hover:border-cyan/30 hover:bg-surface-2 text-foreground transition-all active:scale-95"
              >
                Explore Platform
              </Link>
            </motion.div>

            {/* Trust signals */}
            <motion.div
              variants={fadeUp}
              custom={4}
              className="flex flex-wrap gap-6 justify-center mt-10 text-xs text-muted/60 font-mono"
            >
              {['No credit card required', 'SOC 2 Type II', 'GDPR compliant', '30-day pilot free'].map((t) => (
                <span key={t} className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-cyan/50" />
                  {t}
                </span>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-border">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-strong to-transparent" />

        <div className="max-w-6xl mx-auto px-6 pt-16 pb-10">
          {/* Top row: Logo + links grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-10 mb-14">
            {/* Brand column */}
            <div className="col-span-2">
              <Link href="/" className="flex items-center gap-2.5 mb-5 group w-fit">
                <div className="w-8 h-8 rounded-xl bg-cyan flex items-center justify-center shadow-[0_0_16px_rgba(0,212,255,0.3)] group-hover:shadow-[0_0_24px_rgba(0,212,255,0.5)] transition-shadow">
                  <Cpu className="w-4 h-4 text-background" />
                </div>
                <span className="font-heading font-bold text-base text-foreground tracking-tight">
                  Ye<span className="text-cyan">fai</span>
                </span>
              </Link>
              <p className="text-sm text-muted leading-relaxed max-w-[220px] mb-6">
                Industry 4.0 predictive maintenance platform powered by multimodal AI.
              </p>
              {/* Social icons */}
              <div className="flex items-center gap-3">
                {[Twitter, Linkedin, Mail].map((Icon, i) => (
                  <a
                    key={i}
                    href="#"
                    className="w-8 h-8 rounded-lg border border-border hover:border-cyan/30 hover:bg-surface-2 flex items-center justify-center transition-all text-muted hover:text-foreground"
                    aria-label="Social link"
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </a>
                ))}
              </div>
            </div>

            {/* Link columns */}
            {footerLinks.map((col) => (
              <div key={col.heading} className="col-span-1">
                <p className="text-[11px] font-mono text-muted/50 tracking-[0.15em] uppercase mb-4">{col.heading}</p>
                <ul className="space-y-2.5">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a
                        href="#"
                        className="text-sm text-muted hover:text-foreground transition-colors"
                      >
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom row */}
          <div className="border-t border-border pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-muted/50 font-mono">
              <Globe className="w-3.5 h-3.5" />
              <span>© 2026 Yefai Technologies. All rights reserved.</span>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-muted/40">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse" />
              All systems operational
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
