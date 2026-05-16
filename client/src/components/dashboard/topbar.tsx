'use client';

import { usePathname } from 'next/navigation';
import { Bell, Search } from 'lucide-react';
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
  const { user } = useAuthStore();

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

        {/* Avatar */}
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center">
          <span className="text-white text-xs font-bold">
            {user?.name?.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2) ?? 'YF'}
          </span>
        </div>
      </div>
    </header>
  );
}
