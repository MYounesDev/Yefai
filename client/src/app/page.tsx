'use client';

import { Navbar } from '@/components/landing/navbar';
import { HeroSection } from '@/components/landing/hero-section';
import { StatsSection } from '@/components/landing/stats-section';
import { FeaturesSection } from '@/components/landing/features-section';
import { HowItWorksSection } from '@/components/landing/how-it-works-section';
import { DashboardPreviewSection } from '@/components/landing/dashboard-preview-section';
import { PricingSection } from '@/components/landing/pricing-section';
import { CtaFooterSection } from '@/components/landing/cta-footer-section';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* Persistent background mesh */}
      <div className="bg-mesh" aria-hidden="true" />

      <Navbar />
      <main>
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <HowItWorksSection />
        <DashboardPreviewSection />
        <PricingSection />
      </main>
      <CtaFooterSection />
    </div>
  );
}
