'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard, AlertTriangle, TrendingUp, Package, MessageSquare, Bell,
  Users, Settings, ChevronLeft, ChevronRight, LogOut, ChevronDown, Check,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore'; // may be unused but keeping import just in case

import { useOrgStore } from '@/store/orgStore';
import { useUIStore } from '@/store/uiStore';
import { getNavItems } from '@/lib/permissions';
import { RoleBadge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

const iconMap: Record<string, React.ElementType> = {
  LayoutDashboard, AlertTriangle, TrendingUp, Package, MessageSquare, Bell, Users, Settings,
};

export function Sidebar() {
  const pathname = usePathname();
  const { activeOrgId, activeRole, organizations, switchOrg } = useOrgStore();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const [orgDropdownOpen, setOrgDropdownOpen] = useState(false);

  const navItems = getNavItems(activeRole);
  const currentOrg = organizations.find((o) => o.org_id === activeOrgId);

  return (
    <motion.aside
      animate={{ width: sidebarCollapsed ? 64 : 240 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="relative flex flex-col h-full bg-surface border-r border-border overflow-hidden shrink-0"
    >
      {/* Logo */}
      <div className="flex items-center h-14 px-4 border-b border-border shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center shrink-0">
            <span className="text-white font-bold text-xs font-heading">Y</span>
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="font-heading font-bold text-base text-gradient"
              >
                Yefai
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </div>

      {/* Org Switcher */}
      <div className="px-3 py-3 border-b border-border">

        {/* Org Switcher */}
        {!sidebarCollapsed && currentOrg && (
          <div className="relative">
            <button
              onClick={() => organizations.length > 1 && setOrgDropdownOpen((p) => !p)}
              className={cn(
                'w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-surface-2 transition-colors text-left border border-border/50',
                organizations.length > 1 && 'cursor-pointer'
              )}
            >
              <div className="w-6 h-6 rounded bg-gradient-to-br from-violet-500 to-cyan-600 flex items-center justify-center shrink-0">
                <span className="text-white font-bold text-[10px]">{currentOrg.org_name[0]}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground truncate">{currentOrg.org_name}</p>
                <RoleBadge role={currentOrg.role} />
              </div>
              {organizations.length > 1 && (
                <ChevronDown className={cn('w-3.5 h-3.5 text-muted transition-transform', orgDropdownOpen && 'rotate-180')} />
              )}
            </button>

            <AnimatePresence>
              {orgDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="absolute left-0 right-0 top-[110%] z-40 rounded-lg border border-border bg-surface-2 overflow-hidden shadow-lg"
                >
                  {organizations.map((org) => (
                    <button
                      key={org.org_id}
                      onClick={() => { switchOrg(org.org_id); setOrgDropdownOpen(false); }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-surface transition-colors text-left"
                    >
                      <div className="w-5 h-5 rounded bg-violet-500/20 flex items-center justify-center shrink-0">
                        <span className="text-violet-400 font-bold text-xs">{org.org_name[0]}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-foreground truncate">{org.org_name}</p>
                      </div>
                      <RoleBadge role={org.role} />
                      {org.org_id === activeOrgId && <Check className="w-3 h-3 text-cyan-400" />}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map((item) => {
          const Icon = iconMap[item.icon] || LayoutDashboard;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

          return (
            <Link
              key={item.href}
              href={item.href}
              title={sidebarCollapsed ? item.label : undefined}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 group relative',
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-muted hover:text-foreground hover:bg-surface-2'
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="nav-active"
                  className="absolute left-0 top-0 bottom-0 w-0.5 bg-cyan-400 rounded-full"
                />
              )}
              <Icon className={cn('w-4 h-4 shrink-0', isActive ? 'text-cyan-400' : 'text-muted group-hover:text-foreground')} />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="font-medium"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>



      {/* Collapse Toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-surface border border-border flex items-center justify-center text-muted hover:text-foreground transition-colors z-10"
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {sidebarCollapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>
    </motion.aside>
  );
}


