import type { Metadata, Viewport } from 'next';
import { Inter, Space_Grotesk } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

export const metadata: Metadata = {
  title: { default: 'Yefai — Predictive Maintenance Platform', template: '%s | Yefai' },
  description: 'AI-powered predictive maintenance for manufacturing. Zero-shot anomaly detection, real-time alerts, and smart spare parts management.',
  keywords: ['predictive maintenance', 'AI', 'anomaly detection', 'manufacturing', 'CNC'],
  openGraph: {
    title: 'Yefai — Predictive Maintenance Platform',
    description: 'AI-powered predictive maintenance for manufacturing.',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: '#0A0E1A',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${spaceGrotesk.variable} bg-background antialiased`}
    >
      <body className="min-h-screen text-foreground">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
