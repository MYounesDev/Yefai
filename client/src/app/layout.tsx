import type { Metadata, Viewport } from 'next';
import { IBM_Plex_Mono, Noto_Serif, Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-ibm-plex-mono',
  display: 'swap',
});

const notoSerif = Noto_Serif({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-noto-serif',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: { default: 'Yefai — Kestirimci Bakım Platformu', template: '%s | Yefai' },
  description:
    'Yapay zeka destekli kestirimci bakım. Gerçek zamanlı anomali tespiti, akıllı yedek parça yönetimi ve endüstriyel IoT izleme.',
  keywords: ['kestirimci bakım', 'yapay zeka', 'anomali tespiti', 'üretim', 'CNC', 'endüstriyel IoT'],
  openGraph: {
    title: 'Yefai — Kestirimci Bakım Platformu',
    description: 'Yapay zeka destekli kestirimci bakım platformu.',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: '#f6f3f1',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="tr"
      className={`${ibmPlexMono.variable} ${notoSerif.variable} ${inter.variable} antialiased bg-paper-canvas`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-paper-canvas text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
