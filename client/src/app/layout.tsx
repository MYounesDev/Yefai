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
  title: { default: 'Yefai — AI Predictive Maintenance Platform', template: '%s | Yefai' },
  description: 'Industry 4.0 predictive maintenance powered by multimodal AI. Real-time tool wear detection, failure forecasting, and automated spare parts procurement.',
  keywords: ['predictive maintenance', 'AI', 'tool wear detection', 'Industry 4.0', 'CNC', 'machine learning', 'computer vision', 'IoT'],
  openGraph: {
    title: 'Yefai — AI Predictive Maintenance Platform',
    description: 'Know before it breaks. Yefai fuses computer vision, acoustic sensors, and AI to detect tool wear in real time.',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: '#06090F',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${spaceGrotesk.variable} antialiased bg-background`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background text-foreground">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
