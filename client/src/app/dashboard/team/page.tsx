'use client';

import { useMemo, useState } from 'react';
import { motion, type Variants } from 'framer-motion';
import { Users, UserPlus, Shield, Mail, MoreHorizontal, Search } from 'lucide-react';
import { mockOrgMembers } from '@/services/mock/auth';
import { RoleBadge, StatusDot } from '@/components/ui/index';
import { cn, formatRelativeTime } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.04 } } },
  item: { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } } },
};

const statusLabels: Record<string, string> = {
  active: 'Aktif',
  invited: 'Davet Edildi',
  disabled: 'Devre Dışı',
};

export default function TeamPage() {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search) return mockOrgMembers;
    return mockOrgMembers.filter((m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) || m.email.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  const counts = useMemo(() => ({
    total: mockOrgMembers.length,
    active: mockOrgMembers.filter((m) => m.status === 'active').length,
    invited: mockOrgMembers.filter((m) => m.status === 'invited').length,
  }), []);

  return (
    <div className="p-6 space-y-6">
      {/* Stats */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Toplam Üye', value: counts.total, icon: Users, color: 'bg-cyan/10 text-cyan' },
          { label: 'Aktif', value: counts.active, icon: Shield, color: 'bg-emerald/10 text-emerald' },
          { label: 'Davet Edildi', value: counts.invited, icon: Mail, color: 'bg-amber/10 text-amber' },
        ].map((s) => (
          <motion.div key={s.label} variants={stagger.item} className="bg-surface border border-border rounded-xl p-4 flex items-center gap-3">
            <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', s.color)}>
              <s.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] text-muted tracking-wide uppercase">{s.label}</p>
              <p className="text-xl font-heading font-bold text-foreground">{s.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Actions row */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Üye ara..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-border text-sm text-foreground placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
          />
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan to-violet text-white text-xs font-semibold shadow-lg shadow-cyan/15 hover:shadow-xl transition-all active:scale-95">
          <UserPlus className="w-4 h-4" />
          Üye Davet Et
        </button>
      </div>

      {/* Members Table */}
      <motion.div
        variants={stagger.container}
        initial="hidden"
        animate="show"
        className="bg-surface border border-border rounded-xl overflow-hidden"
      >
        {/* Header */}
        <div className="grid grid-cols-12 gap-4 px-5 py-3 border-b border-border text-[11px] text-muted font-medium tracking-wide uppercase">
          <div className="col-span-4">Üye</div>
          <div className="col-span-2">Rol</div>
          <div className="col-span-2">Durum</div>
          <div className="col-span-2">Son Aktivite</div>
          <div className="col-span-2">Katılım</div>
        </div>

        {filtered.map((member) => (
          <motion.div
            key={member.user_id}
            variants={stagger.item}
            className="grid grid-cols-12 gap-4 px-5 py-4 border-b border-border/50 last:border-0 items-center hover:bg-surface-2 transition-all group"
          >
            <div className="col-span-4 flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet/30 to-cyan/30 flex items-center justify-center text-xs font-bold text-foreground border border-border">
                {member.name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-foreground truncate">{member.name}</p>
                <p className="text-[10px] text-muted truncate">{member.email}</p>
              </div>
            </div>
            <div className="col-span-2">
              <RoleBadge role={member.role} />
            </div>
            <div className="col-span-2">
              <div className="flex items-center gap-1.5">
                <StatusDot status={member.status === 'active' ? 'safe' : member.status === 'invited' ? 'watch' : 'critical'} pulse={false} />
                <span className="text-xs text-muted">{statusLabels[member.status]}</span>
              </div>
            </div>
            <div className="col-span-2">
              <span className="text-[11px] text-muted">
                {member.last_active ? formatRelativeTime(member.last_active) : '—'}
              </span>
            </div>
            <div className="col-span-2 flex items-center justify-between">
              <span className="text-[11px] text-muted">{new Date(member.joined_at).toLocaleDateString('tr-TR')}</span>
              <button className="p-1.5 rounded-lg text-muted hover:text-foreground hover:bg-surface-3 transition-all opacity-0 group-hover:opacity-100">
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
