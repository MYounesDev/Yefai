'use client';

import { useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Bell, Search, LogOut, Sun, Moon, Menu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useAuthStore } from '@/store/authStore';
import { useUIStore } from '@/store/uiStore';
import { cn } from '@/lib/utils';
import Link from 'next/link';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Kontrol Paneli',
  '/dashboard/anomalies': 'Anomali Tespiti',
  '/dashboard/predictions': 'Tahminler',
  '/dashboard/spare-parts': 'Yedek Parçalar',
  '/dashboard/chatbot': 'AI Asistan',
  '/dashboard/notifications': 'Bildirimler',
  '/dashboard/team': 'Ekip Yönetimi',
  '/dashboard/settings': 'Ayarlar',
};

const PAGE_DESCRIPTIONS: Record<string, string> = {
  '/dashboard': 'Fabrika durumu ve anomali özeti',
  '/dashboard/anomalies': 'Gerçek zamanlı anomali izleme',
  '/dashboard/predictions': 'Makine aşınma tahminleri',
  '/dashboard/spare-parts': 'Stok ve kriz yönetimi',
  '/dashboard/chatbot': 'RAG destekli yapay zeka',
  '/dashboard/notifications': 'Uyarı ve bildirim merkezi',
  '/dashboard/team': 'Üye ve rol yönetimi',
  '/dashboard/settings': 'Platform ayarları',
};

export function TopBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { notificationCount, toggleSidebar } = useUIStore();
  const { theme, setTheme } = useTheme();
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const initials = (user?.name || '')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'YF';

  const title = Object.entries(PAGE_TITLES).find(([key]) =>
    pathname === key || pathname.startsWith(key + '/')
  )?.[1] ?? 'Yefai';

  const description = Object.entries(PAGE_DESCRIPTIONS).find(([key]) =>
    pathname === key || pathname.startsWith(key + '/')
  )?.[1];

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-border bg-surface/80 backdrop-blur-xl shrink-0 z-20">
      {/* Left: Mobile menu + Page title */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 rounded-lg text-muted hover:text-foreground hover:bg-surface-2 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-sm font-bold text-foreground font-heading tracking-tight">{title}</h1>
          {description && (
            <p className="text-[11px] text-muted mt-0.5 hidden sm:block">{description}</p>
          )}
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <button
          className="hidden md:flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-surface-2 border border-border text-muted text-xs hover:border-border-strong hover:text-foreground transition-all group"
        >
          <Search className="w-3.5 h-3.5 group-hover:text-cyan transition-colors" />
          <span>Ara...</span>
          <kbd className="ml-3 px-1.5 py-0.5 rounded-md bg-surface-3 text-[10px] font-mono text-muted border border-border">⌘K</kbd>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2.5 rounded-xl text-muted hover:text-foreground hover:bg-surface-2 transition-all"
          aria-label="Tema değiştir"
        >
          <AnimatePresence mode="wait">
            {theme === 'dark' ? (
              <motion.div key="sun" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
                <Sun className="w-4 h-4" />
              </motion.div>
            ) : (
              <motion.div key="moon" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
                <Moon className="w-4 h-4" />
              </motion.div>
            )}
          </AnimatePresence>
        </button>

        {/* Notifications */}
        <Link
          href="/dashboard/notifications"
          className={cn(
            'relative p-2.5 rounded-xl text-muted hover:text-foreground hover:bg-surface-2 transition-all',
            pathname.startsWith('/dashboard/notifications') && 'text-cyan bg-cyan/8'
          )}
        >
          <Bell className="w-4 h-4" />
          {notificationCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-rose text-[9px] font-bold text-white flex items-center justify-center animate-pulse">
              {notificationCount}
            </span>
          )}
        </Link>

        {/* Divider */}
        <div className="w-px h-8 bg-border mx-1 hidden sm:block" />

        {/* User Profile */}
        <div className="flex items-center gap-2.5 relative">
          <button
            onClick={() => setProfileDropdownOpen((p) => !p)}
            className="relative shrink-0 transition-transform active:scale-95 group"
            title="Profil Menüsü"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center ring-2 ring-transparent group-hover:ring-cyan/20 transition-all">
              <span className="text-white text-xs font-bold">{initials}</span>
            </div>
          </button>

          <div className="hidden md:block flex-1 min-w-0 text-left">
            <p className="text-sm font-semibold text-foreground truncate max-w-[130px]">{user?.name}</p>
            <p className="text-[10px] text-muted truncate max-w-[130px]">{user?.email}</p>
          </div>

          {/* Profile Dropdown */}
          <AnimatePresence>
            {profileDropdownOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setProfileDropdownOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -6, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -6, scale: 0.97 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-12 z-50 w-52 rounded-xl border border-border bg-surface overflow-hidden shadow-elevated"
                >
                  <div className="md:hidden px-4 py-3 border-b border-border">
                    <p className="text-sm font-semibold text-foreground truncate">{user?.name}</p>
                    <p className="text-[10px] text-muted truncate mt-0.5">{user?.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-3 text-sm text-rose hover:bg-rose/8 transition-colors text-left font-medium"
                  >
                    <LogOut className="w-4 h-4 shrink-0" />
                    Çıkış Yap
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
