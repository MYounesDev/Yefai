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
  title: { default: 'Yefai — Kestirimci Bakım Platformu', template: '%s | Yefai' },
  description: 'Yapay zeka destekli kestirimci bakım. Gerçek zamanlı anomali tespiti, akıllı yedek parça yönetimi ve endüstriyel IoT izleme.',
  keywords: ['kestirimci bakım', 'yapay zeka', 'anomali tespiti', 'üretim', 'CNC', 'endüstriyel IoT'],
  openGraph: {
    title: 'Yefai — Kestirimci Bakım Platformu',
    description: 'Yapay zeka destekli kestirimci bakım platformu.',
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
      lang="tr"
      className={`${inter.variable} ${spaceGrotesk.variable} antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background text-foreground">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
