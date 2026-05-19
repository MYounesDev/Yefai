'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, AlertTriangle, TrendingUp, Package, MessageSquare, Bell,
  Users, Settings, ChevronLeft, ChevronRight, ChevronDown, Check, Cpu,
} from 'lucide-react';

import { useOrgStore } from '@/store/orgStore';
import { useUIStore } from '@/store/uiStore';
import { getNavItems } from '@/lib/permissions';
import { RoleBadge } from '@/components/ui/index';
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
      animate={{ width: sidebarCollapsed ? 68 : 260 }}
      transition={{ type: 'spring', stiffness: 320, damping: 30 }}
      className="relative flex flex-col h-full bg-surface border-r border-border overflow-hidden shrink-0 z-30"
    >
      {/* ── Logo ── */}
      <div className="flex items-center h-16 px-4 border-b border-border shrink-0">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center shrink-0 shadow-lg shadow-cyan/20">
            <Cpu className="w-4 h-4 text-white" />
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -12 }}
                className="flex flex-col"
              >
                <span className="font-heading font-bold text-[15px] text-gradient tracking-tight">
                  Yefai
                </span>
                <span className="text-[9px] text-muted tracking-widest uppercase">
                  Kestirimci Bakım
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </Link>
      </div>

      {/* ── Org Switcher ── */}
      <div className="px-3 py-3 border-b border-border">
        {!sidebarCollapsed && currentOrg && (
          <div className="relative">
            <button
              onClick={() => organizations.length > 1 && setOrgDropdownOpen((p) => !p)}
              className={cn(
                'w-full flex items-center gap-2.5 p-2 rounded-xl hover:bg-surface-2 transition-all text-left border border-transparent',
                orgDropdownOpen && 'bg-surface-2 border-border',
                organizations.length > 1 && 'cursor-pointer'
              )}
            >
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet to-cyan flex items-center justify-center shrink-0">
                <span className="text-white font-bold text-[10px]">{currentOrg.org_name[0]}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-foreground truncate">{currentOrg.org_name}</p>
                <RoleBadge role={currentOrg.role} />
              </div>
              {organizations.length > 1 && (
                <ChevronDown className={cn('w-3.5 h-3.5 text-muted transition-transform duration-200', orgDropdownOpen && 'rotate-180')} />
              )}
            </button>

            <AnimatePresence>
              {orgDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -6, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -6, scale: 0.97 }}
                  transition={{ duration: 0.15 }}
                  className="absolute left-0 right-0 top-[110%] z-40 rounded-xl border border-border bg-surface overflow-hidden shadow-elevated"
                >
                  {organizations.map((org) => (
                    <button
                      key={org.org_id}
                      onClick={() => { switchOrg(org.org_id); setOrgDropdownOpen(false); }}
                      className="w-full flex items-center gap-2.5 px-3 py-2.5 text-xs hover:bg-surface-2 transition-colors text-left"
                    >
                      <div className="w-5 h-5 rounded bg-violet/15 flex items-center justify-center shrink-0">
                        <span className="text-violet font-bold text-[10px]">{org.org_name[0]}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-foreground truncate font-medium">{org.org_name}</p>
                      </div>
                      <RoleBadge role={org.role} />
                      {org.org_id === activeOrgId && <Check className="w-3 h-3 text-cyan" />}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* ── Navigation ── */}
      <nav className="flex-1 overflow-y-auto py-4 px-2.5 space-y-1">
        {navItems.map((item) => {
          const Icon = iconMap[item.icon] || LayoutDashboard;
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href + '/'));
          const isExactDashboard = item.href === '/dashboard' && pathname === '/dashboard';
          const active = isActive || isExactDashboard;

          return (
            <Link
              key={item.href}
              href={item.href}
              title={sidebarCollapsed ? item.label : undefined}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] transition-all duration-200 group relative',
                active
                  ? 'bg-cyan/8 text-cyan font-semibold'
                  : 'text-muted hover:text-foreground hover:bg-surface-2'
              )}
            >
              {active && (
                <motion.div
                  layoutId="nav-active-indicator"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-cyan rounded-r-full"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              {/* @ts-expect-error - Icon is ElementType and accepts className */}
              <Icon className={cn(
                'w-[18px] h-[18px] shrink-0 transition-colors',
                active ? 'text-cyan' : 'text-muted group-hover:text-foreground'
              )} />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="tracking-tight"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>

      {/* ── Version tag ── */}
      <AnimatePresence>
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="px-4 py-3 border-t border-border"
          >
            <p className="text-[10px] text-muted/60 tracking-wide">
              Yefai Platform v2.0
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Collapse Toggle ── */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-surface border border-border flex items-center justify-center text-muted hover:text-foreground hover:border-border-strong transition-all z-10 shadow-card"
        aria-label={sidebarCollapsed ? 'Menüyü genişlet' : 'Menüyü daralt'}
      >
        {sidebarCollapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>
    </motion.aside>
  );
}
