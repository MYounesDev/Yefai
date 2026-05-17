'use client';

import { useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Bell, Search, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';
import Link from 'next/link';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/dashboard/anomalies': 'Anomalies',
  '/dashboard/predictions': 'Predictions',
  '/dashboard/spare-parts': 'Spare Parts',
  '/dashboard/chatbot': 'AI Chatbot',
  '/dashboard/notifications': 'Notifications',
  '/dashboard/team': 'Team',
  '/dashboard/settings': 'Settings',
};

export function TopBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
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

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-border bg-surface shrink-0">
      <div>
        <h1 className="text-sm font-semibold text-foreground font-heading">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Search hint */}
        <button className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-2 border border-border text-muted text-xs hover:border-border-strong transition-colors">
          <Search className="w-3.5 h-3.5" />
          <span>Search...</span>
          <kbd className="ml-2 px-1 rounded bg-surface-3 text-[10px] font-mono text-muted">⌘K</kbd>
        </button>

        {/* Notification bell */}
        <Link
          href="/dashboard/notifications"
          className={cn(
            'relative p-2 rounded-lg text-muted hover:text-foreground hover:bg-surface-2 transition-colors',
            pathname.startsWith('/dashboard/notifications') && 'text-cyan-400 bg-cyan-500/10'
          )}
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-rose-500" />
        </Link>

        {/* User Profile */}
        <div className="flex items-center gap-2 relative">
          <button
            onClick={() => setProfileDropdownOpen((p) => !p)}
            className="relative shrink-0 transition-transform active:scale-95"
            title="Profile Menu"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center">
              <span className="text-white text-xs font-bold">{initials}</span>
            </div>
          </button>
          
          <div className="hidden md:block flex-1 min-w-0 text-left">
            <p className="text-sm font-medium text-foreground truncate max-w-[120px]">{user?.name}</p>
            <p className="text-[10px] text-muted truncate max-w-[120px]">{user?.email}</p>
          </div>

          {/* Profile Dropdown Menu */}
          <AnimatePresence>
            {profileDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                className="absolute right-0 top-10 z-50 mt-1 w-48 rounded-lg border border-border bg-surface-2 overflow-hidden shadow-xl"
              >
                <div className="md:hidden px-3 py-2 border-b border-border">
                  <p className="text-sm font-medium text-foreground truncate">{user?.name}</p>
                  <p className="text-[10px] text-muted truncate">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-rose-400 hover:bg-rose-500/10 transition-colors text-left font-medium"
                >
                  <LogOut className="w-4 h-4 shrink-0" />
                  Logout
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
