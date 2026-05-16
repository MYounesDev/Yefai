'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, UserPlus, Mail, MoreHorizontal, Shield } from 'lucide-react';
import { RoleBadge } from '@/components/ui/badge';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { Role } from '@/types';

const MOCK_MEMBERS = [
  { user_id: 'u1', name: 'Ahmet Yılmaz', email: 'ahmet@yilmazmakina.com', role: 'manager' as Role, status: 'active', last_active: new Date(Date.now() - 300000).toISOString(), joined_at: '2025-01-10T00:00:00Z' },
  { user_id: 'u2', name: 'Fatma Demir', email: 'fatma@yilmazmakina.com', role: 'technician' as Role, status: 'active', last_active: new Date(Date.now() - 1800000).toISOString(), joined_at: '2025-02-01T00:00:00Z' },
  { user_id: 'u3', name: 'Mehmet Kaya', email: 'mehmet@yilmazmakina.com', role: 'operator' as Role, status: 'active', last_active: new Date(Date.now() - 7200000).toISOString(), joined_at: '2025-03-15T00:00:00Z' },
  { user_id: 'u4', name: 'Zeynep Çelik', email: 'zeynep@yilmazmakina.com', role: 'procurement' as Role, status: 'active', last_active: new Date(Date.now() - 86400000).toISOString(), joined_at: '2025-03-20T00:00:00Z' },
  { user_id: 'u5', name: 'Ali Şahin', email: 'ali@yilmazmakina.com', role: 'viewer' as Role, status: 'invited', last_active: undefined, joined_at: '2026-05-15T00:00:00Z' },
];

export default function TeamPage() {
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Role>('operator');

  const ROLES: Role[] = ['manager', 'technician', 'operator', 'procurement', 'viewer'];

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-muted" />
          <span className="text-sm text-muted">{MOCK_MEMBERS.length} members</span>
        </div>
        <button
          onClick={() => setShowInvite(true)}
          className="flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 transition-all"
        >
          <UserPlus className="w-3.5 h-3.5" />
          Invite Member
        </button>
      </div>

      {/* Invite form */}
      {showInvite && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-surface border border-cyan-500/20 rounded-xl p-5 space-y-3"
        >
          <h3 className="text-sm font-semibold font-heading text-foreground">Invite a team member</h3>
          <div className="flex gap-3 flex-wrap">
            <div className="flex-1 relative min-w-48">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted" />
              <input
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="colleague@company.com"
                className="w-full pl-9 pr-3 py-2 text-sm bg-surface-2 border border-border rounded-lg text-foreground placeholder:text-muted focus:outline-none focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20 transition-all"
              />
            </div>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as Role)}
              className="px-3 py-2 text-sm bg-surface-2 border border-border rounded-lg text-foreground focus:outline-none focus:border-cyan-500/40 transition-all"
            >
              {ROLES.map((r) => <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>)}
            </select>
            <button
              onClick={() => setShowInvite(false)}
              className="px-4 py-2 rounded-lg bg-cyan-500 text-background text-sm font-medium hover:bg-cyan-400 transition-all"
            >
              Send Invite
            </button>
          </div>
        </motion.div>
      )}

      {/* Members table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="divide-y divide-border">
          {MOCK_MEMBERS.map((member, i) => (
            <motion.div
              key={member.user_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.04 }}
              className="flex items-center gap-4 px-5 py-4 hover:bg-surface-2 transition-colors"
            >
              {/* Avatar */}
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center shrink-0">
                <span className="text-white text-xs font-bold">
                  {member.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)}
                </span>
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-foreground">{member.name}</span>
                  {member.status === 'invited' && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      Invited
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted">{member.email}</p>
              </div>

              <RoleBadge role={member.role} />

              <div className="text-right shrink-0">
                <p className="text-xs text-muted">
                  {member.last_active ? `Active ${formatRelativeTime(member.last_active)}` : 'Not yet joined'}
                </p>
              </div>

              <button className="p-1.5 rounded-lg text-muted hover:text-foreground hover:bg-surface-3 transition-colors">
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Role legend */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-muted" />
          <h3 className="text-xs font-semibold text-muted">Role Permissions</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[
            { role: 'manager', desc: 'Full access + member management' },
            { role: 'technician', desc: 'Anomalies, predictions, spare parts' },
            { role: 'operator', desc: 'Dashboard, anomalies, notifications' },
            { role: 'procurement', desc: 'Spare parts + PO approval' },
            { role: 'viewer', desc: 'Read-only dashboard access' },
          ].map((r) => (
            <div key={r.role} className="flex items-start gap-2 p-2.5 rounded-lg bg-surface-2">
              <RoleBadge role={r.role} />
              <p className="text-[11px] text-muted">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
