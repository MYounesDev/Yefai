import { LandingNavbar } from '@/components/landing/navbar';
import { HeroSection } from '@/components/landing/hero-section';
import { FeaturesSection } from '@/components/landing/features-section';
import { PipelineSection } from '@/components/landing/pipeline-section';
import { FaqSection } from '@/components/landing/faq-section';
import { CtaFooter } from '@/components/landing/cta-footer';

export default function LandingPage() {
  return (
    <main className="min-h-screen" style={{ background: 'var(--color-paper-canvas)' }}>
      <LandingNavbar />
      <HeroSection />
      <FeaturesSection />
      <PipelineSection />
      <FaqSection />
      <CtaFooter />
    </main>
  );
}
